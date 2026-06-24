# US CTO Outbound Stack

![Status](https://img.shields.io/badge/status-production-success?style=flat-square)
![Cost](https://img.shields.io/badge/all--in_cost-under_%242%2Fmo-22c55e?style=flat-square)
![Audience](https://img.shields.io/badge/target-US_CTOs-1e40af?style=flat-square)

A full outbound system targeting Chief Technology Officers at B2B companies in the US. Designed the targeting logic, sequence design, reply handling automation, and CRM sync from scratch. The full stack costs under $2 a month at the scale we operate — that radical cost edge comes from self-hosted Sendy plus careful tool composition with Apollo, Clay and Prospectoo. Built for a client at [Growisto](https://growisto.com).

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
   │  Clay + Apollo +        │  Find CTO contacts + signals
   │  Prospectoo enrichment  │  Verify email + LinkedIn
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
   │  Sendy delivery         │  Self-hosted email sending
   │  (cold email)           │  Amazon SES backend, near-zero
   │                         │  per-send cost at volume
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
   │  Zoho CRM sync          │  Lead stage updates,
   │                         │  meeting bookings logged,
   │                         │  attribution preserved
   └─────────────────────────┘
```

## The workflow

1. **Build the target list.** Clay orchestrates the enrichment workflow; Apollo and Prospectoo provide CTO contact data, LinkedIn URLs, and recent signals (hires, fundraises, product launches). Prospectoo is the secondary verifier when Apollo confidence is low on a contact.
2. **Filter against ICP.** Claude scores each account against the ICP rubric before any outreach happens. Accounts that fail the gate are flagged for review, not contacted.
3. **Generate per-account hooks.** For each surviving account, Claude pulls the recent signals and writes 3 distinct hook angles. Each one is grounded in a specific signal URL. Hooks that read generic ("the company is growing") are rejected by the guardrail.
4. **Send the sequence.** Sendy delivers the high-volume cold touches over 21 days using Amazon SES on the backend. Lemlist is used for the more personalized warm follow-ups where the per-send cost is justified by closer-to-the-buyer messaging. Cadence is tuned per ICP segment.
5. **Triage replies.** When a reply lands, the n8n + Claude reply-triage agent (see [claude-skills/reply-triage-agent](../../claude-skills/reply-triage-agent)) classifies intent and either drafts a response for AE approval or routes to human review based on confidence.
6. **Sync to Zoho CRM.** Every meaningful event (open, reply, meeting booked, unsubscribe) writes to Zoho for attribution and reporting.

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
| Prospectoo | Shared, allocated cost is small |
| Sendy + Amazon SES | Self-hosted Sendy; SES costs ~$0.10 per 1,000 sends |
| Lemlist (warm follow-up only) | Shared, allocated cost is small |
| n8n | Self-hosted |
| Zoho CRM | Existing client license |
| **Total** | **Under $2/month all-in for this stack** |

The headline number compares to a typical US team paying $2,000+/month for a comparable outbound stack. The 1,000x cost edge comes from three deliberate choices: self-host Sendy instead of paying per-seat to a managed cold-email SaaS, share enrichment licenses (Apollo + Clay + Prospectoo) across projects, and use Claude for the expensive specialist work (personalization at scale, reply classification, ICP scoring).

## The stack

`Clay` orchestrates enrichment · `Apollo` for prospect data · `Prospectoo` for secondary contact verification · `Sendy` (self-hosted on Amazon SES) for high-volume cold sends · `Lemlist` for warm personalized follow-ups · `n8n` for automation glue · `Zoho CRM` as system of record · `Claude (Sonnet 4.6)` for ICP scoring, hook generation, and reply classification

## Read more

Full case study with context on the portfolio website: **[shivsaurabh.netlify.app](https://shivsaurabh.netlify.app)**
