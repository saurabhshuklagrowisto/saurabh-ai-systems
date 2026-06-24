# Signal Monitor

Every morning, Claude reads new signals (LinkedIn posts, news, funding, hiring) across the top 100 target accounts, rates each on relevance plus persona match plus recency, and pushes a ranked digest of the top 3 to 5 to SDRs.

This is the closest analog to the "Sales Copilot signal capture" pattern. Sources change per industry; the reasoning layer doesn't.

## What it does

**Input:** a list of raw signals tagged with account, persona, date, source URL, signal text.
**Output:** a JSON array (one rated object per signal) plus a rendered Slack or Cliq-style digest of the actionable few.

Each signal is scored on:
- **Relevance** (0-10) · 10 = direct buying signal; 0-2 = noise
- **Persona match** (bool) · does the signal align with the persona we sell to at this account?
- **Recency band** · last_7d / last_30d / last_90d / older
- **send_to_sdr** (bool) · triggered only when relevance is at least 7, persona matches, and the signal is in the last 30 days

The recency cliff is hard: anything older than 90 days gets `send_to_sdr: false` regardless of relevance.

## What it proves

- **Multi-gate filtering** · three independent gates (relevance, persona, recency) all compound, no single signal sneaks through
- **One-signal-per-account dedup** · if the same account has 4 signals today, only the highest-relevance one reaches the SDR
- **Hook-grounded outputs** · each rated signal includes a `hook_angle` that an SDR can literally use in outreach, anchored to the specific signal

## How to run

```bash
python signal_rater.py --demo
```

Output is a scored table plus a rendered Markdown digest preview. Save the full digest with `--save`:

```bash
python signal_rater.py --demo --save
# writes digest_today.md
```

Live API mode:
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
python signal_rater.py --live --input sample_signals.json
```

## Layout

```
signal-monitor/
├── signal_rater.py           the agent plus digest renderer
├── prompt.md                 rating rubric plus hard rules
├── sample_signals.json       8 realistic mixed-quality signals
├── demo_output.json          recorded outputs (replays in --demo)
└── digest_demo.md            rendered Slack-style digest example
```

## Map to a Sales Copilot

For a Sales Copilot targeting a specific industry, the same architecture applies. Only the signal sources change. Where this demo reads LinkedIn, news and funding, an industry Copilot reads operational events relevant to that industry. The rating rubric, the recency cliff, the dedup logic, the persona match are all unchanged.
