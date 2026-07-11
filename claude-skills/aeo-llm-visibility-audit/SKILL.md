---
name: aeo-llm-visibility-audit
description: Measures whether a brand shows up when buyers ask AI assistants (ChatGPT, Perplexity, Gemini) about its category, and turns the gaps into a content plan. Takes a brand name and a set of real buyer questions, checks which brands each engine names, and returns a share-of-voice score, the competitors winning the answers, and the exact questions where the brand is invisible. Use to audit AI/answer-engine discoverability (AEO/GEO), to prioritise content that AI assistants will cite, or to track share of voice in AI answers over time.
---

# AEO / LLM Visibility Audit Skill

Search is moving from ten blue links to one AI answer. This skill measures the new page one: when your buyer asks ChatGPT, Perplexity, or Gemini for the best tool in your category, does your brand get named — and if not, who does, and on which questions.

## When to use

- To baseline and track **answer-engine optimisation (AEO/GEO)** — visibility inside AI-generated answers.
- To decide which content to write next: the questions where you are invisible are your highest-leverage targets.
- To benchmark share of voice against named competitors in AI answers over time.

## When NOT to use

- For classic Google SEO rank tracking — that is a different surface; use an SEO tool.
- For brand sentiment — this measures presence in answers, not tone.

## Method

1. Take the real questions your buyers type into AI assistants.
2. For each question, across each engine, capture which brands the answer names.
3. Score: **share of voice** = the share of answers that name you; list the competitors named most; flag the questions where you appear in **zero** engines (true content gaps).

## Inputs

- `brand` — your brand name
- `questions` — the buyer questions to test
- `answers` — for each (question, engine), the brands named. In production these come from live API calls to each assistant; the demo ships a sampled set so the logic runs with no keys.

## Output (JSON)

`share_of_voice_pct`, `answers_checked`, `mentions`, `top_competitors[]`, and `gap_questions[]` — the questions to target first.

## Run it

```bash
python scripts/aeo_score.py         # built-in sample
python scripts/aeo_score.py in.json # your own brand + questions + answers
```

Zero dependencies, no API keys. To go live, replace the sampled answers with real calls to the ChatGPT / Perplexity / Gemini APIs; the scoring stays identical. A scheduled n8n version of this exact logic ships in `pipeline-automation/aeo-llm-visibility-monitor.json`.
