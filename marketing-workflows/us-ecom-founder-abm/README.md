# ABM Outbound to US eCommerce Founders

![Status](https://img.shields.io/badge/status-production-success?style=flat-square)
![Channel](https://img.shields.io/badge/motion-account--based_outbound-7c3aed?style=flat-square)
![Region](https://img.shields.io/badge/region-USA-1e40af?style=flat-square)

An account-based outbound motion targeting founders of US eCommerce companies. I build the target account lists, the account-specific hooks, and the multichannel sequences that turn a curated list of founders into booked meetings. Apollo for the contact data, Claude for per-account personalization, Lemlist for multichannel delivery. Built for a client at [Growisto](https://growisto.com).

## The outcome

| Metric | Value |
|---|---|
| Qualified meetings booked | 25+ per month |
| Influenced pipeline | ~$1.2M across 6 months |
| Reply rate | 6%+ (industry baseline: 1 to 3%) |
| Target ICP | Founders of US eCommerce brands |

## The architecture

```
   Target list: US eCommerce brands
            │
            v
   ┌─────────────────────────────┐
   │  Apollo + Clay enrichment   │  Find the founder, verify email
   │                             │  and LinkedIn, pull company signals
   └────────────┬────────────────┘
                │
                v
   ┌─────────────────────────────┐
   │  ICP gate                   │  Is this a real D2C eCommerce brand
   │  (Claude reasoning)         │  with a founder worth a 1:1 touch?
   └────────────┬────────────────┘
                │
                v
   ┌─────────────────────────────┐
   │  Per-account hooks          │  Claude writes founder-level hooks
   │  (Claude + signals)         │  grounded in a real company signal
   │                             │  (launch, funding, store, press)
   └────────────┬────────────────┘
                │
                v
   ┌─────────────────────────────┐
   │  Lemlist multichannel       │  Email + LinkedIn touches per
   │  sequence                   │  founder, paced over the cadence
   └────────────┬────────────────┘
                │
                v
   ┌─────────────────────────────┐
   │  Reply handling + Zoho CRM  │  Replies triaged, meetings booked,
   │                             │  every touch logged for attribution
   └─────────────────────────────┘
```

## The workflow

1. **Build the founder list.** Start from a list of US eCommerce brands that fit the ICP. Apollo and Clay resolve the founder, verify the email and LinkedIn, and pull recent company signals (new launches, funding, store changes, press).
2. **Gate on ICP.** Claude checks each account is a real D2C eCommerce brand with a founder worth a personal, founder-level touch. Off-ICP accounts are flagged, not contacted.
3. **Write founder-level hooks.** For each surviving founder, Claude writes account-specific hooks anchored to a real signal. Generic "saw you are growing" openers are rejected; every hook references something specific about that brand.
4. **Run the Lemlist multichannel sequence.** Lemlist delivers the founder outreach across email and LinkedIn, paced over the cadence. Founder-to-founder framing, not a vendor pitch.
5. **Handle replies and book.** Replies are triaged, meetings booked, and every touch is logged to Zoho CRM for attribution.

## Where AI plugs in

- **ICP gate** · Claude reads the enriched account and decides whether the founder is worth a 1:1 touch before anyone is contacted.
- **Founder-level hook generation** · Claude writes the personalization for each founder, anchored to a real company signal. This is what makes founder outreach land instead of reading like spray-and-pray.
- **Reply triage** · Claude classifies inbound replies and proposes the next step (book, nurture, or hand to the founder for a personal reply).

## Why founder-to-founder ABM, not blast outbound

Founders do not respond to volume. They respond to a relevant, specific message that respects their time and clearly comes from someone who looked at their brand. So this motion is deliberately account-based: a curated list, real research per account, a hook tied to a real signal, and a multichannel cadence that earns attention across email and LinkedIn rather than hammering one inbox. The reply rate is a multiple of cold-list-blast outbound because the personalization is real.

## The stack

`Apollo` for founder contact data · `Clay` to orchestrate enrichment · `Claude` for the ICP gate, founder-level hooks, and reply triage · `Lemlist` for the multichannel email + LinkedIn sequence · `Zoho CRM` as the system of record

## Related

The multichannel cadence used to book in-person founder meetings is documented as its own workflow: [Lemlist Multichannel Meeting Booking](../lemlist-meeting-booking).

## Read more

Full case study with context on the portfolio website: **[shivsaurabh.netlify.app](https://shivsaurabh.netlify.app)**
