# Hiring-Signal Outbound · Staffing Vertical

![Status](https://img.shields.io/badge/status-live%20code%20%2B%20architecture-blue?style=flat-square)
![Motion](https://img.shields.io/badge/motion-intent--signal_outbound-7c3aed?style=flat-square)
![Region](https://img.shields.io/badge/region-USA-1e40af?style=flat-square)

An outbound motion built around a single insight: a job posting is one of the most honest buying signals a company puts on the internet. When a business posts "hiring a medical biller," it is telling you it has an open seat, an approved budget, and a real pain today. This motion catches that signal the morning it goes live, qualifies it, finds the buyer, and starts a personalized conversation, all while the seat is still open. Built for a staffing company that places trained remote talent with US businesses.

Where the [ATLAS · AI Employee System](../../production-systems/atlas-ai-employee-system) documents the agent infrastructure, this documents the marketing motion those agents run.

## The outcome

Honest framing. This is a live-code build proven on a real scrape, not a six-month pipeline claim. The numbers below are what the engine produced on a representative run and the targets set for the pilot.

| Metric | Value |
|---|---|
| Real postings scraped and scored in one run | 259 across 15 title queries, US only |
| Qualified rate after the rubric gate | ~4% qualified, ~50% into a softer nurture track, the rest disqualified |
| Cost to scrape and score | $0 (Indeed and free boards via JobSpy, keyword filter before any AI) |
| Pilot targets | open rate above 40%, reply rate above 2%, at least 5 booked calls per 200 leads |
| Deliverability guardrail | spam complaints under 0.2%, bounces under 3% |

## The architecture

```
   Job boards, scanned daily
            │
            v
   ┌─────────────────────────────┐
   │  Scrape US admin postings   │  JobSpy for Indeed, ZipRecruiter,
   │  25 target titles           │  Google Jobs, plus free remote APIs
   └────────────┬────────────────┘
                │
                v
   ┌─────────────────────────────┐
   │  Relevancy gate, score 0-100│  Keyword filter free, then Claude
   │  (rubric + Claude)          │  on the ambiguous middle. Only 70+
   │                             │  spends any money downstream.
   └────────────┬────────────────┘
                │
                v
   ┌─────────────────────────────┐
   │  Free size check, then Clay │  NPPES provider registry confirms
   │  enrichment                 │  size for free, then Clay finds the
   │                             │  decision maker, verified email+phone
   └────────────┬────────────────┘
                │
                v
   ┌─────────────────────────────┐
   │  Personalized 5-touch       │  Claude writes each sequence from
   │  sequence (Claude)          │  the actual posting, with the posted
   │                             │  salary as the savings math
   └────────────┬────────────────┘
                │
                v
   ┌─────────────────────────────┐
   │  Warmed cold send           │  Smartlead or Instantly, secondary
   │                             │  domains, human approves the copy
   └────────────┬────────────────┘
                │
                v
   ┌─────────────────────────────┐
   │  Reply → Close CRM → rep     │  Positive reply routes to a rep with
   │                             │  a full context card and a call cadence
   └─────────────────────────────┘
```

## The workflow

1. **Scrape the demand.** Every morning, pull the target admin job titles across the US. Deduplicate, keep only postings under fourteen days old so the seat is still open, and capture the posted salary where it is shown.
2. **Qualify with the rubric.** Every posting starts at 50 points. Hard blockers (clinical duties, hospitals, licensed roles) drop it to zero for free. Red flags subtract, green flags (remote language, remote-scope duties, a named cloud EHR, growth signals, a small or mid sized employer) add. The gate is 70. Postings from 40 to 69 fall into a softer nurture track rather than being discarded.
3. **Enrich, free checks first.** The free NPPES registry confirms company size before any paid credit, which is what catches a large firm hiding behind a small-sounding name. Then Clay resolves the decision maker keyed to company size, with a verified email and phone, at most two or three contacts per company.
4. **Write from the posting.** Claude drafts a five touch sequence anchored to the exact role, quoting duties from the posting and using the posted salary to show the same work done at a fraction of the cost. Never a generic blast.
5. **Send warm, hand off warmer.** Sequences go out from warmed secondary domains, never the main one, after a human approves the copy. A positive reply routes into Close CRM with a full context card, and the rep runs a call cadence starting within the hour.

## Where AI plugs in

- **Relevancy scoring** · Claude judges the ambiguous middle after a free keyword pass, so paid enrichment is only ever spent on postings that truly fit. This is the control that makes the whole motion affordable.
- **Personalization** · Claude writes each sequence from the specific posting, the named EHR, the posted salary, and the practice size, so every email reads like it was written for that one business.
- **Reply handling** · a positive reply is classified and routed to a rep with the full context attached, so the human starts warm.

## Why hiring-signal outbound, not a cold list blast

A cold list is a guess about who might be in the market. A job posting is a business telling you it is in the market, right now, with budget. The motion is built to notice that signal the day it appears and act while it is fresh, which is why the qualification gate matters more than volume. Sending fewer, sharper, signal-triggered messages beats spraying a list, and it keeps the enrichment budget small enough that the whole thing runs for a low monthly cost.

## The stack

`JobSpy` and free job-board APIs for scraping · `Claude` for relevancy scoring and sequence writing · `NPPES` provider registry for a free company-size check · `Clay` for decision-maker enrichment · `Smartlead` or `Instantly` for warmed cold sending · `Close` as the CRM and rep call cadence

## Related

- The agent infrastructure that runs this motion: [ATLAS · AI Employee System](../../production-systems/atlas-ai-employee-system)
- The working scraper and ICP scorer: [Scout pipeline code](../../production-systems/atlas-ai-employee-system/code)
- The full engine spec: [OUTBOUND-ENGINE.md](../../production-systems/atlas-ai-employee-system/OUTBOUND-ENGINE.md)
