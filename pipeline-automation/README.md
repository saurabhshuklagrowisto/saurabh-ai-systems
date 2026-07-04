# Pipeline Automation Flows

Four import ready n8n workflows that together form a self running B2B pipeline engine: instant lead response, anonymous visitor conversion, and intent based account prioritization. Built for enterprise ABM motions targeting 500+ employee accounts in regulated industries (insurance, banking, wealth, fintech).

Every flow follows the same design rules I use in production:

- AI proposes, a validated schema executes, a human gates customer facing sends until trust is earned
- Suppression and cooling windows enforced in code, not memory
- Cheap fast model (Haiku) for high volume scoring, larger models only where judgment is scarce
- Every flow ends in the CRM, so the weekly scorecard builds itself

## The flows

| Flow | File | What it does |
|------|------|--------------|
| Speed to Lead Engine | speed-to-lead-engine.json | Demo form submit to personalized calendar email in under 5 minutes: enrich, AI score against ICP, tier route, alert the AE, log to CRM |
| Speed to Lead (Demo Mode) | speed-to-lead-engine-demo.json | Same graph with enrichment and AI scoring mocked as rule based code nodes. Runs anywhere with zero API keys, useful for testing the routing logic |
| Visitor Identification Outreach | visitor-identification-outreach.json | Person level website visitor identification (RB2B style webhook) to same day outreach: ICP gate, CRM suppression check, 28 day cooling window, page aware AI opener, tier routing to sequence or retargeting |
| Intent Priority Engine | intent-priority-engine.json | Daily scheduled scoring of three signal streams (job changes, web visits, content engagement) with weights and 30 day time decay. T1 becomes a human task with an AI written why now line, T2 flows to automation, T3 to ads |

Plus `priority-dashboard-emergent-prompt.md`: a complete build prompt for a working dashboard app (built on Emergent) that visualizes the priority engine: live tier board, signal simulator, score decay, daily queue.

## Proof: real execution outputs

Demo mode flow, two test payloads fired at the webhook, same engine, opposite decisions.

**Test 1: strong lead**

Input: `Sarah Mitchell, sarah.mitchell@northwesternmutual.com, "We hire 40 financial advisors a quarter and ramp takes 4 months"`

Output:

```
organization: Northwestern Mutual, insurance, 7500 employees
score: 10   tier: T1
reasoning: industry match: insurance; enterprise scale: 7500 employees;
           problem is core use case: sales ramp/training; quantified need stated
email_subject: Your demo, Northwestern Mutual
sent_within: under 5 minutes of form submit
crm_summary: Sarah Mitchell | Northwestern Mutual | score 10 (T1) | source: Website Demo Form
```

Tier 1 branch fired: personalized calendar email plus AE alert with full context card.

**Test 2: weak lead**

Input: `Raj Patel, raj.patel92@gmail.com, "just exploring AI tools"`

Output:

```
organization: Personal Email, unknown, 0 employees
score: 0   tier: T2
nurture_campaign: Warm Nurture: case studies + webinar invites
re_score: monthly, promoted to T1 on any new signal
crm_summary: Raj Patel | Personal Email | score 0 (T2) | source: Website Demo Form
```

Tier 2 branch fired: no AE time spent, lead quietly enrolled in nurture with monthly re scoring.

## Import

1. n8n, Workflows, three dot menu, Import from File
2. Pick a JSON, the full node graph appears
3. Production flows: replace the credential placeholders (Apollo, Anthropic, Instantly, Slack webhook, CRM token)
4. Demo mode flow: nothing to configure, activate and fire the test payload

Test payload for the demo flow:

```
curl -X POST "https://YOUR-N8N-URL/webhook/speed-to-lead-demo" \
  -H "Content-Type: application/json" \
  -d '{"name":"Sarah Mitchell","email":"sarah.mitchell@northwesternmutual.com","phone":"+1 414 555 0134","problem":"We hire 40 financial advisors a quarter and ramp takes 4 months"}'
```

## Why these three flows compose

The visitor flow feeds signals into the priority engine. The priority engine decides where human hours go. The speed to lead flow catches whoever raises a hand. One engine, three entry points, zero daily manual routing.
