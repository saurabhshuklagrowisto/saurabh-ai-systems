# ICP & Job-Post Scoring Rubric

Updated: 2026-07-10 · Owner: Scout (reads), Librarian (maintains)

## Who we sell to

Small and mid-size **US healthcare practices, MSOs, and medical billing companies** that are hiring for remote-friendly administrative roles we can fill with trained Philippines-based virtual staff at 40–60% lower cost.

- ✅ Solo / small practice (1–5 providers), mid-size group (6–25 providers, multi-location), dental practices, billing/RCM companies, MSOs
- ❌ Hospitals and large health systems (rigid, on-site, won't outsource offshore) — **hard disqualifier**
- Geography: US companies only (the job's employer must be US-based)

## Scoring: 0–100 per job posting

Start at 50, apply modifiers, clamp to 0–100. **Gate: score ≥ 70 goes to Clay enrichment.** Anything with a hard disqualifier scores 0.

### Hard disqualifiers (score = 0)

- Hospital or large health system employer
- Hands-on clinical duties: take vitals, room patients, draw blood/phlebotomy, injections, EKG, specimen collection, assist with exams, CNA/clinical MA certification, BLS/CPR required, scrubs
- Explicit legal blockers: "must be authorized to work in the US", "W-2 only", "no contractors/1099", in-person background check/fingerprinting

### Red flags (−15 to −30 each)

- "On-site", "in-office", "in person", "must report to our office", "local candidates only" (−30)
- Specific clinic address as work location with no remote option (−25)
- "Must live in [state]", "US-based only", "no remote" (−25)
- "Reliable transportation required", "valid driver's license", "travel between locations" (−20)

### Green flags (+10 to +20 each)

- "Remote", "fully remote", "work from home", "virtual", "telecommute", "anywhere" (+20)
- Duties match VA scope: answer phones, schedule appointments, appointment confirmations/reminders, verify insurance/eligibility, prior authorizations, data entry, medical records, billing, claims, AR follow-up, collections, referrals, patient intake paperwork (+15)
- EHR/EMR named: Athena, eClinicalWorks, Kareo, DrChrono, NextGen, Epic, etc. — cloud-based, accessible from anywhere (+15)
- Growth/pain signals: "high call volume", "growing practice", "multiple providers/locations", "need to scale", "backlog" (+10)
- Small/mid practice or billing company employer (+10)

### Output per job (Scout writes this)

```json
{
  "score": 0,
  "verdict": "qualified | deprioritized | disqualified",
  "reasons": ["..."],
  "practice_size_guess": "solo-small | mid-size | large | billing-company | unknown",
  "remote_signal": "explicit-remote | ambiguous | on-site"
}
```

Jobs with ambiguous remote signal but strong green flags elsewhere: cap at 69 (deprioritized pool, revisit if pipeline runs dry). The pitch works even for on-site-posted admin roles *if* duties are fully virtualizable — but explicit on-site language means the buyer isn't mentally ready; deprioritize, don't burn credits.
