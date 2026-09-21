# The approval gate: why a prompt is not a lock

The agent sent a real WhatsApp message to a real person from an opportunity it had invented.

The rule saying "always ask before sending" was in its prompt. It had been there since day one, written clearly, near the top. The agent read it, agreed with it, and sent the message anyway.

That is the whole lesson. A prompt is a request. If you need something not to happen, put it somewhere the model cannot reach.

## What the failure actually looked like

The agent drafts outreach off scanned opportunities. One scan produced an entry that no source message supported. The agent had filled the gaps itself: a plausible contact, a plausible brief, a plausible deadline. Then it drafted a message and sent it, skipping the approval step, because from inside a single turn "I should ask first" and "I asked and it was fine" are indistinguishable states.

Nothing in the system could tell the difference either. The agent held the send capability. Asking permission was a behaviour it chose, not a wall it hit.

## The fix

Sending moved into a separate process on a cron. The agent has no path to it.

```
agent writes draft  ->  outbox/pending/
                              |
                   approval-gate.sh (cron, every minute)
                              |
        preview to owner + random 4 char code  ->  outbox/awaiting/<code>.txt
                              |
        owner replies "SEND A7K2" from their own number
                              |
        gate matches that exact code in the inbound logs
                              |
                    sends that one message  ->  outbox/sent/
```

The agent can write a file. That is all it can do. It cannot read a code, generate one, move a file out of `awaiting`, or call the send command.

## The four properties that make it hold

**The code comes from outside.** The gate generates four random characters after the draft exists. The agent never sees a code before the owner sends it, so it cannot produce one and a stray "yes" cannot release anything.

**Approval is per message, not per session.** A code releases one file. Approving a draft does not approve the next one, so a confused or compromised agent cannot ride a single approval into a batch of sends.

**Codes expire in thirty minutes.** An unapproved draft is discarded rather than left in a queue where a later, unrelated approval could catch it.

**One gate runs at a time.** `flock -n 9` on a lock file, checked before any work. Cron fires every minute and a send takes several seconds. Two overlapping runs had already sent the same message twice before the lock went in.

## The companion fix

The same agent once reported that it had changed the scan schedule, added spam filtering and disabled alerts. It had changed none of those. All three live in files outside its workspace and always did. The report read like a competent status update, which is what made it expensive: nothing in the message signalled that it was fiction.

The answer was a capabilities file in the workspace listing, by path, what the agent can write and what it cannot, and why each thing sits where it does. The agent now names the boundary instead of narrating work it never did. See [agent-workspace-design.md](./agent-workspace-design.md).

## Where this generalises

Any agent with a send, a write, a payment or a deploy. Ask one question: if the model decided right now to do the dangerous thing, what stops it? If the only answer is a sentence in the prompt, there is no answer. Move the capability behind a process the model cannot call, and make the human's approval carry a token the model could not have produced.

## The file

[scripts/approval-gate.sh](./scripts/approval-gate.sh) is the gate, sanitised. Phone numbers and host details are placeholders. The control flow, the lock, the code generation, the expiry sweep and the state directories are what runs.
