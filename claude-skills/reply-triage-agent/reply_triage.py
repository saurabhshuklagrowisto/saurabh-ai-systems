"""
Reply Triage Agent — classifies inbound replies and decides routing.

Usage:
    python reply_triage.py --demo                # replays demo_output.json
    python reply_triage.py --live                # calls Claude API (needs ANTHROPIC_API_KEY)
    python reply_triage.py --live --input X.json # custom input file
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent))

from shared.guardrails import guard_input, guard_output, extract_json  # noqa: E402

REQUIRED_OUTPUT_KEYS = {"intent", "sentiment", "confidence", "suggested_action", "draft_reply", "crm_update", "reasoning"}


def load_prompt() -> str:
    return (HERE / "prompt.md").read_text(encoding="utf-8")


def build_user_message(reply: dict) -> str:
    return (
        f"Reply ID: {reply['id']}\n"
        f"From: {reply['from']}\n"
        f"Subject: {reply['subject']}\n"
        f"Campaign: {reply['context']['campaign']}\n"
        f"Previous touches: {reply['context']['previous_touches']}\n"
        f"Last touch days ago: {reply['context']['last_touch_days_ago']}\n\n"
        f"--- Reply body ---\n{reply['body']}\n--- End body ---\n\n"
        f"Classify per the schema. Return JSON only."
    )


def call_claude_live(system_prompt: str, user_msg: str) -> str:
    try:
        from anthropic import Anthropic
    except ImportError:
        print("ERROR: anthropic SDK not installed. Run: pip install anthropic")
        sys.exit(1)

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY env var not set")
        sys.exit(1)

    client = Anthropic(api_key=api_key)
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=system_prompt,
        messages=[{"role": "user", "content": user_msg}],
    )
    return response.content[0].text


def triage_one(reply: dict, mode: str, demo_lookup: dict) -> dict:
    user_msg = build_user_message(reply)

    input_guard = guard_input(user_msg)
    if not input_guard.passed:
        return {
            "input_id": reply["id"],
            "blocked_at": "input_guardrail",
            "violations": input_guard.violations,
        }

    if mode == "demo":
        cached = demo_lookup.get(reply["id"])
        if not cached:
            return {"input_id": reply["id"], "error": "no demo output recorded for this id"}
        output = cached["output"]
    else:
        raw = call_claude_live(load_prompt(), user_msg)
        output = extract_json(raw)
        if output is None:
            return {"input_id": reply["id"], "error": "claude returned unparseable response", "raw": raw[:500]}

    output_guard = guard_output(
        output,
        required_keys=REQUIRED_OUTPUT_KEYS,
        text_fields_to_scan=["draft_reply"] if output.get("draft_reply") else [],
        confidence_threshold=7,
    )

    return {
        "input_id": reply["id"],
        "output": output,
        "guardrails_triggered": output_guard.violations,
        "input_guardrails": [v for v in input_guard.violations if "pii_scrubbed" in v],
    }


def print_result(result: dict) -> None:
    if "error" in result:
        print(f"\n[{result['input_id']}] ERROR — {result['error']}")
        return
    if "blocked_at" in result:
        print(f"\n[{result['input_id']}] BLOCKED at {result['blocked_at']}: {result['violations']}")
        return

    out = result["output"]
    print(f"\n[{result['input_id']}]")
    print(f"  intent              {out['intent']}")
    print(f"  confidence          {out['confidence']}/10")
    print(f"  suggested_action    {out['suggested_action']}")
    print(f"  crm.stage           {out['crm_update']['stage']}")
    print(f"  crm.next_follow_up  {out['crm_update']['next_follow_up_days']} days")
    print(f"  reasoning           {out['reasoning']}")
    if out.get("draft_reply"):
        print(f"  draft               {out['draft_reply'][:120]}...")
    if result["guardrails_triggered"]:
        print(f"  guardrails          {result['guardrails_triggered']}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["demo", "live"], default="demo")
    parser.add_argument("--demo", dest="mode", action="store_const", const="demo")
    parser.add_argument("--live", dest="mode", action="store_const", const="live")
    parser.add_argument("--input", default=str(HERE / "sample_replies.json"))
    parser.add_argument("--save", action="store_true", help="save results to results.json")
    args = parser.parse_args()

    replies = json.loads(Path(args.input).read_text(encoding="utf-8"))
    demo_lookup = {}
    demo_path = HERE / "demo_output.json"
    if demo_path.exists():
        demo_data = json.loads(demo_path.read_text(encoding="utf-8"))
        demo_lookup = {item["input_id"]: item for item in demo_data}

    print(f"\nReply Triage Agent — mode: {args.mode}, replies: {len(replies)}")
    print("=" * 70)

    results = []
    for reply in replies:
        result = triage_one(reply, args.mode, demo_lookup)
        results.append(result)
        print_result(result)

    summary = {}
    for r in results:
        if "output" in r:
            action = r["output"]["suggested_action"]
            summary[action] = summary.get(action, 0) + 1

    print("\n" + "=" * 70)
    print("Routing summary:")
    for action, count in sorted(summary.items()):
        print(f"  {action:25s} {count}")

    if args.save:
        out_path = HERE / "results.json"
        out_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
        print(f"\nResults saved to {out_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
