#!/usr/bin/env python3
"""
AEO / GEO Improvement Bot -- turns visibility gaps into a ranked fix plan.

Takes the output of the AEO / LLM Visibility Audit (../aeo-llm-visibility-audit)
-- the questions where a brand is invisible in AI answers -- plus a per-question
read of *why* (no owned content, no structured data, no third-party citations),
and returns a prioritised, engine-ready action plan: what to build, in what
order, and when to re-check.

This is the "close the loop" half of AEO/GEO: the audit skill finds the gap,
this skill decides the fix. No dependencies, no API keys.

Input schema:
{
  "brand": "YourBrand",
  "gap_questions": ["...", "..."],
  "signals": {                              # per gap question, what's missing
    "question text": {
      "has_owned_content": false,           # does a page on the brand's site answer this directly?
      "has_schema_markup": false,           # does that page carry FAQ/Article/Product JSON-LD?
      "third_party_mentions": 0,            # count of independent sources (review sites, Reddit, roundups) naming the brand for this
      "search_volume_proxy": 7              # 1-10, relative demand for this question
    }
  }
}

In production, `signals` is filled by a live crawl of the brand's own site
(does a page exist / does it carry schema) plus a search of third-party
sources. The demo generates a deterministic sample so the logic runs anywhere.
"""
import json, sys

FIX_ACTIONS = {
    "content": "No owned page answers this question directly. Write an answer-shaped page/section "
               "(direct answer in the first 2 sentences, then supporting detail) targeting this exact question.",
    "schema": "An owned page exists but carries no structured data. Add FAQPage/Article JSON-LD so AI "
              "crawlers can parse the answer cleanly, then resubmit for indexing.",
    "citation": "Content and schema are in place but no independent source corroborates it. Seed the "
                "answer into 2-3 third-party surfaces (Reddit thread, comparison roundup, review site) -- "
                "AI answers weight independent corroboration over owned claims.",
    "authority": "Content, schema, and citations all exist but the brand still loses the answer. The "
                 "competitor is winning on authority -- earn backlinks or citations from higher-trust "
                 "sources in this specific sub-topic.",
}

RECHECK_DAYS = {"content": 21, "schema": 7, "citation": 14, "authority": 30}


def classify(sig):
    if not sig.get("has_owned_content"):
        return "content"
    if not sig.get("has_schema_markup"):
        return "schema"
    if sig.get("third_party_mentions", 0) == 0:
        return "citation"
    return "authority"


def plan(data):
    brand = data["brand"]
    gap_questions = data["gap_questions"]
    signals = data.get("signals", {})

    fixes = []
    for q in gap_questions:
        sig = signals.get(q, {})
        fix_type = classify(sig)
        volume = sig.get("search_volume_proxy", 5)
        # cheaper fixes (schema) surface first at equal volume -- fastest path to a win
        effort_rank = {"schema": 0, "citation": 1, "content": 2, "authority": 3}[fix_type]
        priority = volume * 10 - effort_rank
        fixes.append({
            "question": q,
            "fix_type": fix_type,
            "action": FIX_ACTIONS[fix_type],
            "recheck_after_days": RECHECK_DAYS[fix_type],
            "priority": priority,
        })

    fixes.sort(key=lambda f: -f["priority"])

    fix_type_counts = {}
    for f in fixes:
        fix_type_counts[f["fix_type"]] = fix_type_counts.get(f["fix_type"], 0) + 1

    if not fixes:
        summary = "No visibility gaps supplied -- nothing to fix."
    else:
        top = fixes[0]
        summary = (f"{len(fixes)} gap question(s) to close. Start with \"{top['question']}\" "
                   f"({top['fix_type']} fix, re-check in {top['recheck_after_days']} days). "
                   f"Mix: {fix_type_counts}.")

    return {
        "brand": brand,
        "fixes": fixes,
        "fix_type_mix": fix_type_counts,
        "summary": summary,
    }


# --- deterministic sample so the demo runs with no keys ---
def _sample():
    brand = "YourBrand"
    gap_questions = [
        "tools to make my brand discoverable in AI search",
        "how to automate outbound sales with AI",
        "best marketing automation platforms 2026",
    ]
    # Deterministic per-question signal spread, mirrors the pattern used by aeo_score.py's sample generator.
    signals = {}
    for i, q in enumerate(gap_questions):
        signals[q] = {
            "has_owned_content": i % 3 != 0,
            "has_schema_markup": i % 3 == 2,
            "third_party_mentions": [0, 1, 0][i % 3],
            "search_volume_proxy": [8, 6, 9][i % 3],
        }
    return {"brand": brand, "gap_questions": gap_questions, "signals": signals}


if __name__ == "__main__":
    data = json.load(open(sys.argv[1], encoding="utf-8")) if len(sys.argv) > 1 else _sample()
    print(json.dumps(plan(data), indent=2))
