# US CTO Outbound Stack

![Status](https://img.shields.io/badge/status-production-success?style=flat-square)
![Cost](https://img.shields.io/badge/all--in_cost-under_%242%2Fmo-22c55e?style=flat-square)
![Audience](https://img.shields.io/badge/target-US_CTOs-1e40af?style=flat-square)

A full outbound system targeting Chief Technology Officers at B2B companies in the US. Designed the targeting logic, sequence design, reply handling automation, and CRM sync from scratch. The full stack costs under $2 a month at the scale we operate. Built for a client at [Growisto](https://growisto.com).

## The outcome

| Metric | Value |
|---|---|
| Qualified meetings booked | 25+ per month |
| Influenced pipeline | ~$1.2M across 6 months |
| Monthly tooling cost | Under $2 all-in |
| Cold outbound reply rate | 6%+ (industry baseline: 1-3%) |
| Audience | Chief Technology Officers, US B2B |

## The architecture

```
   Target list
     │
     v
   ┌─────────────────────────┐
   │  Clay enrichment        │  Find CTO contacts + signals
   │  + Apollo prospecting   │  Verify email + LinkedIn
   └────────────┬────────────┘
                │
                v
   ┌─────────────────────────┐
   │  ICP filter             │  Claude scores against ICP
   │  (Claude reasoning)     │  before any account gets touched
   └────────────┬────────────┘
                │
                v
   ┌─────────────────────────┐
   │  Per-account hook       │  Claude generates 3 distinct
   │  generation             │  hooks per account, grounded
   │  (Claude + signals)     │  in real LinkedIn/news signals
   └────────────┬────────────┘
                │
                v
   ┌─────────────────────────┐
   │  Smartlead delivery     │  Multi-touch sequence,
   │  (cold email)           │  warmup-protected
   └────────────┬────────────┘
                │
                v
   ┌─────────────────────────┐
   │  Reply triage           │  n8n + Claude classifies
   │  (n8n + Claude)         │  intent, routes auto-draft
   │                         │  or human review
   └────────────┬────────────┘
                │
                v
   ┌─────────────────────────┐
   │  HubSpot CRM sync       │  Lead stage updates,
   │                         │  meeting bookings logged,
   │                         │  attribution preserved
   └─────────────────────────┘
```

## The workflow

1. **Build the target list.** Clay enriches a seed list of US B2B companies with CTO contact data, LinkedIn URLs, and recent signals (hires, fundraises, product launches).
2. **Filter against ICP.** Claude scores each account against the ICP rubric before any outreach happens. Accounts that fail the gate are flagged for review, not contacted.
3. **Generate per-account hooks.** For each surviving account, Claude pulls the recent signals and writes 3 distinct hook angles. Each one is grounded in a specific signal URL. Hooks that read generic ("the company is growing") are rejected by the guardrail.
4. **Send the sequence.** Smartlead delivers a 5-touch sequence over 21 days. Cadence is tuned per ICP segment.
5. **Triage replies.** When a reply lands, the n8n + Claude reply-triage agent (see [claude-skills/reply-triage-agent](../../claude-skills/reply-triage-agent)) classifies intent and either drafts a response for AE approval or routes to human review based on confidence.
6. **Sync to HubSpot.** Every meaningful event (open, reply, meeting booked, unsubscribe) writes to HubSpot for attribution and reporting.

## Where AI plugs in

Three places, each load-bearing:

- **ICP scoring** — Claude reads the enriched account record and rates ICP fit before any outreach. Cheap to run, prevents off-ICP accounts polluting the pipeline.
- **Per-account hook generation** — Claude writes the personalization, anchored to real signals. This is what makes 6%+ reply rates possible on cold email.
- **Reply triage** — Claude classifies inbound replies and proposes routing. AE approves with one click, never auto-sends. Same pattern documented in `claude-skills/reply-triage-agent`.

## Why under $2/month

| Cost line | Monthly |
|---|---|
| Claude API (via Anthropic direct) | ~$0.50 to $1.50 depending on volume |
| Clay (lower-tier plan) | Shared across multiple projects, allocated cost is minor |
| Apollo (lower-tier plan) | Shared, allocated cost is minor |
| Smartlead | Shared workspace, allocated cost is small |
| n8n | Self-hosted |
| HubSpot | Existing client license |
| **Total** | **Under $2/month all-in for this stack** |

The headline number compares to a typical US team paying $2,000+/month for a comparable outbound stack. The 1,000x cost edge comes from careful tool choice plus heavy use of Claude for the parts that used to require expensive specialist tools (personalization at scale, reply classification, ICP scoring).

## The stack

`Clay` for enrichment · `Apollo` for prospect data · `Smartlead` for cold email delivery · `n8n` for automation glue · `HubSpot` as CRM · `Claude (Sonnet 4.6)` for ICP scoring, hook generation, and reply classification

## Read more

Full case study with context on the portfolio website: **[shivsaurabh.netlify.app](https://shivsaurabh.netlify.app)**
