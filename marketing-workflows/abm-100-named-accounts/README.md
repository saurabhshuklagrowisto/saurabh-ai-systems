# ABM Playbook · 100 Named US B2B Accounts

![Status](https://img.shields.io/badge/status-production-success?style=flat-square)
![Channels](https://img.shields.io/badge/channels-paid_%2B_outbound_%2B_events-7c3aed?style=flat-square)
![Region](https://img.shields.io/badge/region-USA-1e40af?style=flat-square)

A multi-touch Account-Based Marketing motion combining LinkedIn paid, outbound sequences, and offline US event activation, run against a curated list of 100 named US B2B accounts. Built for a client at [Growisto](https://growisto.com).

## The outcome

| Metric | Value |
|---|---|
| First meetings booked | 32 out of 100 named accounts in 90 days |
| Engagement lift on tier-1 accounts | 3x versus pre-program baseline |
| Influenced pipeline from event ABM | ~$410K |
| US conferences activated | 4 |
| Channels orchestrated | Paid (LinkedIn), Outbound (cold email), Offline (events) |

## The architecture

```
   100 named accounts
       │
       v
   ┌──────────────────────────┐
   │  Clay-driven enrichment  │  Each account scored on
   │  (firmographic + people) │  ICP fit, buying committee
   │                          │  mapped (3-5 personas / acc)
   └────────────┬─────────────┘
                │
                v
   ┌──────────────────────────────────────────────┐
   │            Parallel multi-channel touch      │
   │                                              │
   │  ┌──────────────┐ ┌──────────────┐ ┌──────┐  │
   │  │ LinkedIn Ads │ │  Smartlead   │ │ Field│  │
   │  │ (paid retarg)│ │  (outbound)  │ │ event│  │
   │  └──────┬───────┘ └──────┬───────┘ └──┬───┘  │
   │         │                 │            │     │
   └─────────┼─────────────────┼────────────┼─────┘
             │                 │            │
             v                 v            v
   ┌──────────────────────────────────────────────┐
   │  HubSpot · account-level engagement scoring  │
   │  Each account scored on combined activity    │
   │  across all 3 channels                       │
   └────────────────────┬─────────────────────────┘
                        │
                        v
   ┌──────────────────────────────────────────────┐
   │  Tier promotion (engagement above threshold) │
   │  → assigned to AE                            │
   │  → high-intent nurture sequence              │
   └──────────────────────────────────────────────┘
```

## The workflow

1. **Build the 100-account list.** Sales and marketing agreed on the named accounts. Clay enrichment pulled firmographic data (size, tech stack, recent funding), and Apollo enriched buying-committee personas (typically 3-5 contacts per account: CMO, VP Marketing, Head of Growth, plus a CXO sponsor).
2. **Persona mapping.** For each account, the buying committee was mapped explicitly. Outreach varied by persona role.
3. **Coordinated multi-channel.** LinkedIn Ads ran retargeting against the account list. Smartlead delivered an outbound sequence per persona. Field event activation happened at 4 US conferences across the year.
4. **Engagement scoring.** HubSpot scored each account based on combined activity across paid, outbound, and event touchpoints. The score is account-level, not contact-level, which is the right unit for ABM.
5. **Tier promotion.** When an account crossed the engagement threshold, it was promoted to an AE for warm follow-up. The promotion was the gate that triggered manual outreach by sales.
6. **Post-event nurture.** Attendees from the 4 conferences entered a tailored nurture sequence based on which session they attended and which booth they engaged with.

## Where AI plugs in

- **Account scoring** · Claude reads enrichment data and rates fit against the ICP rubric, surfacing the 100 from a broader funnel.
- **Persona-specific copy** · Claude generates outbound copy variants by persona role within each account. A CMO gets different messaging than a Head of Growth at the same company.
- **Event signal extraction** · Post-event, Claude reads attendance and engagement data (badge scans, session attendance) and proposes the right nurture path for each attendee.

## Why this differs from generic outbound

Outbound at the contact level treats every person as their own funnel. ABM at 100 accounts treats the **account** as the funnel, and the 3-5 people inside it as a buying committee that needs to be moved together. Engagement scoring rolls up to account level. Tier promotion happens at account level. The AE inherits the account, not just a lead.

## The stack

`Clay` for firmographic and people enrichment · `LinkedIn Ads` for paid retargeting · `Smartlead` for outbound sequences · `Apollo` for buying-committee data · `HubSpot` for account-level scoring and tracking · `Claude` for persona-specific copy and account scoring

## Read more

Full case study with context on the portfolio website: **[shivsaurabh.netlify.app](https://shivsaurabh.netlify.app)**
