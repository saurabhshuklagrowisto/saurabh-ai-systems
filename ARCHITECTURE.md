# Architecture

Every workflow in this repo follows the same five-stage shape. Understanding the shape is more useful than reading any single workflow.

## The shape

```
   Input (webhook / cron / manual)
              │
              ▼
   ┌─────────────────────────────┐
   │  1. Input guardrail         │
   │  - PII scrub                │
   │  - Prompt-injection check   │
   │  - Max input size cap       │
   └──────────┬──────────────────┘
              │ pass
              ▼
   ┌─────────────────────────────┐
   │  2. Claude call             │
   │  - System prompt (v(N).md)  │
   │  - Strict JSON schema       │
   │  - Tag with prompt version  │
   └──────────┬──────────────────┘
              │
              ▼
   ┌─────────────────────────────┐
   │  3. Output guardrail        │
   │  - Schema validation        │
   │  - Banned phrase scan       │
   │  - Confidence threshold     │
   │  - Length compliance        │
   └──────────┬──────────────────┘
              │ pass
              ▼
   ┌─────────────────────────────┐
   │  4. Routing / side effects  │
   │  - CRM write                │
   │  - Channel send (gated)     │
   │  - Human review queue       │
   │  - Dead-letter on failure   │
   └──────────┬──────────────────┘
              │
              ▼
   ┌─────────────────────────────┐
   │  5. Eval feedback loop      │
   │  - Log output + version     │
   │  - Replay against golden    │
   │  - Block promote on regress │
   └─────────────────────────────┘
```

Each stage has a single, falsifiable responsibility. Stages are independently testable. The whole agent is the composition.

## Stage 1 · Input guardrail

Lives in [claude-skills/shared/guardrails.py](./claude-skills/shared/guardrails.py). Three things happen before any Claude call:

- **PII scrubbing** · emails, phone numbers, Indian PAN numbers, government-ID hints are detected and replaced with placeholders. The Claude prompt never sees raw PII.
- **Prompt-injection detection** · patterns like `ignore previous instructions`, `system prompt:`, `<|im_start|>` block the call entirely.
- **Size cap** · input > 8000 chars is rejected, not truncated. Truncation hides bugs; rejection surfaces them.

If any guardrail fails fatally, the agent returns `{blocked_at: "input_guardrail", violations: [...]}` and the Claude call never happens. Cheaper, safer, observable.

## Stage 2 · Claude call

The system prompt is the contract. Each workflow ships its prompt as a versioned file:

```
prompts/
├── v1.md          # deprecated, with reason
└── v2.md          # current production
```

Every call tags the output with the prompt version. Production logs let you ask: "show me all outputs from prompt v2 with confidence below 7 in the last 24 hours" — that question is unanswerable if prompts are buried in code or rolled into a system message constant.

The schema is declared at the top of each prompt. Claude returns strict JSON. Anything else is rejected at Stage 3.

## Stage 3 · Output guardrail

Same module as Stage 1, different functions. The output checks:

- **Schema validation** · `REQUIRED_OUTPUT_KEYS` must all be present; types must be correct; enums must be valid
- **Banned phrases** · sales-y filler like `circling back`, `quick question`, `leverage synergies` rejected from anything that hits a customer
- **Confidence threshold** · below 7 forces `human_review` regardless of intent (override the model when the contract demands it)
- **Length compliance** · subject under 50 chars, body under 60 words

A schema or banned-phrase violation is fatal. A confidence violation triggers re-routing to `human_review` but doesn't drop the case.

## Stage 4 · Routing and side effects

This is where the agent talks to the rest of the world: writes to Zoho CRM, sends via Smartlead, posts to Slack/Cliq, schedules follow-ups. The routing decision is data, not code — `suggested_action` from the model output drives the path through a switch node.

In the demos, this stage is collapsed (we print to stdout). In production via n8n, see [claude-skills/reply-triage-agent/n8n-workflow.json](./claude-skills/reply-triage-agent/n8n-workflow.json) for the full switch graph.

**Critical** · any side effect that touches a customer (sending an email, writing to a public-facing CRM field) is gated by a human-in-the-loop one-click approval. Auto-write to internal CRM stages, auto-send to a customer — never.

## Stage 5 · Eval feedback loop

This is where most teams stop. They build stages 1 through 4 and call it shipped.

The eval loop is what makes the system **continue to work** as prompts change, models update, and the world drifts.

See [claude-skills/reply-triage-agent/eval.py](./claude-skills/reply-triage-agent/eval.py). The pattern:

1. Maintain a hand-labeled golden set with `critical_safety_rules` per case
2. Every prompt change replays the golden set
3. Score on 5 dimensions: schema validity, intent accuracy, action accuracy, critical safety (zero-tolerance), confidence calibration
4. Compare current run to thresholds in `THRESHOLDS = {...}`
5. Exit 1 if any threshold fails. CI blocks promote.

The harness ships with both a passing fixture (`demo_output.json`) and a deliberately broken fixture (`broken_output.json`) so you can see the gate work in both directions.

## Why this shape, and not "one giant prompt"

Three reasons.

**Composability.** When you add a fifth workflow, you reuse `claude-skills/shared/guardrails.py`. Without the separation, you copy-paste the PII regex into every new agent. The first time the regex needs to change for a compliance update, you have a 14-file diff.

**Testability.** You can unit-test the schema validator without calling Claude. You can fuzz the input guardrail without spending API credits. The Claude call is one stage of five. When something breaks, the other four narrow the search space.

**Operability.** When a production incident hits ("we sent an unsubscribe a draft reply"), you can answer in five minutes: which stage failed? The eval would have caught it pre-promote. The guardrail should have caught it at output. The routing should have refused it. One of those three failed; the logs tell you which.

A monolithic prompt fails one of those three checks silently and the incident takes a day.

## When to break the shape

This shape isn't religion. Break it when:

- The agent is read-only (no side effects). Stage 4 collapses.
- There's no production scale yet (under 50 calls a day). Stage 5 can be a weekly batch eval instead of a CI gate.
- The output is consumed by another agent, not a human. Banned-phrase rules don't apply, but schema validation tightens.

But for any agent that touches a customer, writes to a system of record, or runs at meaningful scale: this shape, or your incident rate grows linearly with the number of agents.
