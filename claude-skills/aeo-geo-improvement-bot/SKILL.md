---
name: aeo-geo-improvement-bot
description: Turns AEO/GEO visibility gaps (the questions where a brand is invisible in ChatGPT, Perplexity, or Gemini answers) into a ranked, engine-ready fix plan. Takes the gap questions from the AEO / LLM Visibility Audit skill plus a read of what's missing on each one -- owned content, structured data, third-party citations -- and returns a prioritised action list: what to build first, the exact fix, and when to re-check. Use this after running the visibility audit, whenever the ask is "how do we actually close these AEO/GEO gaps" rather than just measure them.
---

# AEO / GEO Improvement Bot

The visibility audit tells you *where* a brand is invisible in AI answers. This skill tells you *what to do about it* -- it is the second half of the loop: measure, diagnose, fix, re-measure.

## When to use

- Right after running [AEO / LLM Visibility Audit](../aeo-llm-visibility-audit) and getting back `gap_questions`.
- When the ask is to build an actual improvement plan, not another audit -- content briefs, schema fixes, citation targets, in priority order.
- To decide what a content/SEO team should work on first when there are more gaps than there is time.

## When NOT to use

- To measure share of voice in the first place -- that's the visibility audit skill.
- As a substitute for writing the content or shipping the schema -- this produces the plan and the specific instruction, not the final asset. Feed the `content` fixes to a content-writing skill and the `schema` fixes to a schema-audit skill.

## Method

1. For every gap question, read four signals: does an owned page answer it, does that page carry schema markup, how many independent (third-party) sources corroborate it, and how much demand it represents.
2. Classify the gap into exactly one root cause, cheapest-explanation-first: **no content** > **no schema** > **no citations** > **authority deficit**. Fixing the wrong layer wastes effort -- adding schema to a page that doesn't exist does nothing.
3. Prioritise: higher demand first; at equal demand, cheaper fixes (schema) surface before expensive ones (earning citations or authority) so the plan front-loads fast wins.
4. Attach a re-check window per fix type -- schema changes show up in re-crawls faster than earned citations do.

## Inputs

- `brand` -- the brand name
- `gap_questions` -- from the visibility audit's `gap_questions[]`
- `signals` -- per question: `has_owned_content`, `has_schema_markup`, `third_party_mentions`, `search_volume_proxy` (1-10). In production these come from a site crawl + a third-party source search; the demo ships a deterministic sample.

## Output (JSON)

`fixes[]` (each with `question`, `fix_type`, `action`, `recheck_after_days`, `priority`), `fix_type_mix`, and a one-line `summary` naming the top fix to start on.

## Run it

```bash
python scripts/geo_improve.py         # built-in sample
python scripts/geo_improve.py in.json # your own brand + gap_questions + signals
```

Zero dependencies, no API keys. To go live: swap the sampled `signals` for a real site crawl (does the page exist, does it carry JSON-LD) and a real third-party mention count; the classification and prioritisation logic stays identical. Chain it after `aeo_score.py`'s output and, on a schedule, after re-running the audit to confirm each fix moved the needle -- a scheduled n8n version of the full measure-diagnose-fix-recheck loop ships in `pipeline-automation/aeo-geo-improvement-loop.json`.
