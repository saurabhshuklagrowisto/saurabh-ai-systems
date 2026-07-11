# The Outbound Engine

A fresh job posting is one of the most honest buying signals a company puts on the internet. A post that reads "hiring a medical biller" does not just mean they want a biller. It means they have an open seat, a budget already approved for it, and a pain real enough today that someone wrote the ad. The engine is built entirely around catching that signal early and acting on it while it is still live.

The vertical here is a staffing company that places trained remote talent with US businesses, using healthcare administrative roles as the example. The mechanics, job postings as intent signals, relevance scoring, decision maker enrichment, and a personalized sequence, are general B2B outbound and transfer to any vertical.

## The six stages

```
1 scrape  ->  2 qualify  ->  3 enrich  ->  4 write  ->  5 send  ->  6 hand to sales
```

Stages 1 and 2 are Scout. Stage 3 is Finder. Stages 4 and 5 are Scribe. Stage 6 is the sales rep. Atlas moves each lead between them.

## Stage 1, scrape the demand

Every morning, before most people have opened their inbox, Scout pulls the target admin job titles across the US, deduplicates them, and normalizes them into one schema. A posting only enters if the employer is a US company, the post is under fourteen days old so the seat is likely still open, and it is not already in the pipeline.

**Sources, ranked by real yield.** A live test made the ranking obvious. Indeed alone produced about ninety five percent of the qualified leads.

- Primary, and nearly all the volume: Indeed, ZipRecruiter, Google Jobs, all through JobSpy for free.
- Secondary, small but free, kept running: Remotive, Jobicy, RemoteOK, We Work Remotely.
- Worth adding for pure fit: niche healthcare admin boards.
- Low priority, very little volume, deprioritized: Monster, Wellfound, Remote.co, and the tech only hiring threads.

**A detail worth keeping.** Indeed shows the posted salary on most postings and the scraper captures it. That number becomes the arithmetic in the outreach later. If a company has budgeted a certain rate for a seat, the email can quote it and show the same work done for a fraction. A posting with three or more open seats at once is tagged as a priority account, since that is one conversation and several placements.

## Stage 2, qualify with the relevancy rubric

Every posting starts at 50 points. Flags move it. The gate is set at 70. Only postings at 70 or above spend any money downstream. This is the single control that keeps the enrichment budget small. A free keyword pass removes the obvious rejects first, then Claude judges the ambiguous middle at a fraction of a cent per posting.

**Hard blockers, scored 0 immediately.** These need a body in a room, not a remote assistant.

- Hands on clinical duties. Take vitals, room patients, phlebotomy, injections, EKG, specimen collection, assist with exams.
- Clinical certifications. CNA, clinical MA, BLS or CPR certified, scrubs.
- Licensed roles. Nurse, therapist, provider, pharmacist.
- Hospitals and large health systems. Usually rigid, on site, and will not outsource offshore.
- In person fingerprinting.

**Red flags, deprioritized rather than deleted.**

- On site, in office, in person, must report to our office, local candidates only. Minus 30.
- A clinic address as the work location with no remote option, or must live in a named state, or no remote. Minus 25.
- Reliable transportation, driver's license, travel between locations. Minus 20.
- Must be authorized to work in the US, W2 only, no contractors. Treated as a soft signal, not a kill. The staffing company contracts with the business and never employs the worker directly, so this language mainly signals a cautious buyer worth a softer approach.

**Green flags.**

- Remote, work from home, virtual, telecommute, anywhere. Plus 20.
- Duties that match the remote scope. Phones, scheduling, confirmations, insurance verification, prior authorizations, data entry, records, billing, claims, AR follow up, collections, referrals, intake paperwork. Plus 15.
- A cloud EHR or EMR named. Athena, eClinicalWorks, Kareo, DrChrono, NextGen, Epic, Dentrix. Reachable from anywhere. Plus 15.
- Pain and growth signals. High call volume, growing practice, multiple locations, backlog. Plus 10.
- A small or mid sized practice, a dental office, a billing company, or an MSO. Plus 10.

**The gate.**

- 70 and above goes to enrichment.
- 40 to 69 goes to a nurture pool, a second and softer education track. These businesses have not accepted remote help yet, but the duties are often fully virtualizable, so this pool is usually the larger market over time.
- Below 40 is archived. Still useful as a wage benchmark.
- An ambiguous remote signal caps the score at 69, keeping it out of paid enrichment until it looks clearer.

## Stage 3, enrich and find the buyer

Free checks first, paid credits last, at most two or three contacts per company.

**NPPES first, for free.** The US government provider registry gives the official practice phone and address and the number of providers billing at that address. That last number is a free company size check. It kills oversized organizations before a single Clay credit is spent. This is the control that caught a two thousand person firm that read as a small billing shop on its name alone.

**Then Clay for the company.** Name, location, website, number of facilities, staff count, and estimated revenue. The size verdict confirms or corrects the earlier guess and routes the decision maker lookup.

**The decision maker waterfall, keyed to size.**

- Solo or small practice, one to five providers, at most two contacts. Owner or physician or dentist owner, then office manager or practice manager. The owner is usually the decision maker.
- Mid sized group, six to twenty five providers and multi location, at most three contacts. Practice administrator, then director of operations, then the billing or revenue cycle manager if the group is billing heavy.
- A billing or revenue cycle company, a different buyer since they resell labor themselves. Owner or CEO, then director of operations, then client services manager.

**The lead record and the credit guards.** Name, title, LinkedIn, a verified email, and a phone. Email is verified before any send so bounce rate stays under three percent. The suppression list is checked so an opted out company never re enters. Cost per enriched lead and the enrichment match rate are reviewed weekly.

## Stage 4, write the sequence

A five touch sequence, written from the actual posting, never a generic blast.

- Touch 1, day 0. The opening. Same duties, trained remote staff, at a large discount to a local hire. A line about the named EHR if there is one.
- Touch 2, day 3. Proof. One short case study with numbers. Hours saved, dollars saved, a two week ramp.
- Touch 3, day 7. Objection preempt. A dedicated person, US hours, trained on the compliance the vertical needs, an agreement signed.
- Touch 4, day 12. The arithmetic. Their posted salary plus benefits against the monthly rate for the same duty list.
- Touch 5, day 18. Breakup with a one pager. Live in two weeks if the search drags.

Claude personalizes each email from the posted job title, two duties quoted from the posting, the named EHR, the posted salary, the practice size, the pain signals, and the decision maker first name and role. Copy rules keep it under 120 words, one idea per email, plain text with no links or images in the first two touches, a positioning that never reads as cheap offshore labor, and a compliant footer with a physical address and a working unsubscribe on every send. A human approves the copy before any of it goes out.

## Stage 5, send

Cold volume never goes out from the main domain, and never from a CRM that cannot warm inboxes.

- Two or three secondary sending domains, never the main one, with SPF, DKIM, and DMARC configured.
- Permanent inbox warmup and rotation through Smartlead or Instantly. At most fifty cold sends per inbox per day.
- The suppression list is checked before every send and opt outs are honored instantly.
- The watch list. Spam complaints under 0.2 percent, bounces under three percent, domain health tracked per inbox.
- Opens, replies, and bounces come back by webhook around the clock. A positive reply goes to stage 6 instantly and every event is logged to the lead state and to memory.

## Stage 6, hand to sales

The rep calls a warm lead with everything on one card, and runs their own call sequence, exactly as the original brief asked.

- The context card, attached automatically in Close. The posting and its link, the posted salary, the company facts, the full email thread, which touch converted, and the savings arithmetic ready to quote.
- The rep call sequence, in Close. Call one within an hour of the reply, since speed wins deals. A voicemail and a short email on day one, a second call on day three, a final email on day seven. The goal is a fifteen minute discovery call and a placement proposal.
- Closing the loop. Every outcome, won or lost and why, is written back to company memory and the experiment log. Won deals become case studies, so touch 2 gets stronger every month.

## Tool decisions and the reasons

| Stage | Tool | Why this one |
|---|---|---|
| Scraping | JobSpy for Indeed, ZipRecruiter, Google Jobs, plus free APIs, plus Apify for LinkedIn | Indeed carries most US healthcare admin postings and JobSpy scrapes it free with no rate limit. The remote boards cost nothing. LinkedIn is the only source worth paying for. |
| Size check | NPPES, the free government provider registry | Confirms practice size at zero cost before a single paid enrichment credit. Catches large firms a company name alone can miss. |
| Scoring | Keyword filter, then Claude on the ambiguous middle | The free filter removes obvious rejects instantly. Claude only judges the cases that actually need judgment. |
| Enrichment | Clay | Company facts and a decision maker waterfall, limited to two or three contacts per company to protect credits. |
| Cold sending | Smartlead or Instantly | Permanent inbox warmup and rotation, which a CRM does not provide. Protects domain reputation for cold volume. |
| CRM and calling | Close | Where a reply becomes a lead record and the rep call sequence begins. |
| Sequence writing | Claude plus a fixed master template | Every email personalized from the actual posting, with the posted salary used for real arithmetic where available. |

## What protects the budget

1. The score gate at 70, before any Clay credit is spent. Hospitals and clinical roles are rejected at zero cost.
2. At most two or three contacts per company, chosen by practice size. No shotgun lookups.
3. Email verification before sequencing, so bounces stay under three percent.
4. A suppression list, so an opted out company is never sequenced again.
5. A weekly review of cost per enriched lead and cost per booked call.
