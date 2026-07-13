---
name: lead-nurture-sequencer
description: Stages leads by real engagement signal (opens, clicks, replies, meetings booked, unsubscribes, days since last touch) and decides the next nurture action for each -- what to send, and how many days until it's due. Enforces the suppression/cooling rules that keep automated nurture from talking over a real reply or a booked meeting, or re-touching someone who unsubscribed. Use to run or audit an email/lifecycle nurture cadence, decide who's due for a touch today, or check that automation isn't stepping on human-handled leads.
---

# Lead Nurture Sequencer

Nurture cadences break in one of two ways: leads go quiet because nothing re-engages them, or automation keeps emailing someone who already replied, booked a meeting, or unsubscribed. This skill fixes both -- it stages every lead off real signal, not off "days since the sequence started," and hard-stops automation the moment a human should own the thread.

## When to use

- Deciding which leads are due for a nurture touch today, and what that touch should be.
- Auditing an existing sequence for suppression bugs -- leads who replied or unsubscribed but are still receiving automated sends.
- Building the staging logic behind an email/marketing-automation nurture flow.

## When NOT to use

- For lead scoring against an ICP (fit, firmographics) -- that's a qualification skill, not a nurture-cadence one. This only reads engagement behaviour.
- For writing the actual nurture email copy -- this decides *what kind* of touch and *when*, not the words.

## Method

1. Check suppression first, always: `unsubscribed` and `meeting_booked` short-circuit everything else -- no engagement math overrides them.
2. A real `replied` beats every automated signal -- a human must respond within 24 hours, and no scheduled send should follow.
3. Absent those, read opens/clicks/recency: clicks + recent activity = warm (send proof); opens with no clicks = curious (vary the angle); no opens for 30+ days = cold (breakup email, don't just keep silently sending).
4. Attach a cooldown per stage and compute how many days until the next touch is due, so the plan is schedulable, not just descriptive.

## Inputs

- `brand` -- the brand name
- `leads[]` -- each `{name, days_since_last_touch, email_opens, email_clicks, replied, meeting_booked, unsubscribed}`. In production these come from the email platform or CRM webhook; the demo ships a deterministic sample.

## Output (JSON)

`leads[]` (each with `name`, `stage`, `action`, `next_touch_in_days`, `due_now`), `stage_counts`, `due_now[]` (names due today), and a one-line `summary`.

## Run it

```bash
python scripts/nurture_sequencer.py         # built-in sample
python scripts/nurture_sequencer.py in.json # your own brand + leads
```

Zero dependencies, no API keys. To go live, swap the sampled `leads` for a real CRM/email-platform pull; the staging and suppression logic stays identical. A scheduled n8n version of this exact logic follows the same pattern as `pipeline-automation/aeo-geo-improvement-loop.json`.
