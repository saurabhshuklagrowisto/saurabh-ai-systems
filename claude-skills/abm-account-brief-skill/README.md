# ABM Account Brief Skill

A Claude Skill that generates structured, evidence-grounded outbound briefs for B2B accounts. Refuses output when ICP is missed or signal is too weak. Eval-gated, prompt-versioned.

This is the packaged, standalone version of a workflow that runs in production via n8n plus a CRM automation layer plus the Claude API for B2B outbound.

## What it does

**Input:** target account domain plus persona plus recent signals.
**Output:** structured JSON with company snapshot, three distinct hooks (each cited to a real signal URL), recommended channel, a 60-word email draft, and a calibrated confidence score.

The Skill refuses when:
- The account fails the hard ICP gate in `references/icp-criteria.md`
- No signal in the last 90 days (returns `insufficient_signal: true`)
- Confidence below threshold (rep is told not to send without human review)

Refusal is a first-class output, not an error.

## What it proves

- **Skill packaging** · SKILL.md is the contract; `references/icp-criteria.md` is loaded on demand, not stuffed in the system prompt
- **Prompt versioning** · v1 to v2 with documented reason (v1 failed hook diversity 3 of 10 cases on generic-growth hooks)
- **Eval as a gate** · `scripts/score_output.py` runs the golden set and exits non-zero if any threshold regresses
- **Refusal as a feature** · "out of ICP" and "insufficient signal" are valid outputs

## Architecture

```
  Clay enrichment ─────┐
  LinkedIn Sales Nav ──┤
  News API ────────────┤
                       ▼
              ┌────────────────────────────┐
              │   abm-account-brief Skill  │
              │                            │
              │   1. ICP gate              │
              │   2. Evidence audit        │
              │   3. 3 distinct hooks      │
              │   4. Channel selection     │
              │   5. Email draft           │
              │   6. Confidence score      │
              └────────────┬───────────────┘
                           ▼
              ┌────────────────────────────┐
              │  Eval / guardrail layer    │
              │  - schema validation       │
              │  - evidence grounding      │
              │  - length compliance       │
              │  - hook diversity          │
              │  - LLM-as-judge            │
              └────────────┬───────────────┘
                           ▼
              ┌────────────────────────────┐
              │  CRM writeback plus send   │
              │  Reply rate feeds prompt   │
              │  v(N+1) gate               │
              └────────────────────────────┘
```

## How to run

```bash
python scripts/score_output.py --prompt prompts/v2.md --verbose
```

Eval scores on: schema validity (binary), evidence grounding (every hook cites a URL from input signals), hook diversity (no two hooks paraphrase the same signal), length compliance (subject under 50, body under 60 words), LLM-as-judge rating vs golden hook.

Non-zero exit = prompt change blocked from promote.

## Layout

```
abm-account-brief-skill/
├── SKILL.md                  the Skill contract (loaded by Claude)
├── references/
│   └── icp-criteria.md       ICP rubric, loaded on demand
├── prompts/
│   ├── v1.md                 deprecated, with reason
│   └── v2.md                 current production
├── scripts/
│   └── score_output.py       eval harness
└── golden_set.jsonl          3 hand-labeled golden cases
```

## Why a Skill, not a system prompt

- **Composability** · invoke from multiple agents (orchestrator, manual rep tool, batch job) without duplicating the prompt
- **Context efficiency** · Claude loads ICP rubric only when the Skill activates
- **Reviewability** · sales leads can edit `icp-criteria.md` without touching prompts
