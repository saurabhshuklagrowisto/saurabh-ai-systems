---
name: aeo-content-brief-generator
description: Turns a "content" gap (a buyer question with no owned page answering it) into a writable brief -- the question's shape (how-to, best-of, comparison, definition), the matching schema type, a fact-grounded direct-answer opener, and a section outline with a word-count target. Never fabricates data -- when no real facts are supplied it scaffolds an explicit [INSERT] placeholder instead of inventing a claim. Use this on the `content`-type fixes returned by the AEO/GEO Improvement Bot, or on any raw list of buyer questions that need an AI-answer-shaped page written.
---

# AEO Content Brief Generator

Third piece of the AEO/GEO loop. [AEO / LLM Visibility Audit](../aeo-llm-visibility-audit) finds the gap questions. [AEO / GEO Improvement Bot](../aeo-geo-improvement-bot) diagnoses which ones need net-new content. This skill turns each of those into a brief a writer can execute today, without inventing the facts that make the answer citable.

## When to use

- On the `content`-type fixes from the improvement bot's `fixes[]`.
- Any time the ask is "write a page that answers X the way an AI assistant would quote it" -- direct answer first, structure after.

## When NOT to use

- For `schema`, `citation`, or `authority` fixes -- those need markup, outreach, or backlinks, not a new page. Route them to a schema-audit or outreach skill instead.
- As a final draft -- this produces a brief and an opener grounded in supplied facts, not the full article. A writer (human or a long-form content skill) still builds it out.

## Method

1. Classify the question's shape from its wording -- "how to" → how-to, "best/top/tools" → best-of/listicle, "vs/compare" → comparison, "what is/why" → definition, else general.
2. Match the shape to the schema type an AI crawler parses most reliably for that shape (HowTo, ItemList, FAQPage).
3. Draft the direct-answer opener strictly from the `facts` supplied for that question. If none are supplied, emit an explicit `[INSERT: ...]` placeholder rather than a fabricated claim -- ship-blocking on purpose.
4. Return a section outline and word-count target sized to the shape, so the brief is handoff-ready.

## Inputs

- `brand` -- the brand name
- `questions[]` -- each `{question, facts[]}`. `facts` are real, verifiable proof points about the brand relevant to that question; leave empty if none exist yet.

## Output (JSON)

`briefs[]` (each with `question`, `shape`, `recommended_schema`, `title_suggestion`, `opener_draft`, `sections[]`, `word_count_target`, `needs_real_data`), `questions_missing_data[]`, and a one-line `summary`.

## Run it

```bash
python scripts/content_brief.py         # built-in sample
python scripts/content_brief.py in.json # your own brand + questions + facts
```

Zero dependencies, no API keys. Feed its `briefs[]` to whatever writes the full page; feed `questions_missing_data[]` back to the brand team as "we need real proof points before this can publish."
