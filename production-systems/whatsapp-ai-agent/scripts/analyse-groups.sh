#!/bin/bash
#
# analyse-groups.sh
#
# Sanitised version of the production script running on a Contabo VPS.
# This is the actual bash that fires twice daily via cron, parses the
# OpenClaw log file, dedups WhatsApp group messages, and passes them
# to Claude Haiku for filtering.
#
# Sensitive values (operator phone number, VPS IP, persona-specific
# filter rules) have been replaced with placeholders. The control
# flow and the architectural choices are unchanged.
#
# Live since: early 2026
# Cron schedule: 9 AM and 9 PM IST daily
# Cost ceiling: $2/month hard cap on the OpenRouter API key
#

set -euo pipefail

# -----------------------------------------------------------------------------
# 1. Lock file. Prevents concurrent runs.
#    If the morning scan is slow and the evening cron fires before it finishes,
#    the second invocation exits immediately. No double-alerts, no token waste.
# -----------------------------------------------------------------------------
LOCKFILE="/tmp/analyse-groups.lock"
[ -f "$LOCKFILE" ] && exit 0
touch "$LOCKFILE"
trap "rm -f $LOCKFILE" EXIT

# -----------------------------------------------------------------------------
# 2. Timestamp guard. Saves NEW timestamp BEFORE processing.
#    If processing crashes, the next run still moves forward. Without this,
#    a failed run would replay the same messages on the next run, burning
#    tokens on duplicates.
# -----------------------------------------------------------------------------
LAST_SCAN_FILE="/root/.last_group_scan"
LAST_SCAN=$(cat "$LAST_SCAN_FILE" 2>/dev/null || echo "0")
NOW=$(date +%s)
echo "$NOW" > "$LAST_SCAN_FILE"

# -----------------------------------------------------------------------------
# 3. Parse the OpenClaw log file.
#    OpenClaw writes every received WhatsApp message to a daily log file.
#    We grep for "g.us" (group messages), then a Python one-liner does:
#      - JSON parse each line
#      - filter to body+timestamp+from
#      - drop messages shorter than 20 chars (noise)
#      - dedup using a `seen` set
#      - truncate each message to 150 chars (token saving)
# -----------------------------------------------------------------------------
MESSAGES=$(grep "g.us" /tmp/openclaw/openclaw-$(date +%Y-%m-%d).log \
    | grep '"body"' \
    | python3 -c "
import sys, json
last = $LAST_SCAN
msgs = []
seen = set()
for line in sys.stdin:
    try:
        d = json.loads(line)
        body = d.get('1', {}).get('body', '')
        ts = int(d.get('1', {}).get('timestamp', 0))
        if body and ts > last and len(body) > 20 and body not in seen:
            seen.add(body)
            msgs.append(body[:150])
    except: pass
for i, m in enumerate(msgs, 1):
    print(f'[{i}]{m}')
" 2>/dev/null)

# Nothing to process. Exit cleanly.
[ -z "$MESSAGES" ] && exit 0

TOTAL=$(echo "$MESSAGES" | wc -l)

# -----------------------------------------------------------------------------
# 4. Filter prompt + send.
#    The prompt is one tight paragraph. Strict rules. Claude Haiku follows
#    it reliably because the model isn't asked to reason about anything else.
#
#    Placeholders to fill in for your own use case:
#      $OPERATOR_NUMBER     where the filtered alert goes back to
#      $PROFILE_DESCRIPTION the persona the filter is tuned to
#      $REJECT_RULES        what to reject (age, gender, spam patterns)
#      $ACCEPT_RULES        what to accept (opportunity types relevant to ICP)
#      $EXTRACT_FIELDS      what to extract from each kept message
#      $OUTPUT_FORMAT       how Claude returns the result (table / JSON)
# -----------------------------------------------------------------------------
send_batch() {
    local batch="$1"
    [ -z "$batch" ] && return

    openclaw agent --to "$OPERATOR_NUMBER" --message "Filter for $PROFILE_DESCRIPTION.
REJECT: $REJECT_RULES
ACCEPT: $ACCEPT_RULES
EXTRACT: $EXTRACT_FIELDS
FORMAT: $OUTPUT_FORMAT
If none: No opportunities found.
---
$batch" --deliver

    # 10 second sleep between batches to avoid OpenRouter rate limits
    sleep 10
}

# -----------------------------------------------------------------------------
# 5. Batching. Cap at 50 messages per Claude call.
#    Larger batches were expensive on input tokens and harder for Haiku to
#    follow reliably. 50 is the sweet spot for this workload.
# -----------------------------------------------------------------------------
if [ "$TOTAL" -le 50 ]; then
    send_batch "$MESSAGES"
else
    BATCH1=$(echo "$MESSAGES" | head -50)
    BATCH2=$(echo "$MESSAGES" | tail -n +51)
    send_batch "$BATCH1"
    send_batch "$BATCH2"
fi

# -----------------------------------------------------------------------------
# Cost notes (after tuning):
#   ~$0.50 to $2 per month all-in (Claude Haiku via OpenRouter)
#   Previous spend was $15/month before the five optimisations in this script
#   (lock file, timestamp-before-process, dedup, truncation, batching).
#   See production-systems/whatsapp-ai-agent/cost-optimization-case-study.md
# -----------------------------------------------------------------------------
