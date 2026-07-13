# AEO Content Brief Generator

Third piece of the AEO/GEO loop. [AEO / LLM Visibility Audit](../aeo-llm-visibility-audit) measures which buyer questions the brand is invisible on. [AEO / GEO Improvement Bot](../aeo-geo-improvement-bot) diagnoses which of those need net-new content. This skill turns each `content`-type fix into a writable brief -- without inventing the facts that make the answer citable.

## Why a separate skill

Deciding a question's shape (how-to vs. best-of vs. comparison vs. definition) and grounding the opener in real facts is a distinct step from prioritising *which* gap to fix first. Keeping it separate also keeps the no-fabrication rule enforceable in one place: this skill will not draft an answer sentence it wasn't given real facts for, full stop.

## Run it

```bash
python scripts/content_brief.py         # built-in sample
python scripts/content_brief.py in.json # your own brand + questions + facts
```

## Sample output

```json
{
  "briefs": [
    {
      "question": "how to automate outbound sales with AI",
      "shape": "how-to",
      "recommended_schema": "HowTo",
      "opener_draft": "YourBrand cuts manual prospecting time by routing replies by intent automatically.",
      "word_count_target": 900,
      "needs_real_data": false
    },
    {
      "question": "best marketing automation platforms 2026",
      "shape": "best-of",
      "recommended_schema": "ItemList",
      "opener_draft": "[INSERT: one direct, factual sentence ... -- do not publish this placeholder]",
      "word_count_target": 1100,
      "needs_real_data": true
    }
  ],
  "questions_missing_data": ["best marketing automation platforms 2026"],
  "summary": "3 brief(s) drafted. 1 still need real facts supplied before the opener can be written."
}
```

## How it composes

`aeo-llm-visibility-audit` (measure) -> `aeo-geo-improvement-bot` (diagnose + prioritise) -> `aeo-content-brief-generator` (this skill: brief the `content` fixes) -> a writer or long-form content skill builds the full page -> re-run the audit to verify the gap closed.
