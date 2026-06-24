# Case Study · Cost down from $15 to under $2 per month

When the WhatsApp AI agent first went live, it burned around $15 per month in API spend. After investigation that was unexpected — the workload was 2 batched calls per day. The fix turned out to be five small changes, none of which were the obvious "switch to a cheaper model" answer.

This is a real example of how the difference between a $0.50 a month agent and a $15 a month agent is operational discipline, not model choice.

## The five issues, ranked by how much they cost

### 1 · `historyLimit: 2` was the wrong number, and not in the direction you would expect

OpenClaw's agent has a `historyLimit` config that controls how many prior messages get loaded into context per session. The initial setting was 2, on the assumption that less context means lower cost.

It was the opposite. With `historyLimit: 2`, every interaction loaded almost no history. The agent then made extra tool calls to compensate (looking up the user's profile, checking past decisions, re-confirming context). Each extra tool call is an extra Claude round trip. The "save tokens" config was actually making the agent burn three round trips where it should have done one.

Fix: set `historyLimit: 15`. Counter-intuitive, but it is the sweet spot for this workload. Above 20 the context cost dominates again. The sweet spot is workload-specific and the only way to find it is to try a few values and watch the bill.

### 2 · Duplicate script runs sent the same messages to Claude twice

The original `analyse-groups.sh` script had no lock file. If the morning scan was slow and the evening scan fired before it finished, both ran in parallel and processed the same log file. Same messages, sent to Claude twice. Sometimes three times if a third manual run snuck in.

Fix: a lock file at the top of the script. Trap the lock removal on exit so it cleans up properly even on crash.

```bash
LOCKFILE="/tmp/analyse-groups.lock"
[ -f "$LOCKFILE" ] && exit 0
touch "$LOCKFILE"
trap "rm -f $LOCKFILE" EXIT
```

Five lines. Removed the duplicate runs entirely.

### 3 · Batches were too big and not deduplicated

Some days had 200 messages in the scan window. The old script sent all 200 in a single Claude call. Two issues. One: a 200-message prompt is expensive on input tokens. Two: many of those 200 messages were duplicates (the same opportunity reposted across groups), so the same content was being analysed several times.

Fix: dedupe within the batch using a `seen` set. Cap each message at 150 characters (the original message has more context than the filter needs). Split into batches of 50 with a 10-second sleep between batches.

```python
msgs = []
seen = set()
for line in sys.stdin:
    body = ...
    if body and ts > last and len(body) > 20 and body not in seen:
        seen.add(body)
        msgs.append(body[:150])
```

This change alone roughly cut input tokens by 60% on busy days.

### 4 · The timestamp was being saved AFTER processing, not before

Original script saved the "last scan" timestamp after the Claude call completed. When the call failed (credit exhausted, rate limit, network hiccup) the timestamp was never written, and the next run re-processed all the same messages and tried to call Claude again. A bad day could rack up 4 to 6 redundant Claude calls.

Fix: save the timestamp before processing. If the processing crashes, the next run still moves forward and we just lose one batch instead of replaying it forever.

```bash
echo "$NOW" > "$LAST_SCAN_FILE"   # save BEFORE processing
```

One line. Solved the cost-blowup-on-failure problem.

### 5 · Tried free model pre-filtering, abandoned it

The optimistic idea was to pre-filter using a free local model (Ollama running llama3.2:3b on the same VPS), and only send the survivors to Claude. In theory: free pre-filter, cheap Claude finishing pass.

It failed on reliability. llama3.2:3b at 3B params could not reliably classify which messages were opportunities versus chatter. Worse, when asked to return message indices for the filtered set, it returned a phone number string from one of the messages instead. The output was wrong about 30% of the time, in ways that were hard to detect downstream.

The decision: every filter call goes through Haiku. The cost difference between Haiku and a 3B local model on this volume is not worth the reliability tax. Haiku at $0.25 per million input tokens is cheap enough that an honest model beats a free unreliable one.

Lesson kept: free does not equal cheap when "free" produces bad outputs you then have to fix. The right answer is to use the cheapest model that is reliable for the task, not the cheapest model that exists.

## The hard spending cap on OpenRouter

Final piece. OpenRouter (the model provider) supports a per-key monthly spending cap. Set to $2. If the agent ever does try to burn more than $2 in a month (because of a bug, a runaway loop, an accidental spam input), the key just stops working. The agent fails closed.

This is a guardrail at the financial layer, not the code layer. Even if every other safety net fails, the spending cap holds.

## What is now baked in

| Layer | Setting |
|---|---|
| Context | `historyLimit: 15` (sweet spot for this workload) |
| Debounce | `debounceMs: 5000` (batches rapid messages into one AI call) |
| Concurrency | Lock file in the bash script |
| State | Timestamp saved before processing, not after |
| Dedup | Within-batch dedup using a `seen` set |
| Truncation | Each message capped at 150 chars |
| Batching | Max 50 messages per Claude call, 10 second sleep between batches |
| Model | Claude Haiku 4.5 (no pre-filter layer) |
| Cost ceiling | $2 per month hard cap on OpenRouter key |

End state · $0.50 to $2 per month. Down from $15. Same coverage, same quality, same agent behaviour.

## The general lesson

The default mental model for cutting AI costs is "use a cheaper model". For most production agents, the actual savings live in:

1. Eliminating duplicate calls (lock files, dedup, timestamp guards)
2. Tuning the context window to the workload (not always "as small as possible")
3. Batching aggressively
4. Trimming inputs to what the model actually needs
5. A hard spending cap so a bug cannot bankrupt you

Model choice is the last 10 to 20 percent. The 80 percent is the orchestration around the model.
