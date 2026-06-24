# WhatsApp AI Agent on a VPS

A WhatsApp Claude agent running on a self-hosted Contabo VPS. The agent monitors WhatsApp group messages on a cron, filters opportunities through Claude using a strict rules prompt, and alerts the user with a numbered list. On approval it drafts and sends application messages back through WhatsApp.

Built originally as a side project to scan WhatsApp groups for time-bounded opportunities. Same pattern transfers to any WhatsApp-based intake stream you want an AI agent on.

## What problem it solves

WhatsApp is where a lot of real opportunities live, especially in India. Sales leads, casting calls, freelance gigs, partnership invites. Groups move fast. By the time you scroll through hundreds of messages, the time-sensitive ones are buried. Manually filtering them every day eats hours.

This system reads the groups for you, twice a day, filters by your rules, and alerts you with a clean list of what to act on.

## What is open here

| File | What it shows |
|---|---|
| [README.md](./README.md) | This doc. Architecture and patterns. |
| [cost-optimization-case-study.md](./cost-optimization-case-study.md) | How the monthly run cost dropped from $15 to under $2 through five small changes. Useful if you are running any Claude agent at sustained volume. |
| [**scripts/analyse-groups.sh**](./scripts/analyse-groups.sh) | The actual bash script running on the VPS, sanitised. Real control flow, real cron entry, real Python parsing inline. Phone numbers, IP, and persona-specific filter rules replaced with placeholders. |

The full system is on a private VPS. Phone numbers and the specific filter rules for the user's domain are not in the public repo. The architecture, the scripts and the cost story are.

## The infrastructure

| Component | Choice | Why |
|---|---|---|
| VPS | Contabo, Ubuntu 24 | Cheap, reliable, full root access |
| WhatsApp gateway | OpenClaw | Self-hosted, no third-party WhatsApp Business API fees, links to a real WhatsApp number |
| Model | Claude Haiku 4.5 via OpenRouter | Fastest cheap model that follows strict-rule prompts reliably |
| Scheduler | Linux cron | Simpler and more reliable than n8n or a webhook server for this scope |
| Trigger | Bash plus Python | Parses the OpenClaw log files, passes filtered messages to Claude via the OpenClaw agent CLI |

## The architecture

```
                    Cron at 9:00 AM and 9:00 PM IST
                                |
                                v
                  ┌─────────────────────────────┐
                  │  /root/analyse-groups.sh    │
                  │  - lock file (no concurrency)│
                  │  - timestamp BEFORE process │
                  │  - dedup via "seen" set     │
                  │  - 150 char trunc per msg   │
                  │  - batch of 50 if many      │
                  └──────────┬──────────────────┘
                              |
                              v
                  ┌─────────────────────────────┐
                  │  Parse the OpenClaw log     │  /tmp/openclaw/openclaw-YYYY-MM-DD.log
                  │  grep "g.us" to keep groups │  Python JSON parse, filter on timestamp
                  │  extract body, dedup        │  longer than 20 chars
                  └──────────┬──────────────────┘
                              |
                              v
                  ┌─────────────────────────────┐
                  │  openclaw agent CLI         │  passes filtered messages as a single
                  │  --to <user phone>          │  user message to Claude Haiku
                  │  --message "...filter rules │  Haiku applies the rules prompt and
                  │  ...batch of messages..."   │  returns the filtered table
                  │  --deliver                  │
                  └──────────┬──────────────────┘
                              |
                              v
                  ┌─────────────────────────────┐
                  │  Claude on WhatsApp         │  user gets a numbered table:
                  │  delivers filtered list     │  No | Type | Details | Contact | Apply
                  │  to user via WhatsApp       │
                  └──────────┬──────────────────┘
                              |
                              v                  User says "apply 3"
                  ┌─────────────────────────────┐
                  │  Claude drafts message      │  uses profile from SOUL.md
                  │  asks "Send?"               │
                  └──────────┬──────────────────┘
                              |
                              v                  User says "yes"
                  ┌─────────────────────────────┐
                  │  openclaw message send      │  outbound WhatsApp message to
                  │  --target +91XXXXXXXXXX     │  the opportunity contact
                  └─────────────────────────────┘
```

## The architecture choices that matter

**Claude on WhatsApp cannot natively read groups.** OpenClaw's agent session only sees direct messages. The workaround is the log file. OpenClaw writes every received group message to a daily log on disk. The cron script reads the log file, filters with a Python one-liner, and passes the filtered text to Claude as a normal direct message. No API auth, no n8n webhook, no token games. The simplest path that works.

**Cron plus bash beat the n8n attempt.** An earlier version used an n8n workflow with webhooks. It worked but had two issues: it depended on n8n being healthy, and debug output for failed runs was harder to access. Switching to plain cron plus a single bash file made the system simpler and more reliable. n8n is still installed on the VPS for other workflows. For this one, cron won.

**Timestamp saved before processing.** A subtle but critical detail. The script writes the new "last scan" timestamp before it processes the batch. If processing crashes halfway through, the next run does not re-process the messages it already alerted on. Without this, every failed run becomes a duplicate flood the next day.

**Lock file prevents concurrent runs.** If the morning run is still going when the evening cron fires, the second one exits immediately. No race conditions, no double-alerts.

**Filter prompt is one tight paragraph.** Not a 3000 character system prompt. Just the rules. "Filter for [profile]. REJECT: ... ACCEPT: ... Extract: ..." Haiku follows it reliably because the rules are explicit and the model is not asked to reason about anything else.

**Two-step send (draft then approve).** Auto-sending WhatsApp messages to real people is dangerous. The system always drafts, asks for explicit approval, and only sends after a "yes". Same human-in-the-loop pattern as the production reply triage agent.

## Numbers

Live production for several months.

- **Coverage** · Every group message above 20 chars in the configured groups, twice daily
- **Volume** · Typically 30 to 80 group messages per scan, sometimes more
- **Filter precision** · Manually estimated. Claude returns roughly 3 to 7 actionable items from a 50-message batch. Junk that slips through is rare.
- **Cost** · Currently $0.50 to $2 per month all-in (model + VPS share). Was $15 a month before tuning, see the case study.
- **Reliability** · Uptime above 99% across the deployed window. The few outages have been credit-runs-out events on OpenRouter, not infrastructure failures.

## Why this transfers

Anything that produces a high-volume stream of text where most of it is noise and a few items are actionable: WhatsApp groups, Slack channels, Telegram, email inboxes, support queues. Replace OpenClaw with the channel's API, replace the filter prompt with your own rules, and the rest of the architecture (cron, log file, lock, timestamp guard, dedup, batched filter call, human-in-the-loop send) all transfers.

## Stack

VPS · Contabo Ubuntu 24
WhatsApp gateway · OpenClaw (self-hosted, links to a real WhatsApp number)
Model · Claude Haiku 4.5 via OpenRouter
Scheduler · Linux cron
Scripting · bash + Python 3
Config · single JSON file at `/root/.openclaw/openclaw.json` plus a SOUL.md for the agent profile

## What is in scope, what is not

In scope · Scan groups twice daily, filter via strict rules, alert the user on WhatsApp, draft and send approved messages.

Not in scope · Auto-reply in groups (the config has `requireMention: true` so the agent never speaks unless tagged). Sending without explicit approval. Reading messages outside the configured groups. Cross-platform monitoring (WhatsApp only for now).
