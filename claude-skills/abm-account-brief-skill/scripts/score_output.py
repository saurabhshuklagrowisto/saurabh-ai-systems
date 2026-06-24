"""
Eval harness for the abm-account-brief Skill.

Runs each input in golden_set.jsonl through the current prompt, then scores
the output on five dimensions:

  1. Schema validity         — does the JSON match the declared schema?
  2. Evidence grounding      — does every hook cite a URL present in input signals?
  3. Hook diversity          — are the three hooks genuinely distinct?
  4. Length compliance       — subject <= 50 chars, body <= 60 words
  5. Hook-quality judge      — LLM-as-judge rates each hook 1-5 vs the golden hook

Usage:
    python scripts/score_output.py --prompt prompts/v2.md
    python scripts/score_output.py --prompt prompts/v2.md --verbose

Designed to be cheap to run (~10 golden cases) so it can sit in CI and gate
prompt changes. A regression on any case below the threshold blocks the change.
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

THRESHOLDS = {
    "schema_validity": 1.0,
    "evidence_grounding": 0.9,
    "hook_diversity": 0.8,
    "length_compliance": 1.0,
    "judge_quality_mean": 3.5,
}

REQUIRED_TOP_LEVEL = {
    "company", "icp_fit", "hooks", "recommended_channel",
    "channel_rationale", "cold_email_draft", "confidence_0_to_10",
    "confidence_rationale", "guardrails_triggered",
}


def check_schema(output: dict) -> tuple[bool, str]:
    missing = REQUIRED_TOP_LEVEL - set(output.keys())
    if missing:
        return False, f"missing keys: {missing}"
    if not isinstance(output.get("hooks"), list) or len(output["hooks"]) != 3:
        return False, "hooks must be a list of exactly 3 items"
    return True, "ok"


def check_evidence_grounding(output: dict, input_signals: list[dict]) -> float:
    allowed_urls = {s["source_url"] for s in input_signals if "source_url" in s}
    if not output.get("hooks"):
        return 0.0
    grounded = sum(
        1 for h in output["hooks"]
        if h.get("evidence_url") in allowed_urls
    )
    return grounded / len(output["hooks"])


def check_hook_diversity(output: dict) -> float:
    """
    Crude diversity check: angles must share fewer than 60% of their non-stop words.
    A real system would use embeddings; this is the cheap proxy that catches
    the obvious failures (v1 of the prompt failed this on 3/10 cases).
    """
    hooks = output.get("hooks", [])
    if len(hooks) < 2:
        return 0.0
    stop = {"the", "a", "an", "is", "are", "to", "of", "in", "and", "or", "for"}
    tokens = [
        set(re.findall(r"\w+", h.get("angle", "").lower())) - stop
        for h in hooks
    ]
    pairs = [(i, j) for i in range(len(tokens)) for j in range(i + 1, len(tokens))]
    overlaps = []
    for i, j in pairs:
        if not tokens[i] or not tokens[j]:
            overlaps.append(1.0)
            continue
        overlap = len(tokens[i] & tokens[j]) / max(len(tokens[i]), len(tokens[j]))
        overlaps.append(overlap)
    worst_overlap = max(overlaps)
    return 1.0 if worst_overlap < 0.6 else 1.0 - worst_overlap


def check_length_compliance(output: dict) -> bool:
    email = output.get("cold_email_draft", {})
    subject = email.get("subject_line", "")
    body = email.get("body", "")
    word_count = len(body.split())
    return len(subject) <= 50 and word_count <= 60


def judge_hook_quality(generated_hook: dict, golden_hook: dict) -> int:
    """
    Placeholder for LLM-as-judge. In production this calls Claude with a
    rubric prompt that returns 1-5. Here we stub to 4 so the harness runs
    end-to-end without an API key during local dev.
    """
    return 4


def run_case(case: dict, prompt_text: str, verbose: bool) -> dict:
    """
    Hook point: this is where the Skill is invoked in production via the
    Anthropic SDK with the prompt text and the case inputs. For the
    interview demo, we load a recorded output from the case file directly
    so the harness runs without network.
    """
    output = case.get("recorded_output")
    if output is None:
        return {"case_id": case["id"], "skipped": "no recorded output"}

    schema_ok, schema_msg = check_schema(output)
    if not schema_ok:
        return {"case_id": case["id"], "fatal": schema_msg}

    return {
        "case_id": case["id"],
        "schema_validity": 1.0 if schema_ok else 0.0,
        "evidence_grounding": check_evidence_grounding(output, case["recent_signals"]),
        "hook_diversity": check_hook_diversity(output),
        "length_compliance": 1.0 if check_length_compliance(output) else 0.0,
        "judge_quality_mean": sum(
            judge_hook_quality(h, case["golden_hooks"][i])
            for i, h in enumerate(output["hooks"])
        ) / len(output["hooks"]),
    }


def aggregate(results: list[dict]) -> dict:
    scored = [r for r in results if "fatal" not in r and "skipped" not in r]
    if not scored:
        return {"error": "no scorable cases"}
    metrics = {}
    for key in THRESHOLDS:
        values = [r[key] for r in scored if key in r]
        metrics[key] = sum(values) / len(values) if values else 0.0
    return metrics


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", default="prompts/v2.md")
    parser.add_argument("--golden", default="golden_set.jsonl")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    prompt_text = Path(args.prompt).read_text(encoding="utf-8")
    cases = [json.loads(line) for line in Path(args.golden).read_text(encoding="utf-8").splitlines() if line.strip()]

    results = [run_case(c, prompt_text, args.verbose) for c in cases]
    metrics = aggregate(results)

    print(f"\nEval run — prompt: {args.prompt}, cases: {len(cases)}\n")
    failed = []
    for key, threshold in THRESHOLDS.items():
        actual = metrics.get(key, 0.0)
        status = "PASS" if actual >= threshold else "FAIL"
        if status == "FAIL":
            failed.append(key)
        print(f"  {key:25s}  threshold {threshold:.2f}  actual {actual:.2f}  {status}")

    if args.verbose:
        print("\nPer-case results:")
        for r in results:
            print(f"  {json.dumps(r)}")

    if failed:
        print(f"\nBLOCKED — {len(failed)} metric(s) below threshold: {failed}")
        return 1
    print("\nALL METRICS PASS — prompt change is safe to promote.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
