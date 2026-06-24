# Email and Newsletter Operations Overhaul

![Status](https://img.shields.io/badge/status-production-success?style=flat-square)
![Open rate](https://img.shields.io/badge/open_rate-14%25_to_29%25-22c55e?style=flat-square)
![CTR](https://img.shields.io/badge/CTR-1.4%25_to_3.8%25-22c55e?style=flat-square)

Took over and rebuilt the full lifecycle email and newsletter motion for a B2B client at [Growisto](https://growisto.com). Work spanned list hygiene, advanced segmentation, deliverability tuning, A/B testing, and AI-assisted copy generation across a high-cadence send schedule. Sends ran through Sendy (self-hosted on Amazon SES), which kept the per-send cost near zero at the 12,000-contact list size.

## The outcome

| Metric | Before | After |
|---|---|---|
| Open rate | 14% | **29%** |
| Click-through rate | 1.4% | **3.8%** |
| Contacts under management | 12,000 | 12,000 (held flat by hygiene, quality up) |
| Send cadence | Inconsistent | 6 sends per month |
| Deliverability | Domain warmup issues | Clean reputation, ~99% inbox placement |

## The architecture

```
   Existing lists
   (12,000 contacts)
        │
        v
   ┌─────────────────────────────┐
   │  Phase 1: Hygiene           │  Bounce removal, suppression
   │                             │  list sync, format fix
   └────────────┬────────────────┘
                │
                v
   ┌─────────────────────────────┐
   │  Phase 2: Segmentation      │  Engagement tier, lifecycle
   │  rebuild (Zoho CRM)         │  stage, industry, role
   └────────────┬────────────────┘
                │
                v
   ┌─────────────────────────────┐
   │  Phase 3: Deliverability    │  SPF/DKIM/DMARC, IP
   │  tuning                     │  warmup, content scoring
   └────────────┬────────────────┘
                │
                v
   ┌─────────────────────────────┐
   │  Phase 4: A/B testing       │  Subject lines, send time,
   │  framework                  │  CTA placement
   └────────────┬────────────────┘
                │
                v
   ┌─────────────────────────────┐
   │  Phase 5: AI-assisted       │  Claude generates first-draft
   │  copy generation            │  copy from a brief, human
   │                             │  edits the final version
   └────────────┬────────────────┘
                │
                v
   ┌─────────────────────────────┐
   │  Send · Sendy + SES         │  6 sends/month cadence
   │                             │  Self-hosted, ~zero per-send
   └────────────┬────────────────┘
                │
                v
   ┌─────────────────────────────┐
   │  Tracking · Looker Studio   │  Open, click, conversion,
   │  + GA4                      │  downstream pipeline
   └─────────────────────────────┘
```

## The workflow

1. **List hygiene first.** Before any send improvement, the list was cleaned: bounces removed, unsubscribes resynced, format errors fixed. This alone often recovers 2-5 points of open rate.
2. **Rebuild segmentation.** Instead of one list, the 12K contacts were split into segments inside Zoho CRM by engagement tier (hot/warm/cold), lifecycle stage (subscriber → MQL → customer), industry, and role. Each segment can receive different content cadence and tone.
3. **Deliverability tuning.** SPF, DKIM, DMARC records verified. IP warmup re-run after a period of inconsistent sending. Content scored against spam triggers before send.
4. **A/B testing framework.** Every send tests one variable: subject line, send time, or CTA placement. Wins compound. The framework keeps tests honest by setting minimum sample size before declaring a winner.
5. **AI-assisted copy.** Claude generates a first-draft from a content brief. A human edits the final version. This is the "brain and hands" pattern: Claude does the heavy lifting on draft 1, the human owns voice and final approval.
6. **Track downstream.** Every send pushes to Looker Studio for visibility, and GA4 tracks the on-site behavior of clickers. Open and click are leading indicators; pipeline conversion is the lagging indicator that actually matters.

## Where AI plugs in

- **First-draft copy generation** · Claude takes a content brief (audience, key message, CTA, length) and produces a draft. The human editor takes it the rest of the way.
- **Subject line A/B candidates** · Claude generates 5-10 subject line variants per send. The A/B test picks the winner.
- **Content scoring before send** · Claude rates the draft against deliverability heuristics (spam triggers, link density, CTA placement) and flags issues before the send goes out.

## Why the open rate doubled

Three reasons compounded:

1. **List hygiene** removed bounces and dead contacts that were tanking the sender reputation. Healthier reputation = better inbox placement.
2. **Segmentation** meant content matched the segment's interest, so engagement (open + click) rose on every send. Engagement signals to the inbox provider that the sender is wanted, which improves placement further.
3. **AI-assisted subject lines** plus systematic A/B testing surfaced winning patterns quickly. The team learned what worked across 60+ sends, applied learnings forward.

The fix was not "find a better email tool." It was discipline applied to the existing stack (Sendy for delivery, Zoho CRM for segmentation) with Claude doing the copy lift that used to take a full-time writer.

## The stack

`Sendy` (self-hosted on Amazon SES) for the actual sends · `Zoho CRM` for lifecycle automation and segmentation · `Claude` for first-draft copy and subject line variants · `Looker Studio` for dashboards · `GA4` for downstream tracking

## Read more

Full case study with context on the portfolio website: **[shivsaurabh.netlify.app](https://shivsaurabh.netlify.app)**
