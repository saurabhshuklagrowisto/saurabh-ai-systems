#!/bin/bash
# approval-gate.sh: nothing leaves without the owner typing a code
#
# WHY THIS EXISTS
# the agent sent a WhatsApp message to a number from a fabricated test opportunity
# without the owner seeing it first. The rule saying "wait for approval" lived in
# her prompt, and a prompt is a request, not a lock.
#
# This moves the gate out of her reach entirely. She can queue a draft. She
# cannot send it. Only a code typed by the owner, from his own number, releases a
# specific message. She never sees the code before he sends it and cannot
# generate one.
#
# FLOW
#   1. She writes a draft to outbox/pending/
#   2. This script previews it to the owner with a random 4 character code
#      and moves it to outbox/awaiting/<code>.txt
#   3. the owner replies to the agent:  SEND A7K2
#   4. This script finds that exact code in HIS inbound messages and only then
#      sends that one message
#   5. Codes expire after 30 minutes. Unapproved drafts are discarded.
set -uo pipefail

# One gate at a time. Cron fires this every minute and a send takes a few
# seconds; two overlapping runs once sent the same application twice.
exec 9>/tmp/approval-gate.lock
flock -n 9 || exit 0

WS="/root/.openclaw/workspace/outbox"
PENDING="$WS/pending"
AWAITING="$WS/awaiting"
SENDING="$WS/sending"
SENT="$WS/sent"
FAILED="$WS/failed"
RUN_LOG="/root/scan.log"
OWNER="+91XXXXXXXXXX"
OWNER_DIGITS="91XXXXXXXXXX"
LOG_DIR="/tmp/openclaw"
EXPIRY_MIN=30

mkdir -p "$PENDING" "$AWAITING" "$SENDING" "$SENT" "$FAILED"
shopt -s nullglob

log() { echo "$(date -Is) [gate] $*" >> "$RUN_LOG"; }

# ---------------------------------------------------------------------------
# 1. New drafts: preview to the owner, assign a code, do NOT send
# ---------------------------------------------------------------------------
for f in "$PENDING"/*.txt; do
    [ -f "$f" ] || continue
    base=$(basename "$f")

    RAW=$(grep -m1 -iE '^TO:' "$f" | sed 's/^[Tt][Oo]: *//' | tr -d '[:space:]')
    CONTEXT=$(grep -m1 -iE '^CONTEXT:' "$f" | sed 's/^[Cc][Oo][Nn][Tt][Ee][Xx][Tt]: *//')
    SUBJECT=$(grep -m1 -iE '^SUBJECT:' "$f" | sed 's/^[Ss][Uu][Bb][Jj][Ee][Cc][Tt]: *//')
    BODY=$(awk 'BEGIN{b=0} /^[[:space:]]*$/{if(!b){b=1;next}} b{print}' "$f")

    # An @ means email. Anything else is a phone number.
    case "$RAW" in
        *@*) KIND=email; TO="$RAW"; SHOWN="$RAW" ;;
        *)   KIND=whatsapp; TO=$(printf '%s' "$RAW" | tr -cd '0-9'); SHOWN="+91$TO" ;;
    esac

    if [ -z "$TO" ] || [ -z "$BODY" ] || { [ "$KIND" = email ] && [ -z "$SUBJECT" ]; }; then
        mv "$f" "$FAILED/$base"
        log "malformed draft $base, discarded"
        openclaw message send --target "$OWNER" \
            --message "A draft was missing a recipient or body, so it was discarded. Nothing was sent." >/dev/null 2>&1
        continue
    fi

    # One request, one approval. She sometimes writes the same email into two
    # files; approving both would send a opportunity director two copies.
    FP=$(printf '%s|%s' "$TO" "$BODY" | tr -d '[:space:]' | md5sum | cut -c1-16)
    DUP=0
    for existing in "$AWAITING"/*.txt; do
        [ -f "$existing" ] || continue
        ETO=$(grep -m1 -iE '^TO:' "$existing" | sed 's/^[Tt][Oo]: *//' | tr -d '[:space:]')
        EBODY=$(awk 'BEGIN{b=0} /^[[:space:]]*$/{if(!b){b=1;next}} b{print}' "$existing")
        EFP=$(printf '%s|%s' "$ETO" "$EBODY" | tr -d '[:space:]' | md5sum | cut -c1-16)
        if [ "$FP" = "$EFP" ]; then DUP=1; break; fi
    done
    if [ "$DUP" -eq 1 ]; then
        mv "$f" "$FAILED/duplicate-$base"
        log "duplicate draft $base discarded, one is already awaiting approval"
        continue
    fi

    # Run every sender validator now, with DRY_RUN so nothing leaves. A draft
    # that cannot be sent must never become an approval request: he would
    # approve it and then be told it failed.
    printf '%s\n' "$BODY" > /tmp/gate-precheck.txt
    if [ "$KIND" = email ]; then
        PRE=$(GATE_RELEASE=1 DRY_RUN=1 FORCE=1 /root/send-opportunity-email.sh \
              "$TO" "$SUBJECT" /tmp/gate-precheck.txt 2>&1)
    else
        PRE=$(GATE_RELEASE=1 DRY_RUN=1 FORCE=1 /root/send-whatsapp.sh \
              "$TO" /tmp/gate-precheck.txt "$CONTEXT" 2>&1)
    fi
    PRE_RC=$?
    rm -f /tmp/gate-precheck.txt

    if [ "$PRE_RC" -ne 0 ]; then
        mv "$f" "$FAILED/rejected-$base"
        REASON=$(printf '%s' "$PRE" | grep -m1 'REFUSED' | cut -c1-140)
        log "draft $base rejected before approval: $REASON"
        openclaw message send --target "$OWNER" --message "A draft was not good enough to send, so I am not asking you to approve it.

To: $SHOWN
$REASON

the agent can write a corrected one." >/dev/null 2>&1
        continue
    fi

    # A word, not a character code. See the note at the top of this file.
    # Avoid a word that already appears in today's messages at all, so a code
    # cannot collide with anything the owner has typed since midnight.
    LOGTODAY="$LOG_DIR/openclaw-$(date +%Y-%m-%d).log"
    CODE=$(shuf -n1 /root/approval-words.txt)
    tries=0
    while [ -e "$AWAITING/$CODE.txt" ] || \
          { [ -f "$LOGTODAY" ] && grep -qi "SEND $CODE" "$LOGTODAY"; }; do
        CODE=$(shuf -n1 /root/approval-words.txt)
        tries=$((tries + 1))
        [ "$tries" -gt 40 ] && break
    done
    mv "$f" "$AWAITING/$CODE.txt"
    log "awaiting approval $CODE -> $SHOWN [$KIND] ($CONTEXT)"

    if [ "$KIND" = email ]; then
        HEAD="To: $SHOWN (email, cc shivsaurabhshukla@gmail.com)
Subject: $SUBJECT"
    else
        HEAD="To: $SHOWN (whatsapp)"
    fi

    # A repeat approach is a judgement call, so it belongs in the preview where
    # the owner can weigh it, not in a refusal after he has already said yes.
    APPLOG="/root/.openclaw/workspace/reference/APPLICATIONS.md"
    PRIOR=""
    if [ -r "$APPLOG" ] && grep -qF "$TO" "$APPLOG" 2>/dev/null; then
        WHEN=$(grep -F "$TO" "$APPLOG" | tail -1 | awk -F'|' '{print $2}' | tr -d ' ')
        PRIOR="ALREADY CONTACTED on $WHEN. Approving sends anyway.
"
    fi

    openclaw message send --target "$OWNER" --message "APPROVAL NEEDED

$HEAD
$CONTEXT
$PRIOR

$BODY

Reply  SEND $CODE  to send this. Reply nothing to discard. Expires in ${EXPIRY_MIN} minutes." >/dev/null 2>&1
done

# ---------------------------------------------------------------------------
# 2. Look for approval codes in the owner's own inbound messages
# ---------------------------------------------------------------------------
LOGFILE="$LOG_DIR/openclaw-$(date +%Y-%m-%d).log"

for f in "$AWAITING"/*.txt; do
    [ -f "$f" ] || continue
    CODE=$(basename "$f" .txt)

    # expire old drafts rather than leaving them approvable forever
    AGE_MIN=$(( ( $(date +%s) - $(stat -c %Y "$f") ) / 60 ))
    if [ "$AGE_MIN" -gt "$EXPIRY_MIN" ]; then
        mv "$f" "$FAILED/expired-$CODE.txt"
        log "expired $CODE after ${AGE_MIN}m"
        continue
    fi

    [ -f "$LOGFILE" ] || continue

    # The approval must come FROM the owner's number. Anything containing the code
    # that did not arrive from him is ignored.
    APPROVED=$(grep '"body"' "$LOGFILE" 2>/dev/null | CODE="$CODE" WHO="$OWNER_DIGITS" MINTS="$(stat -c %Y "$f")" python3 -c "
import sys, json, os
code = os.environ['CODE']; who = os.environ['WHO']
# The approval has to be newer than the draft. A recycled word once matched a
# message from earlier the same day and released an email nobody had seen.
mints = int(os.environ.get('MINTS', '0'))
ok = 0
for line in sys.stdin:
    try:
        m = json.loads(line).get('1', {})
        frm = str(m.get('from', ''))
        body = str(m.get('body', '')).upper()
        ts = m.get('timestamp')
        if ts:
            ts = int(ts)
            ts = ts // 1000 if ts > 1e11 else ts
        else:
            continue
        if ts < mints:
            continue
        words = body.replace(',', ' ').replace('.', ' ').split()
        if who in frm and 'SEND' in words and code in words:
            ok = 1
    except Exception:
        pass
print(ok)
" 2>/dev/null)

    if [ "${APPROVED:-0}" != "1" ]; then
        continue
    fi

    # Claim the draft before doing anything slow. Once it is out of awaiting/
    # no other run can find it, so it cannot be released twice. The lock covers
    # cron; this covers everything else, including a manual run.
    CLAIM="$SENDING/$CODE.txt"
    mv "$f" "$CLAIM" 2>/dev/null || continue
    f="$CLAIM"

    RAW=$(grep -m1 -iE '^TO:' "$f" | sed 's/^[Tt][Oo]: *//' | tr -d '[:space:]')
    CONTEXT=$(grep -m1 -iE '^CONTEXT:' "$f" | sed 's/^[Cc][Oo][Nn][Tt][Ee][Xx][Tt]: *//')
    SUBJECT=$(grep -m1 -iE '^SUBJECT:' "$f" | sed 's/^[Ss][Uu][Bb][Jj][Ee][Cc][Tt]: *//')
    awk 'BEGIN{b=0} /^[[:space:]]*$/{if(!b){b=1;next}} b{print}' "$f" > /tmp/gate-body.txt

    case "$RAW" in
        *@*) TO="$RAW"; SHOWN="$RAW"
             SENDER=(GATE_RELEASE=1 FORCE=1 /root/send-opportunity-email.sh "$TO" "$SUBJECT" /tmp/gate-body.txt) ;;
        *)   TO=$(printf '%s' "$RAW" | tr -cd '0-9'); SHOWN="+91$TO"
             SENDER=(GATE_RELEASE=1 FORCE=1 /root/send-whatsapp.sh "$TO" /tmp/gate-body.txt "$CONTEXT") ;;
    esac

    if OUT=$(env "${SENDER[@]}" 2>&1); then
        mv "$f" "$SENT/$CODE.txt"
        log "APPROVED $CODE sent to $SHOWN"
        openclaw message send --target "$OWNER" --message "Sent to $SHOWN." >/dev/null 2>&1
    else
        mv "$f" "$FAILED/$CODE.txt"
        log "approved $CODE but send refused: $(echo "$OUT" | head -1)"
        openclaw message send --target "$OWNER" \
            --message "You approved it but it was refused before sending, so nothing went out. $(echo "$OUT" | head -1 | cut -c1-100)" >/dev/null 2>&1
    fi
    rm -f /tmp/gate-body.txt
done
