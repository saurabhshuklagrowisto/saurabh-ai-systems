# Upwork CTO Account · End-to-End Motion

![Status](https://img.shields.io/badge/status-production-success?style=flat-square)
![Ownership](https://img.shields.io/badge/account_ownership-100%25-22c55e?style=flat-square)
![Pipeline](https://img.shields.io/badge/pipeline_generated-~%24380K-22c55e?style=flat-square)

Won and now operate the Upwork CTO account in full for [Growisto](https://growisto.com). Built the positioning, content cadence, and outbound system from a blank page. Manages ongoing account growth across both inbound proposals and outbound prospecting.

This is the end-to-end **business motion**. The [Upwork plugin](../../production-systems/upwork-proposals) is the technical layer that powers the inbound-proposal side of it.

## The outcome

| Metric | Value |
|---|---|
| Qualified inbound leads | 22 |
| Pipeline generated | ~$380K |
| Account ownership | 100% (positioning, content, outbound, proposals) |
| Starting point | Built from scratch on Day 1 |

## The architecture

```
   ┌────────────────────────────────────────────────────────────┐
   │  INBOUND MOTION                                            │
   │                                                            │
   │  Upwork platform searches (saved queries by ICP)           │
   │       │                                                    │
   │       v                                                    │
   │  /upwork-scan (Claude plugin)                              │
   │  - 16-dimension scoring                                    │
   │  - Cliq channel notification                               │
   │       │                                                    │
   │       v                                                    │
   │  Per-job recommendation                                    │
   │       │                                                    │
   │       v                                                    │
   │  /upwork-proposal [job URL]                                │
   │  - Brand-permission audit gate                             │
   │  - Expertise-first PDF generation                          │
   │  - TOS-compliant cover letter                              │
   │       │                                                    │
   │       v                                                    │
   │  Submit on Upwork                                          │
   │       │                                                    │
   │       v                                                    │
   │  Client replies → discovery call → close                   │
   └────────────────────────────────────────────────────────────┘

   ┌────────────────────────────────────────────────────────────┐
   │  OUTBOUND MOTION                                           │
   │                                                            │
   │  Apollo (CTO contact data, US)                             │
   │       │                                                    │
   │       v                                                    │
   │  Claude per-account hooks                                  │
   │  (different positioning than off-platform outbound)        │
   │       │                                                    │
   │       v                                                    │
   │  Direct DM on Upwork (within platform)                     │
   │       │                                                    │
   │       v                                                    │
   │  HubSpot tracking                                          │
   └────────────────────────────────────────────────────────────┘

   ┌────────────────────────────────────────────────────────────┐
   │  POSITIONING + CONTENT (always-on)                         │
   │                                                            │
   │  Upwork profile content                                    │
   │  Portfolio entries                                         │
   │  Case study attachments                                    │
   │  Testimonial collection                                    │
   └────────────────────────────────────────────────────────────┘
```

## The workflow

This is two motions running in parallel, plus an always-on positioning layer.

### Inbound motion (driven by the Upwork plugin)

1. **Saved searches per ICP** scan the Upwork platform across multiple queries.
2. **`/upwork-scan` runs daily.** Scores every new job on the 16-dimension rubric (client open rate, brief specificity, portfolio match, AU/NZ over-index, screening questions, etc.). Posts ranked results to the Zoho Cliq channel.
3. **Manual prioritization.** Sales picks which jobs to bid on based on the ranked output.
4. **`/upwork-proposal [job URL]`** generates a tailored PDF proposal for each chosen job. Includes the brand-permission audit gate that prevents citing any client without explicit permission, and the TOS-compliant cover letter format.
5. **Submit on Upwork.** Manual final review, then send.
6. **Reply, discovery, close.** Standard sales cycle from there.

### Outbound motion (different positioning than off-platform)

1. **Apollo** pulls US CTO contact data filtered by ICP.
2. **Claude generates per-account hooks** — different angle than off-platform outbound because Upwork DMs have a different feel and TOS.
3. **Direct DM within Upwork** to the prospect.
4. **HubSpot tracks** the touch and any reply.

### Always-on positioning layer

The Upwork profile itself is the marketing surface. Profile content, portfolio entries, case study attachments, and active testimonial collection compound over time. A strong profile makes both inbound and outbound dramatically easier.

## Where AI plugs in

- **`/upwork-scan` (live Claude plugin)** · scores jobs on 16 dimensions, posts to Cliq, recommends what to research per job. See [production-systems/upwork-proposals](../../production-systems/upwork-proposals) for the full architecture.
- **`/upwork-proposal` (live Claude plugin)** · generates the cover letter and PDF proposal with the permission audit gate. Same plugin.
- **Outbound hook generation** · Claude writes the Upwork-platform-native outbound DMs, tuned differently than off-platform email.

## Why owning the account end-to-end matters

The Upwork account is a small business inside the larger agency. Positioning, content, inbound, outbound, profile reputation, testimonial collection, proposal quality — they all compound or they all decay together. A team that splits the responsibilities ("sales does outbound, marketing does content, ops does proposals") fragments the compound loop. End-to-end ownership keeps the loop intact.

The 22 inbound leads and ~$380K pipeline came from running all four layers in the same hands, with the Upwork plugin doing the heavy lifting on the inbound side.

## The stack

`Upwork` (the platform) · `Apollo` for US CTO contact data · `Claude` for both the plugin (scan + proposal) and outbound hooks · `HubSpot` for tracking · `Zoho Cliq` for ranked job notifications

## Read more

Full case study with context on the portfolio website: **[shivsaurabh.netlify.app](https://shivsaurabh.netlify.app)**

Related repo content: the [Upwork Proposal Automation plugin architecture](../../production-systems/upwork-proposals).
