# Sample MAYA Digest Email

A real (sanitised) example of what MAYA emails out at 9:30 PM IST after a run.
This is the only human touchpoint in the normal case. Everything else is silent.

Brand names, lead IDs, and the internal Zoho org link have been redacted.
The shape and the language are exactly the production format.

---

```
From:    MAYA <maya-bot@example.com>
To:      [marketing operator email]
Cc:      [BD lead email]
Subject: MAYA digest · 2026-06-15 · 7 leads processed (5 linked, 1 new, 1 flagged)
```

---

**MAYA digest · 2026-06-15 09:27 PM IST · live mode**

Processed: **7 leads** from the last 24 hours

- ✓ 5 linked to existing Target Accounts
- ✓ 1 new Target Account created and linked
- ⚠ 1 flagged for human review (low confidence)
- ⛔ 2 junk leads queued for delete

---

## Auto-linked (high confidence)

| # | Lead | Company | Country | → Target Account | Confidence |
|---|---|---|---|---|---|
| 1 | Easwar B. | [REDACTED brand A, beauty D2C] | IE | [REDACTED domain].com | high |
| 2 | Priya R. | [REDACTED brand B, fashion D2C] | IN | [REDACTED domain].in | high |
| 3 | Vikram K. | [REDACTED brand C, electronics] | IN | [REDACTED domain].com | high |
| 4 | Sarah M. | [REDACTED brand D, USA SaaS] | US | [REDACTED domain].com | medium |
| 5 | Aman G. | [REDACTED brand E, India D2C] | IN | [REDACTED domain].in | high |

## Auto-linked, NEW Target Account created

| # | Lead | Company | Country | New TA created | Confidence |
|---|---|---|---|---|---|
| 6 | Rohit S. | [REDACTED new brand] | IN | [REDACTED domain].in | high |

Reasoning: Country-matched D2C ecom site verified (cart + checkout present).
No existing Target Account found. Created new TA and linked.

## Flagged for human review

| # | Lead | Company | Country | Reason |
|---|---|---|---|---|
| 7 | Ramesh K. | "Skyline Trading" | IN | Could not verify D2C ecom presence. Two candidate domains found, both look like marketplace listings, not the brand's own site. Please review. |

**Suggested action:** Open the lead in Zoho [link], review the two candidate domains in the reasoning attached below, and either confirm one or mark for nurture without TA link.

## Junk leads · delete requests

| # | Lead | Company | Reason for skip |
|---|---|---|---|
| - | "test" | "asdf" | Gibberish company, looks like a form test |
| - | Anonymous | (empty) | No company name, no email domain, personal name only |

Recommend deleting both manually. MAYA does not auto-delete.

---

## Run metadata

- Run started: 2026-06-15 21:27:12 IST
- Run finished: 2026-06-15 21:27:43 IST (31 seconds total)
- Helper calls: 13 (5 search_ta, 1 create_ta, 7 link_lead)
- Helper errors: 0
- Mode: `DRY_RUN=false` (live)
- Log file: `logs/run_20260615_212712.json`

— MAYA

---

## What this example demonstrates

This is the output of a system that:

1. **Reasoned about 7 individual leads** in sequence, resolving each one to a real ecommerce domain through WebSearch and WebFetch
2. **Made confidence-based decisions** about which leads to auto-link versus flag for human review
3. **Created exactly one new Target Account** where none existed (no duplicates)
4. **Refused to act on junk data** — flagged 2 junk leads for human cleanup instead of trying to process them
5. **Logged the run completely** in a JSON file for audit
6. **Sent this digest as the only human touchpoint** — no notifications during processing, no chatty status updates

The agent runs every night at 9:30 PM IST. The team usually sees this email by 9:32 PM, reviews flags within a day, and never has to think about CRM-lead-to-account matching as a manual task.

Architecture and the full playbook in [../README.md](../README.md) and [../PLAYBOOK.md](../PLAYBOOK.md).
