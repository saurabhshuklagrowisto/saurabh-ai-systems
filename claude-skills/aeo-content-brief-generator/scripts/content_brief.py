#!/usr/bin/env python3
"""
AEO Content Brief Generator -- turns a "content" gap into a writable brief.

Third piece of the AEO/GEO loop:
  aeo-llm-visibility-audit (measure) -> aeo-geo-improvement-bot (diagnose + prioritise)
  -> aeo-content-brief-generator (this skill: turn each `content`-type fix into a brief a
     writer can execute today) -> publish -> re-run the audit to verify.

Takes the `content`-type fixes from the improvement bot (or any list of gap questions) and
returns, per question: the question shape (how-to / best-of / definition / comparison), the
matching schema type, a direct-answer opener drafted from whatever facts are supplied, the
section outline to cover, and a word-count target. No dependencies, no API keys.

Input schema:
{
  "brand": "YourBrand",
  "questions": [
    {
      "question": "how to automate outbound sales with AI",
      "facts": ["cuts manual prospecting time", "routes replies by intent"]   # optional, real proof points
    }
  ]
}

`facts`, when supplied, are woven into the answer draft verbatim -- this skill never invents
statistics or claims. When no facts are given, the draft opener is scaffolded with an explicit
`[INSERT: ...]` placeholder so nothing fabricated ships by accident.
"""
import json, re, sys

SHAPES = [
    # (matcher, shape, schema_type, sections)
    (re.compile(r"^how to\b|^how do(es)?\b", re.I), "how-to", "HowTo",
     ["Direct answer", "Step-by-step", "Common mistakes", "When to use a tool instead"]),
    (re.compile(r"\bbest\b|\btop\b|\bplatforms?\b|\btools?\b", re.I), "best-of", "ItemList",
     ["Direct answer (name the pick)", "Criteria used to judge", "Ranked list with one line each", "How to choose"]),
    (re.compile(r"\bvs\b|\bversus\b|\bcompare\b|\bcomparison\b", re.I), "comparison", "FAQPage",
     ["Direct answer (who wins, for whom)", "Side-by-side on the criteria that matter", "When to pick each"]),
    (re.compile(r"^what is\b|^what are\b|^why\b", re.I), "definition", "FAQPage",
     ["Direct answer in one sentence", "Why it matters", "Example", "Related questions"]),
]
DEFAULT_SHAPE = ("general", "FAQPage", ["Direct answer", "Supporting detail", "Example", "Related questions"])

WORD_TARGETS = {"how-to": 900, "best-of": 1100, "comparison": 800, "definition": 500, "general": 700}


def classify_shape(question):
    for matcher, shape, schema_type, sections in SHAPES:
        if matcher.search(question):
            return shape, schema_type, sections
    shape, schema_type, sections = DEFAULT_SHAPE
    return shape, schema_type, sections


def draft_opener(question, brand, facts):
    if facts:
        return f"{brand} {facts[0]}" + (f", and {', '.join(facts[1:])}." if len(facts) > 1 else ".")
    return f"[INSERT: one direct, factual sentence that answers '{question}' using {brand}'s real data -- do not publish this placeholder]"


def build_brief(brand, item):
    question = item["question"]
    facts = item.get("facts", [])
    shape, schema_type, sections = classify_shape(question)
    return {
        "question": question,
        "shape": shape,
        "recommended_schema": schema_type,
        "title_suggestion": question[0].upper() + question[1:] + (f" ({brand})" if brand.lower() not in question.lower() else ""),
        "opener_draft": draft_opener(question, brand, facts),
        "sections": sections,
        "word_count_target": WORD_TARGETS[shape],
        "facts_used": facts,
        "needs_real_data": not bool(facts),
    }


def generate(data):
    brand = data["brand"]
    questions = data["questions"]
    briefs = [build_brief(brand, q) for q in questions]
    missing_data = [b["question"] for b in briefs if b["needs_real_data"]]
    if missing_data:
        summary = (f"{len(briefs)} brief(s) drafted. {len(missing_data)} still need real facts supplied "
                   f"before the opener can be written -- see needs_real_data.")
    else:
        summary = f"{len(briefs)} brief(s) drafted, all with a fact-grounded opener ready to hand to a writer."
    return {"brand": brand, "briefs": briefs, "questions_missing_data": missing_data, "summary": summary}


# --- deterministic sample so the demo runs with no keys ---
def _sample():
    return {
        "brand": "YourBrand",
        "questions": [
            {"question": "how to automate outbound sales with AI",
             "facts": ["cuts manual prospecting time by routing replies by intent automatically"]},
            {"question": "best marketing automation platforms 2026", "facts": []},
            {"question": "what is answer engine optimisation", "facts": ["is the practice of earning citations inside AI-generated answers, not just search rankings"]},
        ],
    }


if __name__ == "__main__":
    data = json.load(open(sys.argv[1], encoding="utf-8")) if len(sys.argv) > 1 else _sample()
    print(json.dumps(generate(data), indent=2))
