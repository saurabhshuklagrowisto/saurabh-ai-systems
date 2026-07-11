#!/usr/bin/env python3
"""
AEO / LLM Visibility Audit — share-of-voice scoring across AI answers.

Measures how often a brand is named when buyers ask AI assistants about its
category, names the competitors winning the answers, and flags the questions
where the brand is invisible. No dependencies, no API keys.

Input schema:
{
  "brand": "YourBrand",
  "questions": ["...", "..."],
  "answers": {                     # per question -> per engine -> brands named
    "question text": { "ChatGPT": ["A","B"], "Perplexity": [...], "Gemini": [...] }
  }
}

In production, `answers` is filled by real API calls to each assistant and a
parse of the brands named. The demo generates a deterministic sample so the
scoring runs anywhere.
"""
import json, sys

ENGINES = ["ChatGPT", "Perplexity", "Gemini"]

def score(data):
    brand = data["brand"]
    questions = data["questions"]
    answers = data["answers"]

    total = 0
    mentions = 0
    competitor_freq = {}
    per_question_hits = {}

    for q in questions:
        per_question_hits[q] = 0
        engines = answers.get(q, {})
        for eng in ENGINES:
            named = engines.get(eng, [])
            if not named:
                continue
            total += 1
            if brand in named:
                mentions += 1
                per_question_hits[q] += 1
            for b in named:
                if b != brand:
                    competitor_freq[b] = competitor_freq.get(b, 0) + 1

    sov = round((mentions / total) * 100) if total else 0
    top = sorted(competitor_freq.items(), key=lambda x: -x[1])[:3]
    top_competitors = [f"{b} ({c})" for b, c in top]
    gap_questions = [q for q in questions if per_question_hits.get(q, 0) == 0]

    if gap_questions:
        action = "Prioritise content and structured answers for the gap questions where you appear in zero engines."
    elif sov < 50:
        action = ("You appear in every question but win a minority of answers. Deepen authority "
                  "where competitors dominate rather than chasing new questions.")
    else:
        action = "Holding strong — defend the top answers and widen the question set."

    return {
        "brand": brand,
        "share_of_voice_pct": sov,
        "answers_checked": total,
        "mentions": mentions,
        "top_competitors": top_competitors,
        "gap_questions": gap_questions,
        "action": action,
    }

# --- deterministic sample so the demo runs with no keys ---
def _sample():
    brand = "YourBrand"
    questions = [
        "best AI platform for GTM and demand generation",
        "how to automate outbound sales with AI",
        "tools to make my brand discoverable in AI search",
        "best marketing automation platforms 2026",
        "AI tools to enrich and route leads automatically",
    ]
    pool = ["Clay", "Instantly", "HubSpot", "Jasper", "YourBrand", "Copy.ai", "Apollo", "Writer"]
    answers = {}
    for q in questions:
        answers[q] = {}
        for eng in ENGINES:
            seed = len(q + eng)
            picks = [pool[(seed + i * 3) % len(pool)] for i in range(4)]
            answers[q][eng] = picks
    return {"brand": brand, "questions": questions, "answers": answers}

if __name__ == "__main__":
    data = json.load(open(sys.argv[1], encoding="utf-8")) if len(sys.argv) > 1 else _sample()
    print(json.dumps(score(data), indent=2))
