# Pipeline Automation Flows

Seven import ready n8n workflows that together form a self running B2B pipeline engine: instant lead response, anonymous visitor conversion, intent based account prioritization, lead enrichment and qualification, automated weekly reporting, and AI answer engine visibility. Built for enterprise ABM motions targeting 500+ employee accounts in regulated industries (insurance, banking, wealth, fintech).

Every flow follows the same design rules I use in production:

- AI proposes, a validated schema executes, a human gates customer facing sends until trust is earned
- Suppression and cooling windows enforced in code, not memory
- Cheap fast model (Haiku) for high volume scoring, larger models only where judgment is scarce
- Every flow ends in the CRM, so the weekly scorecard builds itself
- Demo mode everywhere: each flow imports and runs with zero API keys, swap the marked nodes for live connectors to go to production

## The flows

| Flow | File | What it does |
|------|------|--------------|
| Speed to Lead Engine | speed-to-lead-engine.json | Demo form submit to personalized calendar email in under 5 minutes: enrich, AI score against ICP, tier route, alert the AE, log to CRM |
| Speed to Lead (Demo Mode) | speed-to-lead-engine-demo.json | Same graph with enrichment and AI scoring mocked as rule based code nodes. Runs anywhere with zero API keys, useful for testing the routing logic |
| Visitor Identification Outreach | visitor-identification-outreach.json | Person level website visitor identification (RB2B style webhook) to same day outreach: ICP gate, CRM suppression check, 28 day cooling window, page aware AI opener, tier routing to sequence or retargeting |
| Intent Priority Engine | intent-priority-engine.json | Daily scheduled scoring of three signal streams (job changes, web visits, content engagement) with weights and 30 day time decay. T1 becomes a human task with an AI written why now line, T2 flows to automation, T3 to ads |
| Lead Enrichment and Qualification | lead-enrichment-qualification.json | Takes a list of emails, enriches each with company info and which email or collaboration provider they run, then qualifies against ICP and flags switch targets already on a rival platform |
| Weekly Report Bot | weekly-report-bot.json | Scheduled weekly digest that reads the week's pipeline numbers and posts a clean report with week over week movement to Slack or email |
| AEO / LLM Visibility Monitor | aeo-llm-visibility-monitor.json | Checks whether the brand shows up when buyers ask ChatGPT, Perplexity and Gemini real questions, scores share of voice against competitors, and lists the questions where the brand is invisible |

Plus `priority-dashboard-emergent-prompt.md`: a complete build prompt for a working dashboard app (built on Emergent) that visualizes the priority engine: live tier board, signal simulator, score decay, daily queue.

## Proof: real execution outputs

### Speed to Lead, two payloads, opposite decisions

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

### Lead Enrichment and Qualification, four emails in, scored out

Input: a list of four emails. Output after enrich plus qualify:

```
Priya Sharma | HDFC Bank    | fit 10 | qualified true  | switch target: Microsoft 365   | banking, 120000 employees
Dr. Nair     | City Hospital | fit 10 | qualified true  | switch target: Legacy Exchange | healthcare, 3000 employees
Raj Mehta    | Tech Startup  | fit 2  | qualified false | too small (40 employees), non target industry
Anon User    | gmail         | fit 0  | qualified false | personal email, disqualified
```

Two real targets pass and carry a switch target flag, a small startup and a personal email are filtered out automatically.

### Weekly Report Bot, sample week in, formatted digest out

```
Weekly Pipeline Report
New leads: 82  (up +8, 11%)
Qualified: 31  (up +4, 15%)
Replies:   46  (up +7, 18%)
Meetings:  14  (up +3, 27%)
Pipeline:  INR 42.0L  (17% WoW)
Meetings up week over week, keep the winning sequence running.
```

### AEO / LLM Visibility Monitor, five questions across three engines

```
Share of voice in AI answers: 33%  (5 of 15 answers named the brand)
Top competitors winning the answers: Copy.ai (10), Clay (10), Writer (8)
Action: prioritise content and structured answers for the questions where the brand loses.
```

The flow also lists any question where the brand is named by zero engines, so content and AEO effort goes exactly where it moves the number.

## Import

1. n8n, Workflows, three dot menu, Import from File
2. Pick a JSON, the full node graph appears
3. Production flows: replace the credential placeholders (Apollo, Anthropic, Instantly, Slack webhook, CRM token)
4. Demo mode flows: nothing to configure, activate and run

Test payload for the speed to lead demo flow:

```
curl -X POST "https://YOUR-N8N-URL/webhook/speed-to-lead-demo" \
  -H "Content-Type: application/json" \
  -d '{"name":"Sarah Mitchell","email":"sarah.mitchell@northwesternmutual.com","phone":"+1 414 555 0134","problem":"We hire 40 financial advisors a quarter and ramp takes 4 months"}'
```

## How the flows compose

The visitor flow feeds signals into the priority engine. The priority engine decides where human hours go. The speed to lead flow catches whoever raises a hand. Enrichment and qualification keeps the top of funnel clean before anything enters a sequence. The report bot turns the week into a scorecard nobody has to build by hand. The AEO monitor watches the newest channel, whether the brand shows up when buyers ask an AI. One engine, many entry points, zero daily manual routing.
