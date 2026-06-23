# The Eval Pattern

Most teams stop at "the agent works in our demos." This document is the alternative: a reusable eval discipline that lets you change prompts in production without paging someone.

## The shape

```
                  ┌───────────────────────────┐
                  │  Golden set (hand-labeled)│
                  │  + critical safety rules  │
                  └────────────┬──────────────┘
                               ▼
                  ┌───────────────────────────┐
   prompt v(N) ──►│  Agent (run on each case) │──► outputs
                  └────────────┬──────────────┘
                               ▼
                  ┌───────────────────────────┐
                  │  Scorers (5 dimensions)   │
                  │  - schema validity        │
                  │  - intent / classification│
                  │  - action / routing       │
                  │  - critical safety        │
                  │  - confidence calibration │
                  └────────────┬──────────────┘
                               ▼
                  ┌───────────────────────────┐
                  │  Thresholds + gate        │
                  │  any below → exit 1       │
                  │  CI blocks promote        │
                  └───────────────────────────┘
```

## The golden set

A JSON file with the **correct** answer for each input. The golden set is the contract — when behavior changes, you either update the golden set (because the new behavior IS correct) or revert the prompt (because it isn't). There is no third option.

```json
{
  "input_id": "reply-002",
  "intent": "unsubscribe",
  "suggested_action": "suppress",
  "must_draft_reply": false,
  "min_confidence": 9,
  "critical_safety_rules": [
    "NEVER auto_reply",
    "NEVER generate draft_reply",
    "MUST set crm stage to unsubscribed"
  ]
}
```

The `critical_safety_rules` are the zero-tolerance gates. Any violation in any case fails the entire promote — no matter how high the aggregate accuracy.

## The scorers

Five dimensions cover different failure modes:

| Scorer | What it catches |
|---|---|
| **schema_validity** | Output is malformed; downstream systems will crash |
| **intent_accuracy** | The model classified the situation wrong (e.g., labeled an unsubscribe as positive intent) |
| **action_accuracy** | The model classified correctly but routed wrong (e.g., correct intent but wrong follow-up) |
| **critical_safety** | The model did something catastrophic (e.g., auto-replied to an unsubscribe) |
| **confidence_calibration** | The model was confidently wrong (high confidence + incorrect = the worst failure mode) |

Three of these (schema, intent, action) are accuracy metrics. Critical safety is zero-tolerance. Calibration measures whether the model knows what it doesn't know.

## The thresholds

```python
THRESHOLDS = {
    "intent_accuracy": 0.85,
    "action_accuracy": 0.85,
    "schema_validity": 1.0,        # any malformed = fail
    "critical_safety": 1.0,        # any catastrophic = fail
    "confidence_calibration": 0.95, # high-conf must be near-perfect
}
```

`1.0` thresholds mean **no tolerance** — one violation in one case blocks promote.

## Why 1.0 thresholds matter

There are two kinds of errors an agent can make:

1. **Recoverable errors** — wrong classification, suboptimal phrasing. Customer sees a slightly weird reply. Sales fixes it next touch.
2. **Catastrophic errors** — auto-replied to an unsubscribe (regulator). Sent a competitor's name to a customer (brand). Wrote PII to an external system (compliance).

Catastrophic errors are what take the agent down. Aggregate accuracy doesn't surface them — 95% accuracy means 5% of catastrophic events ship.

Zero-tolerance gates on the catastrophic class force you to prove the model never makes that specific error, not "rarely makes" it. That's the difference between an agent you can leave running and an agent that needs a babysitter.

## Adapting this to a new workflow

1. Write a golden set — 10-30 hand-labeled cases. Include edge cases on purpose (unsubscribe, wrong-person, low-confidence-positive).
2. Annotate each case with `critical_safety_rules` — the things that must NEVER happen.
3. Pick scorers — schema validity is always required; pick 3-4 task-specific accuracy dimensions.
4. Set thresholds — `1.0` on schema + critical safety, `0.85-0.95` on accuracy dimensions.
5. Wire to CI — `pytest`-style exit code, fail the build on any threshold miss.

## What this catches that "manual review" doesn't

- **Regressions** — v3 of the prompt accidentally drops the unsubscribe-handling logic. Manual review would catch it next week. The eval catches it before merge.
- **Quiet drift** — model provider rolls out a new version. Aggregate accuracy stays flat, but the rate of confident-but-wrong outputs creeps up. Calibration metric catches it.
- **Cross-case interactions** — a prompt change improves cases 1-5 but regresses case 9. Without the harness, you'd see "looks better" and ship.

## What this doesn't catch

- **Inputs you haven't labeled** — the eval is only as good as the golden set
- **Prompt-injection in the wild** — covered separately by `shared/guardrails.py` at runtime
- **Cost regressions** — if v3 burns 10× the tokens of v2 for marginal quality gain, accuracy metrics won't tell you. Track input/output token counts separately.

The eval pattern is necessary but not sufficient. Combine with runtime guardrails (Stage 1 + 3 in [ARCHITECTURE.md](../ARCHITECTURE.md)) and you have a production-shaped quality discipline.
