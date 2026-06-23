# 04 · Pre-Meeting Brief Generator

30 minutes before a sales meeting, an agent compiles a one-page brief: where the account stands, the signals that matter for this call, three talking points, one risk to handle, one question to ask, and three things NOT to say. Lands in the AE's inbox + Cliq.

---

## What it does

**Trigger:** a meeting on the AE's calendar is 30 minutes out.
**Process:** the agent identifies the external attendee, matches them to a CRM record (with confidence scoring), pulls recent signals, persona pain themes, and prior touch history, then generates the brief.
**Output:** structured JSON + rendered Markdown brief.

## What it proves

- **Identity resolution with confidence** — low-confidence matches (< 0.7) trigger an explicit warning rather than silently producing a confident-looking brief
- **Data freshness as a first-class concern** — signals older than 30 days get tagged with a freshness warning the AE can see
- **No-fabrication rule** — every talking point traces to an input signal or CRM fact; the prompt explicitly bans "they are growing" generic hooks
- **Honest risk modeling** — the brief includes one REAL risk + concrete handling language, not "they might be busy"

## How to run

```bash
python meeting_brief.py --demo
```

The demo input is a realistic meeting scheduled with Priya Menon, Director MTech at "ExampleBPM" — a fictional BPM company with UK utilities expansion + active hiring for a Marketing Engineering Lead role. The generated brief:
- Opens the call by referencing Priya's actual LinkedIn post (specific, not generic)
- Names the three signal types her UK utilities expansion implies (outage, billing, digital transformation)
- Frames the open MEL role as partner-of-choice (not replacement)
- Flags the May-22 signal as past the 30-day recency window

Live API mode:
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
python meeting_brief.py --live --input sample_meeting.json
```

## Layout

```
04-meeting-brief/
├── meeting_brief.py          ← the agent + Markdown renderer
├── prompt.md                 ← brief generator system prompt
├── sample_meeting.json       ← full meeting + CRM + signals + persona
├── demo_output.json          ← recorded brief output
└── brief_demo.md             ← rendered one-page brief example
```

## Map to a Sales Copilot

This IS a Sales Copilot — for outbound rather than for a specific vertical. The architecture transfers:
- Identity resolution layer (attendee → CRM)
- Context fetch (CRM history + signals + persona)
- Reasoning layer (Claude generates the brief)
- Delivery (inbox + Slack/Cliq)

For a UK utilities Sales Copilot, the identity layer reads the customer database, the context fetch adds outage events and billing-pressure flags, and the brief format adjusts to operations-team consumption. The agent reasoning and the prompt shape stay constant.
