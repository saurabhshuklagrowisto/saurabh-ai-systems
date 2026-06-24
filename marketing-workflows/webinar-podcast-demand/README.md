# Webinar and Podcast Demand Engine

![Status](https://img.shields.io/badge/status-production-success?style=flat-square)
![Webinars](https://img.shields.io/badge/webinars_run-12-1e40af?style=flat-square)
![Conversion](https://img.shields.io/badge/registrant_to_meeting-10%25-22c55e?style=flat-square)

A top-of-funnel demand generation engine built around a closed-loop content motion: pre-event ABM activation for high-intent accounts, live engagement scoring during sessions, and attendance-based nurture sequences that turn listeners into qualified meetings. Built at [Growisto](https://growisto.com).

## The outcome

| Metric | Value |
|---|---|
| Webinars run | 12 |
| Podcast episodes shipped | 8 |
| Average registrants per webinar | ~150 |
| Registrant to qualified meeting conversion | 10% |
| Format | Closed-loop content engine (pre + live + post) |

## The architecture

```
   ┌───────────────────────────────────────┐
   │            PRE-EVENT (T-14 days)      │
   │                                       │
   │  ABM list of high-intent accounts     │
   │       │                               │
   │       v                               │
   │  Personalised invite sequence         │
   │  (HubSpot + Smartlead)                │
   │       │                               │
   │       v                               │
   │  Topic relevance scoring per account  │
   │  (Claude reads account history +      │
   │   recent signals)                     │
   │       │                               │
   │       v                               │
   │  Registration page (HubSpot)          │
   └───────────────┬───────────────────────┘
                   │
                   v
   ┌───────────────────────────────────────┐
   │            LIVE EVENT                 │
   │                                       │
   │  Riverside (recording)                │
   │       │                               │
   │       v                               │
   │  Live engagement signals              │
   │  (Q&A activity, poll responses,       │
   │   session duration)                   │
   │       │                               │
   │       v                               │
   │  Real-time scoring (n8n)              │
   │  Hot attendees flagged                │
   └───────────────┬───────────────────────┘
                   │
                   v
   ┌───────────────────────────────────────┐
   │            POST-EVENT                 │
   │                                       │
   │  Branched nurture (by attendance      │
   │  level and engagement score)          │
   │       │                               │
   │       v                               │
   │   ┌────────────┬────────────┐         │
   │   v            v            v         │
   │  Hot         Engaged       No-show    │
   │  attendee    attendee      sequence   │
   │  → AE        → nurture     → replay   │
   │              continues       invite   │
   │       │            │            │     │
   │       └────────────┴────────────┘     │
   │                   │                   │
   │                   v                   │
   │   Qualified meeting booked            │
   └───────────────────────────────────────┘

   Podcast variant: same shape, asynchronous.
   Episodes go through pre-promote ABM activation,
   download signals serve as "live engagement,"
   post-listen nurture mirrors webinar nurture.
```

## The workflow

1. **Pre-event ABM activation (T-14 days).** A target account list is enriched with topic relevance. Claude reads each account's recent signals and history, and rates topic relevance. High-relevance accounts get personalized invite sequences.
2. **Registration landing page.** HubSpot forms capture registrants. Confirmation email lands. Calendar invite sent.
3. **Live event.** Hosted via Riverside (high-quality recording). During the session, engagement signals (Q&A activity, poll responses, session duration) feed an n8n workflow that scores attendees in real time.
4. **Hot attendees flagged.** Anyone hitting an engagement threshold gets flagged to the AE within an hour of session end.
5. **Branched post-event nurture.** Three branches based on what the attendee did:
   - **Hot attendee** (high engagement, full session) → AE follow-up within 24 hours, custom one-pager
   - **Engaged attendee** (partial session, some engagement) → nurture sequence continues, replay shared
   - **No-show** (registered, did not attend) → replay invite, reschedule offer
6. **Convert to meeting.** Goal is 10% of registrants book a qualified meeting. Across 12 webinars at 150 registrants average, that's roughly 180 meetings from the engine over the program.

## Where AI plugs in

- **Topic relevance scoring** · Claude reads target account histories and rates which topics are most relevant for which accounts. Drives the pre-event invite personalisation.
- **Live engagement scoring rules** · Claude assists in writing the n8n rules that score live signals into a hot/warm/cold tier.
- **Branched nurture copy** · Claude generates the variant sequences for hot/engaged/no-show branches. Each variant references something specific from the session.

## Why this beats "send invites and hope"

The default webinar motion is: blast invites, watch attendance, hope for follow-up. Two things break that model:

1. **Attendance does not equal intent.** Some no-shows are highly engaged (calendar conflict but watched the replay 3x). Some attendees ghost the entire session. Engagement signals matter more than the registration list.
2. **Post-event nurture is where conversion happens.** The session itself is a conversation starter. The branched nurture is where you compound that conversation into a meeting. Teams that skip the branched nurture lose 80% of the funnel value.

This engine treats every webinar as a 4-week motion, not a 1-hour event. The 10% registrant-to-meeting conversion is what falls out of doing all three phases well.

## The stack

`Riverside` for recording · `HubSpot` for registration, landing pages, and nurture sequences · `n8n` for live engagement scoring and branching · `Canva` for design assets · `Claude` for topic relevance scoring and nurture copy

## Read more

Full case study with context on the portfolio website: **[shivsaurabh.netlify.app](https://shivsaurabh.netlify.app)**
