---
name: competitor-teardown
description: Turns a messy competitive landscape into a scored positioning matrix and a recommended wedge. Takes your brand plus 2-5 competitors and a set of buyer-decision dimensions, each scored 0-5 per player, and returns where you win, where you lose, the category whitespace nobody owns, and the sharpest wedge to position on. Use before writing positioning or messaging, before a launch, or when a rep keeps losing deals to the same competitor and you need to know why.
---

# Competitor Teardown Skill

Most competitive analysis is a wall of prose nobody acts on. This skill forces the landscape into a scored matrix and then answers the only three questions that matter: where do we win, where do we lose, and what is the wedge no one else can copy.

## When to use

- Before writing positioning or homepage messaging.
- Before a launch, to pick the angle competitors cannot easily counter.
- When deals keep slipping to one competitor and you need to see the pattern.

## When NOT to use

- For feature checklists to hand to product — this is about buyer-decision positioning, not a spec sheet.
- With only your own opinion as input — score dimensions from real buyer evidence (reviews, sales-call notes, win/loss), not gut feel.

## Method

1. Pick the **dimensions a buyer actually decides on** (not every feature — the 5-8 that move a deal).
2. Score every player 0-5 on each dimension, from evidence.
3. The engine returns:
   - **Wins** — dimensions where you lead.
   - **Losses** — dimensions where a competitor leads you.
   - **Whitespace** — dimensions the whole category scores low on (own it before anyone does).
   - **Wedge** — the single dimension where you are strong and the field is weak: your sharpest positioning.

## Inputs

```json
{
  "brand": "YourBrand",
  "competitors": ["Rival A", "Rival B"],
  "dimensions": [
    {"name": "Time to value", "weight": 3, "scores": {"YourBrand": 5, "Rival A": 2, "Rival B": 3}}
  ]
}
```
`weight` (1-3) reflects how much the dimension moves a buyer.

## Output (JSON)

`ranking[]` (weighted total per player), `wins[]`, `losses[]`, `whitespace[]`, and a single recommended `wedge` with the reason.

## Run it

```bash
python scripts/teardown_score.py          # built-in sample
python scripts/teardown_score.py in.json  # your own landscape
```

Zero dependencies, no API keys. Deterministic scoring in `scripts/teardown_score.py`.
