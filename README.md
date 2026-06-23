# AI Sales & Marketing Systems

Production-shaped Claude agents and the eval, guardrail, and orchestration patterns behind them. Each system in this repo runs end-to-end without an API key — clone, `python <agent>.py --demo`, see real output in under a second.

I architect and ship Claude systems for sales and marketing at [Growisto](https://growisto.com). The full production system — a multi-MCP fabric over Zoho CRM, Google Drive, our internal Wiki, Fireflies, Apollo, and n8n, wired by a canonical account ID and a per-account Claude project pattern — lives in a separate plan repo. **This repo is the standalone, runnable proof of the patterns inside that system.**

---

## What's here

| # | System | What it proves | One-line demo |
|---|---|---|---|
| [01](./01-abm-account-brief-skill) | **ABM Account Brief Skill** | Reusable Claude Skill, ICP gate, evidence grounding, prompt versioning | `python 01-abm-account-brief-skill/scripts/score_output.py` |
| [02](./02-reply-triage-agent) | **Reply Triage Agent** | Smartlead → Claude → CRM. Schema-first, regression-gated, n8n-deployable | `python 02-reply-triage-agent/reply_triage.py --demo` |
| [03](./03-signal-monitor) | **Signal Monitor** | Daily ABM digest. The Sales Copilot pattern — signal capture, persona match, recency cliff | `python 03-signal-monitor/signal_rater.py --demo` |
| [04](./04-meeting-brief) | **Pre-Meeting Brief Generator** | Identity resolution + CRM context + signals → one-page brief 30 min before the call | `python 04-meeting-brief/meeting_brief.py --demo` |
| — | **[Eval & Guardrail Harness](./02-reply-triage-agent/eval.py)** | Threshold-gated CI eval that BLOCKS promote when critical safety rules are violated | `python 02-reply-triage-agent/eval.py` |

---

## Why this repo exists

Most "AI demos" are screenshots and prompts. Real production systems need five things this repo demonstrates concretely:

1. **A schema** — every output is JSON, every field has a contract, malformed = dead-letter
2. **Guardrails as code** — PII scrub, banned phrases, confidence thresholds enforced before output reaches a human or a CRM
3. **An eval harness** — golden set + critical-safety rules + thresholds; CI blocks promote if any metric regresses
4. **Prompt versioning** — v1 deprecated with documented reason, v2 in production, v3 must pass the eval before promote
5. **Orchestration thinking** — every agent is one node in a routing graph; demos include n8n workflow exports

If your system has these, you ship. If it doesn't, every change becomes an incident.

---

## 30-second quickstart

```bash
git clone <this-repo-url>
cd saurabh-ai-systems
python --version              # 3.10+ required

# Run any demo (no API key needed — replays recorded outputs)
python 02-reply-triage-agent/reply_triage.py --demo
python 03-signal-monitor/signal_rater.py --demo
python 04-meeting-brief/meeting_brief.py --demo

# Run the eval (proves the regression gate works)
python 02-reply-triage-agent/eval.py
python 02-reply-triage-agent/eval.py --outputs 02-reply-triage-agent/broken_output.json
# ^ exits 1; shows you exactly which critical safety rules were violated

# Run live against Claude API
pip install anthropic
export ANTHROPIC_API_KEY="sk-ant-..."          # macOS/Linux
$env:ANTHROPIC_API_KEY = "sk-ant-..."          # PowerShell
python 02-reply-triage-agent/reply_triage.py --live
```

If you're on Windows and see encoding warnings, set `$env:PYTHONIOENCODING = "utf-8"` once per session.

---

## The patterns this repo demonstrates

### Schema-first agents
Every prompt declares an output schema. The agent code validates against `REQUIRED_OUTPUT_KEYS` before passing anything downstream. Malformed JSON goes to a dead-letter queue, not into a customer's inbox.

### Critical-safety rules (zero-tolerance gates)
The reply-triage eval enforces hard rules that override threshold-based scoring:
- Never auto-reply to an unsubscribe (compliance incident)
- Never auto-reply on a competitive objection (relationship incident)
- Never auto-reply when confidence < 7 (the explicit prompt rule)
- Never generate a draft when the label says "no draft required"

Any single violation in any single case fails the entire promote gate. Try it: `python 02-reply-triage-agent/eval.py --outputs 02-reply-triage-agent/broken_output.json`.

### Golden-set evals + regression gates
Each workflow ships with a hand-labeled golden set. The eval harness scores:
- Schema validity (binary)
- Intent / classification accuracy (exact match)
- Action routing accuracy
- Critical safety (zero-tolerance, see above)
- Confidence calibration (high-confidence cases must be correct ≥ 95%)

Below threshold → exit 1 → prompt change cannot be promoted. Same pattern that lets engineering teams ship to production without paging someone every night.

### Prompt versioning
`prompts/v1.md` exists alongside `prompts/v2.md` with a documented reason for deprecation. v2 was promoted only after passing the golden set. v3 (in development) must pass the same gate.

### Shared guardrail layer
`shared/guardrails.py` is consumed by every workflow. Same module enforces PII scrubbing, banned-phrase detection, schema validation, and prompt-injection detection. Centralizing this is what makes scale possible — change the rule once, every agent gets the update.

### n8n-deployable
The Python script and the n8n workflow are two surfaces over the same logic. See `02-reply-triage-agent/n8n-workflow.json` — importable into any n8n instance, wires Smartlead webhook → Claude → router → Zoho update + Slack review queue.

---

## Stack

- **Models:** Claude (Sonnet 4.6) via Anthropic SDK
- **Languages:** Python 3.10+ (agents, evals), JavaScript (n8n nodes), Markdown / YAML (prompts, configs)
- **Orchestration:** n8n (in production), Anthropic SDK direct, Zoho Flow
- **Data plane:** Zoho CRM, Google Drive, Smartlead, Apollo, Clay, LinkedIn Sales Navigator
- **Eval / Quality:** Custom harness in this repo, BigQuery for production logs, LLM-as-judge for subjective quality

---

## How this maps to a Marketing Engineering Lead role

| JD-shape ask | Where in this repo |
|---|---|
| "Library of reusable Claude skills" | [01-abm-account-brief-skill](./01-abm-account-brief-skill) |
| "Agentic layer over CRM data fabric" | [02-reply-triage-agent](./02-reply-triage-agent) — Smartlead ↔ Claude ↔ Zoho |
| "Sales Copilot — signal capture across operational systems" | [03-signal-monitor](./03-signal-monitor) + [04-meeting-brief](./04-meeting-brief) |
| "Eval and guardrail layer under everything" | [02-reply-triage-agent/eval.py](./02-reply-triage-agent/eval.py) + [shared/guardrails.py](./shared/guardrails.py) |
| "Low-code agent platforms (n8n, Zapier AI)" | [n8n-workflow.json](./02-reply-triage-agent/n8n-workflow.json) |
| "Internal tooling — prototypes that become production tools" | Whole repo. Every workflow has a `--live` mode. |

---

## Honest scope

This repo is **scoped-down packaging** of patterns that run in production via n8n + Zoho + Smartlead at Growisto. The standalone scripts let you see the reasoning, guardrails, and eval shape cleanly — without the full production wiring. The bigger system architecture (canonical Account ID + multi-MCP fabric + per-account Claude project pattern) is documented in a separate plan repo.

**What's real:** the prompts, the guardrails, the schema design, the eval rubric, the routing logic.
**What's scoped:** the integrations (mock outputs replace live Smartlead/Apollo/Zoho calls in `--demo` mode).
**What's next:** wiring this same harness into the production system's CI so prompt changes are gated automatically.

---

## License

MIT — fork it, study it, adapt it. Attribution appreciated, not required.

## About

**Saurabh Shukla** — AI systems architect, sales & marketing | Mumbai | [LinkedIn](https://linkedin.com/in/shivsaurabh) | officialsaurabhshukla@gmail.com
