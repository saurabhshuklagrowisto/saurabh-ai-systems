# AEO / LLM Visibility Audit

Measures whether a brand shows up when buyers ask AI assistants about its category — and turns the gaps into a content plan. This is answer-engine optimisation (AEO/GEO): the new page one is a single AI answer, not ten blue links.

## What it does

Input: a brand, a set of real buyer questions, and the brands each engine (ChatGPT / Perplexity / Gemini) names in its answer.

Output: **share of voice** (share of answers that name you), the **competitors** winning those answers, and the **gap questions** where you appear in zero engines — your highest-leverage content targets.

## How to run

```bash
python scripts/aeo_score.py          # built-in sample
python scripts/aeo_score.py in.json  # your own brand + questions + answers
```

Zero dependencies, no API keys. See `demo_output.json` for a real run.

## Going live

The demo fills the `answers` with a deterministic sample so the scoring runs anywhere. To take it live, replace that with real API calls to each assistant and a parse of the brands named — the scoring is unchanged. A scheduled, self-running version of this exact logic ships as an importable n8n workflow in `pipeline-automation/aeo-llm-visibility-monitor.json`, so this can run weekly and post to Slack on its own.

## Why it matters

Buyers increasingly shortlist tools by asking an AI assistant, not by scrolling a SERP. If your brand is absent from those answers, you are invisible at the exact moment of consideration. This skill makes that visibility measurable and gives you the ranked list of questions to go win.
