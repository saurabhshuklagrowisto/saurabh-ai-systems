# How to Run

## Prerequisites

- Python 3.10 or newer
- Optional: an Anthropic API key (only for `--live` mode)

## Demo mode (no API key)

Every workflow has a `--demo` flag that replays pre-recorded Claude outputs. Useful for:

- Showing the system to someone without spending API credits
- Running in CI / offline
- Iterating on the eval harness without re-calling the model

```bash
python claude-skills/reply-triage-agent/reply_triage.py --demo
python claude-skills/signal-monitor/signal_rater.py --demo
python claude-skills/meeting-brief/meeting_brief.py --demo
```

Output appears on stdout. Add `--save` to write the rendered Markdown or JSON to disk.

## Live mode (with Claude API)

```bash
pip install anthropic

# macOS / Linux
export ANTHROPIC_API_KEY="sk-ant-..."

# Windows PowerShell
$env:ANTHROPIC_API_KEY = "sk-ant-..."

# Run any workflow live
python claude-skills/reply-triage-agent/reply_triage.py --live
```

The model used is `claude-sonnet-4-6`. Adjust in each agent's `call_claude_live()` function if you want to try a different tier.

## Running the eval

The reply-triage workflow ships with a regression-gate eval harness:

```bash
# Should PASS (exit 0)
python claude-skills/reply-triage-agent/eval.py

# Should FAIL (exit 1) — demonstrates the gate catches critical safety violations
python claude-skills/reply-triage-agent/eval.py --outputs claude-skills/reply-triage-agent/broken_output.json

# Save a Markdown report
python claude-skills/reply-triage-agent/eval.py --save

# Machine-readable JSON (for CI consumption)
python claude-skills/reply-triage-agent/eval.py --json
```

Exit code is the contract: 0 = thresholds met, 1 = at least one threshold or critical-safety rule failed.

## Running the ABM Skill eval

```bash
python claude-skills/abm-account-brief-skill/scripts/score_output.py --verbose
```

Same pattern, different metric set (schema validity, evidence grounding, hook diversity, length compliance, LLM-as-judge quality).

## Windows-specific note

If you see character encoding warnings (em-dashes rendering as `?`), set:

```powershell
$env:PYTHONIOENCODING = "utf-8"
```

The agents try to reconfigure stdout to UTF-8 automatically; this is a belt-and-braces fix.

## CI integration

To use the eval as a pre-promote gate on prompt changes, add a step to your CI:

```yaml
# .github/workflows/eval.yml example
- name: Run reply-triage eval
  run: python claude-skills/reply-triage-agent/eval.py

- name: Run ABM Skill eval
  run: python claude-skills/abm-account-brief-skill/scripts/score_output.py
```

A non-zero exit blocks merge. That's the entire CI gate.
