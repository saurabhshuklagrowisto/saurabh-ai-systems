"""
Reply Triage Eval Harness — regression-tests agent outputs against a
human-labeled golden set. Returns non-zero exit if any threshold fails,
so this can sit in CI as a pre-promote gate on prompt changes.

Scoring dimensions:
  1. intent_accuracy      — exact match on `intent`         (threshold 0.85)
  2. action_accuracy      — exact match on `suggested_action` (threshold 0.85)
  3. schema_validity      — required keys present, types correct (threshold 1.0)
  4. critical_safety      — zero catastrophic errors        (threshold 1.0, hard)
  5. confidence_calibration — high-conf cases correct >= 0.95 (threshold 0.95)

Usage:
    python eval.py                              # scores demo_output.json vs golden_set.json
    python eval.py --outputs results.json       # custom outputs file
    python eval.py --save                       # writes eval_report.md
    python eval.py --json                       # machine-readable JSON output
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = Path(__file__).parent

THRESHOLDS = {
    "intent_accuracy": 0.85,
    "action_accuracy": 0.85,
    "schema_validity": 1.0,
    "critical_safety": 1.0,
    "confidence_calibration": 0.95,
}

REQUIRED_OUTPUT_KEYS = {
    "intent", "sentiment", "confidence", "suggested_action",
    "draft_reply", "crm_update", "reasoning",
}

VALID_INTENTS = {
    "positive", "objection", "interested_later", "wrong_person",
    "out_of_office", "unsubscribe", "other",
}

VALID_ACTIONS = {"auto_reply", "human_review", "crm_update_only", "suppress"}


def check_schema(output: dict) -> tuple[bool, list[str]]:
    violations = []
    missing = REQUIRED_OUTPUT_KEYS - set(output.keys())
    if missing:
        violations.append(f"missing_keys: {sorted(missing)}")
    if output.get("intent") not in VALID_INTENTS:
        violations.append(f"invalid_intent: {output.get('intent')}")
    if output.get("suggested_action") not in VALID_ACTIONS:
        violations.append(f"invalid_action: {output.get('suggested_action')}")
    conf = output.get("confidence")
    if not isinstance(conf, (int, float)) or not (0 <= conf <= 10):
        violations.append(f"invalid_confidence: {conf}")
    crm = output.get("crm_update", {})
    if not isinstance(crm, dict) or "stage" not in crm:
        violations.append("malformed_crm_update")
    return len(violations) == 0, violations


def check_critical_safety(output: dict, label: dict) -> list[str]:
    """Zero-tolerance rules. Any violation here = fail the gate."""
    violations = []
    intent = output.get("intent")
    action = output.get("suggested_action")
    draft = output.get("draft_reply")
    confidence = output.get("confidence", 0)

    # Rule A: Unsubscribe must never get a draft or auto_reply
    if intent == "unsubscribe" or label["intent"] == "unsubscribe":
        if action == "auto_reply":
            violations.append("CRITICAL: auto_reply on unsubscribe intent")
        if draft is not None:
            violations.append("CRITICAL: generated draft_reply for unsubscribe")

    # Rule B: Confidence below 7 must route to human_review
    if isinstance(confidence, (int, float)) and confidence < 7 and action == "auto_reply":
        violations.append(f"CRITICAL: auto_reply at confidence {confidence} < 7")

    # Rule C: Objection must route to human_review
    if label["intent"] == "objection" and action == "auto_reply":
        violations.append("CRITICAL: auto_reply on objection")

    # Rule D: must_draft_reply=false in label means draft_reply MUST be null
    if label.get("must_draft_reply") is False and draft not in (None, ""):
        violations.append("CRITICAL: generated draft when label says no draft required")

    return violations


def score_case(output: dict, label: dict) -> dict:
    intent_correct = output.get("intent") == label["intent"]
    action_correct = output.get("suggested_action") == label["suggested_action"]
    schema_ok, schema_violations = check_schema(output)
    safety_violations = check_critical_safety(output, label)
    confidence = output.get("confidence", 0)
    is_high_conf = isinstance(confidence, (int, float)) and confidence >= 8

    return {
        "input_id": label["input_id"],
        "intent_correct": intent_correct,
        "action_correct": action_correct,
        "schema_ok": schema_ok,
        "schema_violations": schema_violations,
        "safety_violations": safety_violations,
        "confidence": confidence,
        "is_high_conf": is_high_conf,
        "predicted_intent": output.get("intent"),
        "expected_intent": label["intent"],
        "predicted_action": output.get("suggested_action"),
        "expected_action": label["suggested_action"],
    }


def aggregate(scored: list[dict]) -> dict:
    n = len(scored)
    if n == 0:
        return {"error": "no cases scored"}

    high_conf_cases = [s for s in scored if s["is_high_conf"]]

    metrics = {
        "intent_accuracy": sum(1 for s in scored if s["intent_correct"]) / n,
        "action_accuracy": sum(1 for s in scored if s["action_correct"]) / n,
        "schema_validity": sum(1 for s in scored if s["schema_ok"]) / n,
        "critical_safety": sum(1 for s in scored if not s["safety_violations"]) / n,
        "confidence_calibration": (
            sum(1 for s in high_conf_cases if s["intent_correct"]) / len(high_conf_cases)
            if high_conf_cases else 1.0
        ),
    }
    return metrics


def render_report(scored: list[dict], metrics: dict, failed: list[str]) -> str:
    lines = [
        "# Reply Triage Eval Report\n",
        f"\n**Cases scored:** {len(scored)}\n",
        f"**Status:** {'PASS' if not failed else 'FAIL (' + ', '.join(failed) + ')'}\n\n",
        "## Metric summary\n\n",
        "| Metric | Threshold | Actual | Status |\n",
        "|---|---|---|---|\n",
    ]
    for metric, threshold in THRESHOLDS.items():
        actual = metrics.get(metric, 0.0)
        status = "PASS" if actual >= threshold else "FAIL"
        lines.append(f"| {metric} | {threshold:.2f} | {actual:.2f} | {status} |\n")

    lines.append("\n## Per-case results\n\n")
    lines.append("| Case | Intent (pred → exp) | Action (pred → exp) | Schema | Safety | Conf |\n")
    lines.append("|---|---|---|---|---|---|\n")
    for s in scored:
        intent_cell = f"{s['predicted_intent']} → {s['expected_intent']}" + (" OK" if s["intent_correct"] else " WRONG")
        action_cell = f"{s['predicted_action']} → {s['expected_action']}" + (" OK" if s["action_correct"] else " WRONG")
        schema_cell = "OK" if s["schema_ok"] else f"FAIL: {s['schema_violations']}"
        safety_cell = "OK" if not s["safety_violations"] else f"FAIL: {s['safety_violations']}"
        lines.append(
            f"| {s['input_id']} | {intent_cell} | {action_cell} | {schema_cell} | {safety_cell} | {s['confidence']} |\n"
        )

    if any(s["safety_violations"] for s in scored):
        lines.append("\n## Critical safety violations (any single one blocks promote)\n\n")
        for s in scored:
            for v in s["safety_violations"]:
                lines.append(f"- [{s['input_id']}] {v}\n")

    return "".join(lines)


def load_outputs(path: Path) -> dict[str, dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return {item["input_id"]: item.get("output", item) for item in data}
    if isinstance(data, dict) and "results" in data:
        return {item["input_id"]: item.get("output", item) for item in data["results"]}
    raise ValueError(f"unrecognized output format in {path}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--outputs", default=str(HERE / "demo_output.json"))
    parser.add_argument("--golden", default=str(HERE / "golden_set.json"))
    parser.add_argument("--save", action="store_true", help="write eval_report.md")
    parser.add_argument("--json", action="store_true", help="machine-readable JSON output")
    args = parser.parse_args()

    golden = json.loads(Path(args.golden).read_text(encoding="utf-8"))["labels"]
    outputs = load_outputs(Path(args.outputs))

    scored = []
    for label in golden:
        agent_output = outputs.get(label["input_id"])
        if not agent_output:
            print(f"WARN: no agent output for {label['input_id']}, skipping")
            continue
        scored.append(score_case(agent_output, label))

    metrics = aggregate(scored)
    failed = [m for m, t in THRESHOLDS.items() if metrics.get(m, 0.0) < t]

    if args.json:
        print(json.dumps({"metrics": metrics, "failed": failed, "cases": scored}, indent=2))
        return 1 if failed else 0

    report = render_report(scored, metrics, failed)
    print(report)

    if args.save:
        out_path = HERE / "eval_report.md"
        out_path.write_text(report, encoding="utf-8")
        print(f"\nReport saved to {out_path}")

    if failed:
        print(f"\nBLOCKED — {len(failed)} metric(s) below threshold: {failed}")
        print("Prompt change is NOT safe to promote until these regress.")
        return 1

    print("\nALL THRESHOLDS PASS — prompt change is safe to promote.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
