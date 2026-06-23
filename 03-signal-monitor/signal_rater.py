"""
Signal Rater — daily ABM signal rating and ranked digest generator.

Reads raw signals (LinkedIn, news, funding, hiring), rates each on
relevance/persona-match/recency, and produces a Slack-style digest
of the top 3-5 for SDRs to act on today.

Usage:
    python signal_rater.py --demo
    python signal_rater.py --live
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

from shared.guardrails import guard_input, extract_json  # noqa: E402

TOP_N_FOR_DIGEST = 5


def load_prompt() -> str:
    return (HERE / "prompt.md").read_text(encoding="utf-8")


def build_user_message(signals: list[dict]) -> str:
    return (
        f"Rate the following {len(signals)} signals per the schema.\n\n"
        f"Signals:\n{json.dumps(signals, indent=2)}\n\n"
        "Return a JSON array with one object per signal in the same order."
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
        max_tokens=4096,
        system=system_prompt,
        messages=[{"role": "user", "content": user_msg}],
    )
    return response.content[0].text


def rate_signals(signals: list[dict], mode: str) -> list[dict]:
    if mode == "demo":
        return json.loads((HERE / "demo_output.json").read_text(encoding="utf-8"))

    user_msg = build_user_message(signals)
    input_guard = guard_input(user_msg, max_chars=20000)
    if not input_guard.passed:
        print(f"BLOCKED at input guardrail: {input_guard.violations}")
        sys.exit(1)

    raw = call_claude_live(load_prompt(), user_msg)
    parsed = extract_json(raw)
    if parsed is None or not isinstance(parsed, list):
        print(f"ERROR: Claude returned unparseable response. First 500 chars:\n{raw[:500]}")
        sys.exit(1)
    return parsed


def build_digest(signals: list[dict], ratings: list[dict]) -> str:
    """Build a Slack/Cliq-style markdown digest of the top N signals."""
    by_id = {s["signal_id"]: s for s in signals}
    actionable = [r for r in ratings if r.get("send_to_sdr") is True]
    actionable.sort(key=lambda r: r["relevance_0_10"], reverse=True)
    top = actionable[:TOP_N_FOR_DIGEST]

    seen_accounts = set()
    deduped = []
    for r in top:
        sig = by_id.get(r["signal_id"])
        if not sig:
            continue
        if sig["account_domain"] in seen_accounts:
            continue
        seen_accounts.add(sig["account_domain"])
        deduped.append((sig, r))

    lines = [f"# ABM Daily Digest\n\nTop {len(deduped)} actionable signals.\n\n---\n"]
    for i, (sig, r) in enumerate(deduped, 1):
        lines.append(f"## {i}. {sig['account_name']} — {sig['persona_at_account']} · Score {r['relevance_0_10']}/10\n")
        lines.append(f"**Signal:** {sig['signal_type']} ({r['recency_band']}) — {sig['signal_text'][:200]}\n")
        lines.append(f"**Why now:** {r['why_now']}\n")
        lines.append(f"**Hook:** {r['hook_angle']}\n")
        lines.append(f"**Source:** {sig['source_url']}\n\n---\n")

    filtered = [r for r in ratings if not r.get("send_to_sdr")]
    if filtered:
        lines.append("## Filtered out (not actionable today)\n")
        lines.append("| Account | Score | Reason |\n|---|---|---|\n")
        for r in filtered:
            sig = by_id.get(r["signal_id"])
            if not sig:
                continue
            reason = "persona_match: false" if not r["persona_match"] else (
                "past recency cliff" if r["recency_band"] in ("last_90d", "older") else
                "low relevance" if r["relevance_0_10"] < 7 else
                "dedup — account already in top list"
            )
            lines.append(f"| {sig['account_name']} | {r['relevance_0_10']}/10 | {reason} |\n")

    lines.append(f"\n**Run stats:** {len(signals)} signals processed · {len(deduped)} routed to SDR · {len(filtered)} filtered\n")
    return "".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["demo", "live"], default="demo")
    parser.add_argument("--demo", dest="mode", action="store_const", const="demo")
    parser.add_argument("--live", dest="mode", action="store_const", const="live")
    parser.add_argument("--input", default=str(HERE / "sample_signals.json"))
    parser.add_argument("--save", action="store_true")
    args = parser.parse_args()

    signals = json.loads(Path(args.input).read_text(encoding="utf-8"))

    print(f"\nSignal Rater — mode: {args.mode}, signals: {len(signals)}")
    print("=" * 70)

    ratings = rate_signals(signals, args.mode)

    print(f"\n{'signal_id':12s}  {'score':6s}  {'persona':8s}  {'recency':12s}  {'send':5s}")
    print("-" * 60)
    for r in ratings:
        print(f"{r['signal_id']:12s}  {r['relevance_0_10']:>4}/10  "
              f"{'yes' if r['persona_match'] else 'no':8s}  "
              f"{r['recency_band']:12s}  "
              f"{'YES' if r['send_to_sdr'] else 'no':5s}")

    digest = build_digest(signals, ratings)
    if args.save:
        out_path = HERE / "digest_today.md"
        out_path.write_text(digest, encoding="utf-8")
        print(f"\nDigest saved to {out_path}")

    print("\n" + "=" * 70)
    print("Digest preview (first 800 chars):\n")
    print(digest[:800] + ("\n... [truncated]" if len(digest) > 800 else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
