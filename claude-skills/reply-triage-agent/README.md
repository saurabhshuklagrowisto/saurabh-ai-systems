# Reply Triage Agent

Classifies inbound replies to cold outreach and decides routing: auto-draft plus human approval, full human review, CRM update only, or suppression. Ships with a golden-set eval that blocks promote when critical safety rules are violated.

## What it does

Trigger: a reply lands in your cold-email tool (in production: Sendy webhook; sample payloads here use the common Smartlead/Lemlist shape so the agent is portable).
Action: Claude classifies the reply (intent, sentiment, confidence) and decides one of four routes:
- `auto_reply` · draft for AE one-click send
- `human_review` · escalate to AE, no draft
- `crm_update_only` · silent CRM update, no outbound
- `suppress` · unsubscribe / opt-out, immediate suppression

The agent never auto-sends. The closest thing to autonomy is "draft for AE one-click approval." Customer-facing sends require a human.

## What it proves

- **Schema-first** · every output validated against `REQUIRED_OUTPUT_KEYS`
- **Critical-safety rules** · zero-tolerance gates that override any threshold scoring (never auto-reply to unsubscribe, never auto-reply at confidence below 7)
- **Regression-gated eval** · golden set plus 5 metrics plus CI exit code
- **n8n-deployable** · same logic exported as an importable workflow

## How to run

```bash
# Demo. replays recorded outputs
python reply_triage.py --demo

# Eval against golden set (should pass)
python eval.py

# Eval against deliberately broken output (should fail, proves the gate works)
python eval.py --outputs broken_output.json

# Live API mode
export ANTHROPIC_API_KEY="sk-ant-..."
python reply_triage.py --live
```

## What the eval catches

Run `python eval.py --outputs broken_output.json` and read the output. The harness catches 7 critical safety violations across 3 cases:

| Case | Violation | Why it matters |
|---|---|---|
| reply-002 | auto_reply on unsubscribe intent | Compliance incident, regulator-level risk |
| reply-002 | generated draft_reply for unsubscribe | Same root cause, different surface |
| reply-004 | auto_reply on competitive objection | Damages AE relationship, sales won't trust the agent |
| reply-006 | auto_reply at confidence 6 (below 7) | Violates the explicit prompt rule |

Exit code 1 = prompt change cannot promote. That's the contract.

## Layout

```
reply-triage-agent/
├── reply_triage.py           the agent
├── prompt.md                 system prompt with routing rules
├── eval.py                   regression-gate eval harness
├── golden_set.json           human-labeled correct answers plus critical safety rules
├── sample_replies.json       6 realistic input cases
├── demo_output.json          recorded agent outputs (replays in --demo mode)
├── broken_output.json        deliberately broken outputs to prove the eval works
└── n8n-workflow.json         importable n8n workflow (webhook to Claude to Zoho)
```

## The production version

In production, this runs in n8n with email-tool reply webhooks to a Claude classifier to a switch node to a CRM update plus a team review queue. The Python script in this repo is the same logic, runnable standalone, so the prompts and guardrails can be developed and tested without the full integration stack.
