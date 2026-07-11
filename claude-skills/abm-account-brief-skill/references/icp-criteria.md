# ICP Criteria — B2B ABM (sample, India + USA)

<!-- Sample ICP framework for the skill demo. Replace the thresholds and rules below with your own. -->


This file is loaded by the `abm-account-brief` Skill to gate hook generation. If a target account fails any **hard criterion**, the Skill must return `out_of_icp: true` and stop.

## Hard criteria (all must pass)

| Criterion | Value | Why |
|---|---|---|
| Headcount | 200+ employees | Below this, no dedicated marketing tech budget |
| Annual revenue | $10M+ USD equivalent | Below this, agency engagements are out of reach |
| Geo | India OR USA (HQ or primary market) | Sales coverage limited to these two markets |
| Industry | NOT in: gambling, adult, MLM, crypto-exchange | Brand-safety policy |
| Funding status | NOT in active layoffs or chapter 11 | Wrong timing |

## Soft signals (raise ICP score)

Add 1 point each, max +5:

- Hired a new VP/Director of Marketing, Growth, or RevOps in the last 90 days
- Raised funding (Series A or later) in the last 180 days
- Launched a new product or geographic market in the last 90 days
- Has open job reqs for marketing operations, marketing automation, or RevOps roles
- Currently using a CRM (HubSpot or Salesforce) but no marketing automation layer visible in their public stack

## Persona priorities (in order)

For the persona named in the input, anchor hooks to these pain themes:

- **CTO** — agent reliability in production, integration debt, build vs buy on AI infra
- **VP Engineering** — engineering velocity for the marketing/sales stack, on-call load from broken integrations
- **Director Marketing Technology** — HubSpot/SF data fabric, attribution, agentic workflows that reduce manual ops
- **Head of RevOps** — lead-to-account match rates, sales handoff quality, pipeline forecast accuracy
- **VP Sales** — meetings booked per SDR, reply rates, time-to-first-touch on inbound

## Disqualifiers for outbound (return `insufficient_signal: true`)

- No public signal in the last 90 days
- The persona role is currently vacant (cannot infer the human's priorities)
- Account is already a customer or in active conversation (check CRM before generation)
