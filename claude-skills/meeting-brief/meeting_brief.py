"""
Pre-Meeting Brief Generator — the Sales Copilot analog.

Reads the meeting metadata, matched CRM record, recent signals, and persona
pain themes. Generates a one-page brief the AE reads 90 seconds before
the call.

Usage:
    python meeting_brief.py --demo
    python meeting_brief.py --live --input sample_meeting.json
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent))

from shared.guardrails import guard_output, extract_json  # noqa: E402

REQUIRED_KEYS = {
    "meeting", "context_summary", "recent_signals_relevant",
    "talking_points", "one_risk_or_objection", "one_question_to_ask",
    "do_not_say", "confidence", "data_freshness_warnings",
}


def load_prompt() -> str:
    return (HERE / "prompt.md").read_text(encoding="utf-8")


def days_old(iso_date: str, reference: datetime | None = None) -> int:
    ref = reference or datetime(2026, 6, 23)
    try:
        d = datetime.fromisoformat(iso_date.replace("Z", "+00:00"))
        if d.tzinfo is not None:
            d = d.replace(tzinfo=None)
        return (ref - d).days
    except ValueError:
        return 999


def add_freshness_warnings(brief: dict, signals: list[dict]) -> dict:
    warnings = list(brief.get("data_freshness_warnings", []))
    for sig in signals:
        age = days_old(sig.get("date", ""))
        if age > 30:
            warnings.append(f"Signal from {sig.get('date')} is {age} days old — older than 30-day window")
    if warnings:
        brief["data_freshness_warnings"] = warnings
    return brief


def build_user_message(meeting_data: dict) -> str:
    return (
        "Generate a pre-meeting brief from the following input. Output JSON only, "
        "matching the schema. Apply hard rules in the prompt.\n\n"
        f"{json.dumps(meeting_data, indent=2)}"
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
        max_tokens=2048,
        system=system_prompt,
        messages=[{"role": "user", "content": user_msg}],
    )
    return response.content[0].text


def generate_brief(meeting_data: dict, mode: str) -> dict:
    if mode == "demo":
        brief = json.loads((HERE / "demo_output.json").read_text(encoding="utf-8"))
    else:
        user_msg = build_user_message(meeting_data)
        raw = call_claude_live(load_prompt(), user_msg)
        parsed = extract_json(raw)
        if parsed is None:
            print(f"ERROR: unparseable response. First 500 chars:\n{raw[:500]}")
            sys.exit(1)
        brief = parsed

    brief = add_freshness_warnings(brief, meeting_data.get("recent_signals", []))

    guard_result = guard_output(
        brief,
        required_keys=REQUIRED_KEYS,
        text_fields_to_scan=["context_summary", "one_question_to_ask"],
        confidence_threshold=6,
    )
    brief["_guardrails"] = guard_result.violations
    return brief


def render_markdown(brief: dict, meeting_data: dict) -> str:
    m = brief["meeting"]
    crm_conf = max(
        (a["crm_match_confidence"] for a in meeting_data["meeting"]["attendees"] if a["external"]),
        default=0.0,
    )
    lines = [
        f"# Pre-Meeting Brief — {m['with']} · {m['company']}\n",
        f"**Meeting:** {m['time']} · {m['purpose_one_line']}\n",
        f"**CRM match confidence:** {crm_conf:.2f} · **Brief confidence:** {brief['confidence']}/10\n\n",
        "---\n\n## Where this account stands today\n\n",
        brief["context_summary"] + "\n\n## Signals that matter\n\n",
        "| Date | Signal | Implication |\n|---|---|---|\n",
    ]
    for s in brief["recent_signals_relevant"]:
        lines.append(f"| {s['date']} | {s['signal']} | {s['implication_for_meeting']} |\n")
    lines.append("\n## 3 talking points\n\n")
    for i, tp in enumerate(brief["talking_points"], 1):
        lines.append(f"{i}. {tp}\n")
    lines.append("\n## Risk to handle\n\n")
    risk = brief["one_risk_or_objection"]
    lines.append(f"**Risk:** {risk['risk']}\n\n**How to handle:** {risk['how_to_handle']}\n\n")
    lines.append(f"## Question to ask\n\n> {brief['one_question_to_ask']}\n\n")
    lines.append("## Do not say\n\n")
    for dn in brief["do_not_say"]:
        lines.append(f"- {dn}\n")
    if brief.get("data_freshness_warnings"):
        lines.append("\n## ⚠ Data freshness warnings\n\n")
        for w in brief["data_freshness_warnings"]:
            lines.append(f"- {w}\n")
    if brief.get("_guardrails"):
        lines.append("\n## Guardrails triggered\n\n")
        for v in brief["_guardrails"]:
            lines.append(f"- {v}\n")
    return "".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["demo", "live"], default="demo")
    parser.add_argument("--demo", dest="mode", action="store_const", const="demo")
    parser.add_argument("--live", dest="mode", action="store_const", const="live")
    parser.add_argument("--input", default=str(HERE / "sample_meeting.json"))
    parser.add_argument("--save", action="store_true")
    args = parser.parse_args()

    meeting_data = json.loads(Path(args.input).read_text(encoding="utf-8"))

    print(f"\nMeeting Brief Generator — mode: {args.mode}")
    print("=" * 70)

    brief = generate_brief(meeting_data, args.mode)
    md = render_markdown(brief, meeting_data)
    print(md)

    if args.save:
        out_path = HERE / "generated_brief.md"
        out_path.write_text(md, encoding="utf-8")
        print(f"\nBrief saved to {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
