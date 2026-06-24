# Marketing Ops Automation Layer

![Status](https://img.shields.io/badge/status-production-success?style=flat-square)
![Workflows](https://img.shields.io/badge/workflows_live-14-1e40af?style=flat-square)
![Time saved](https://img.shields.io/badge/weekly_time_saved-~12_hrs-22c55e?style=flat-square)

Replaced 12 hours per week of manual marketing operations work with an automation layer spanning CRM hygiene, lead routing, lead scoring, campaign attribution, and reporting. Built at [Growisto](https://growisto.com), self-hosted on Railway.

## The outcome

| Metric | Value |
|---|---|
| Weekly time saved | ~12 hours of manual ops work |
| Workflows in production | 14 |
| Lead routing errors per quarter | 0 |
| Hosting | Self-hosted n8n on Railway |
| Frees up | Higher-leverage creative and strategy work for the team |

## The architecture

```
   ┌──────────────────────────────────────────────────────┐
   │                  TRIGGERS                            │
   │                                                      │
   │  HubSpot webhooks · GA4 events · Form submissions   │
   │  Cron schedules · Manual triggers (Cliq commands)   │
   └────────────────────┬─────────────────────────────────┘
                        │
                        v
   ┌──────────────────────────────────────────────────────┐
   │                  n8n on Railway                      │
   │  (self-hosted orchestrator, 14 workflows live)       │
   └────────────────────┬─────────────────────────────────┘
                        │
       ┌────────────────┼────────────────┐
       v                v                v
   ┌────────┐     ┌──────────┐    ┌────────────┐
   │Hygiene │     │ Routing  │    │  Scoring   │
   │        │     │          │    │            │
   │ Dedup  │     │Territory │    │ Engagement │
   │ Format │     │Vertical  │    │ Behaviour  │
   │ Suppress│    │Round-robin│   │ Firmograph │
   └────┬───┘     └─────┬────┘    └─────┬──────┘
        │               │                │
        v               v                v
   ┌──────────────────────────────────────────────────────┐
   │                 HUBSPOT                              │
   │  (system of record, all writes flow back here)       │
   └────────────────────┬─────────────────────────────────┘
                        │
                        v
   ┌──────────────────────────────────────────────────────┐
   │              REPORTING LAYER                         │
   │                                                      │
   │  Looker Studio dashboards · Google Sheets staging   │
   │  Weekly automation digest email to team             │
   └──────────────────────────────────────────────────────┘
```

## What the 14 workflows actually do

| Category | Workflows |
|---|---|
| **CRM hygiene** | Dedup new contacts against existing records · Normalise phone numbers and email formats · Sync unsubscribes across systems · Auto-tag based on inferred attributes |
| **Lead routing** | Round-robin by territory · Route by vertical to specialist AEs · Escalate hot leads to senior AEs · SLA-based reassignment if no touch in 24h |
| **Lead scoring** | Engagement score (email + site + content) · Firmographic fit score · Buying-intent score from external signals · Composite tier (A/B/C) |
| **Campaign attribution** | UTM normalisation · First/last/multi-touch attribution write-back to HubSpot · Influenced pipeline calculation per campaign |
| **Reporting** | Weekly automation digest email · Looker Studio dashboard refresh · Anomaly alerts (sudden score changes, broken workflows) |

## The workflow philosophy

Every workflow follows the same shape:

1. **One trigger** — webhook, schedule, or manual command
2. **One responsibility** — workflow does exactly one thing, no spaghetti
3. **One write target** — workflow writes back to HubSpot or sends an alert, not both
4. **Idempotent** — re-running the same workflow on the same input produces the same output
5. **Observable** — every run logs to a central location for audit and debugging

This discipline is what keeps the count manageable. Without it, 14 workflows would become 80 spaghetti workflows in a year.

## Why self-hosted on Railway

n8n cloud would have been simpler. The self-hosted choice came from:

- **Cost** · Self-hosted on Railway is roughly $5/month. n8n cloud at the same workflow volume would be $20+/month. Across a year, the difference is meaningful.
- **Data residency** · Self-hosted means client data does not flow through n8n's hosted environment.
- **Custom nodes** · Self-hosted instance can install custom community nodes for the specific integrations needed.
- **Trade-off** · A self-hosted instance needs occasional maintenance (updates, backups). The team takes this on; the trade-off is worth it at this scale.

## Where AI plugs in

- **Anomaly detection** · A weekly Claude call reviews workflow logs and flags unusual patterns (sudden score drops, lead routing skew, attribution gaps). This caught two real issues that would have taken weeks to surface manually.
- **Composite scoring rules** · Claude assisted in writing the composite-tier rules (engagement + firmographic + intent → A/B/C). The rules are codified in n8n, not LLM-decided at runtime, but Claude helped tune the thresholds.
- **Weekly digest** · The weekly automation digest email summary is generated by Claude from raw workflow stats.

## Why 0 routing errors per quarter matters

Before the automation, lead routing was manual. Errors happened weekly (lead assigned to wrong AE, double-assigned, missed assignment). Each error meant either a sales conflict or a slipped lead. After the automation: zero errors per quarter.

Zero is the goal because lead routing errors compound. One bad assignment damages trust between marketing and sales. Five compound into a process review. Twenty compound into a re-org. Automation makes the floor reliably high, which is what lets the team focus on the strategy layer instead of the plumbing.

## The stack

`n8n` self-hosted on `Railway` · `Make.com` for a few cross-app workflows where n8n nodes don't exist · `HubSpot` as system of record · `Google Sheets` for ops staging and weekly review tables · `Looker Studio` for dashboards · `Claude` for anomaly detection and the weekly digest

## Read more

Full case study with context on the portfolio website: **[shivsaurabh.netlify.app](https://shivsaurabh.netlify.app)**
