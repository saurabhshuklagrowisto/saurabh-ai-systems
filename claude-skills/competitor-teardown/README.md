# Competitor Teardown

Turns a messy competitive landscape into a scored positioning matrix and a single recommended wedge. Answers the only three questions that matter: where do we win, where do we lose, and what is the angle no one else can copy.

## What it does

Input: your brand, 2-5 competitors, and the 5-8 dimensions a buyer actually decides on — each scored 0-5 per player, each weighted 1-3 by how much it moves a deal.

Output:
- **Ranking** — weighted total and percentage per player.
- **Wins** — dimensions where you lead.
- **Losses** — dimensions where a competitor leads you (with who).
- **Whitespace** — dimensions the whole category is weak on; own them before anyone does.
- **Wedge** — the single dimension where you are strong and the field is weak. Your sharpest, most defensible positioning.

## How to run

```bash
python scripts/teardown_score.py          # built-in sample
python scripts/teardown_score.py in.json  # your own landscape
```

Zero dependencies, no API keys. See `demo_output.json` — in the sample, the brand leads on time-to-value and AI-native workflow, loses on enterprise security and integrations, and the recommended wedge is time-to-value.

## Why it is built this way

The hard part of competitive work is not gathering facts, it is forcing a decision. By making every dimension a weighted 0-5 score from evidence, the output is a defensible matrix instead of prose — and the wedge falls out of the math rather than a hunch. Score the dimensions from real buyer evidence (reviews, win/loss notes, sales-call recordings), not gut feel, and the recommendation is only as good as that evidence.
