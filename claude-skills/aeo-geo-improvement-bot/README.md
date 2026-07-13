# AEO / GEO Improvement Bot

Second half of the AEO/GEO loop. [AEO / LLM Visibility Audit](../aeo-llm-visibility-audit) tells you which buyer questions the brand is invisible on inside ChatGPT/Perplexity/Gemini answers. This skill takes that gap list and turns it into a ranked, engine-ready fix plan: what's missing (content, schema, citations, or authority), what to do about it, and when to re-check.

## Why a separate skill

Diagnosing *why* a brand loses an AI answer and prioritising the fix is a distinct judgment call from measuring share of voice -- it needs a read of the brand's own site (does the page exist, does it carry structured data) and the wider web (who else corroborates the claim), not just the AI answers themselves. Keeping it separate means either skill can be swapped or improved independently, and the audit skill stays a pure measurement tool.

## Run it

```bash
python scripts/geo_improve.py         # built-in sample
python scripts/geo_improve.py in.json # your own brand + gap_questions + signals
```

## Sample output

```json
{
  "brand": "YourBrand",
  "fixes": [
    {
      "question": "best marketing automation platforms 2026",
      "fix_type": "citation",
      "recheck_after_days": 14,
      "priority": 89
    },
    {
      "question": "tools to make my brand discoverable in AI search",
      "fix_type": "content",
      "recheck_after_days": 21,
      "priority": 78
    },
    {
      "question": "how to automate outbound sales with AI",
      "fix_type": "schema",
      "recheck_after_days": 7,
      "priority": 60
    }
  ],
  "summary": "3 gap question(s) to close. Start with \"best marketing automation platforms 2026\" (citation fix, re-check in 14 days)."
}
```

## How it composes

`aeo-llm-visibility-audit` (measure) -> `aeo-geo-improvement-bot` (diagnose + prioritise, this skill) -> a content-writing / schema-audit skill (build the fix) -> re-run the audit (verify). The scheduled n8n version of the full loop is `pipeline-automation/aeo-geo-improvement-loop.json`.
