# eCommerce (D2C) Conversion Audit

Audits a D2C store along the path to purchase — product page, cart, checkout — and returns findings ranked by revenue impact. The D2C counterpart to the B2B `website-conversion-audit` skill: same discipline, different funnel.

## What it does

Input: a store/product URL plus a structured manual pass (imagery, price clarity, add-to-cart, guest checkout, checkout steps, payment options, shipping transparency, reviews, returns, trust badges, urgency, mobile).

Output: a one-line verdict, a per-pillar count, and findings sorted most-severe first — each with **what** was found, **why** it costs revenue, a concrete **fix**, and how to **measure** it.

## The six D2C pillars

Product (PDP) · Cart · Checkout · Cost transparency · Trust · Urgency + Mobile — scored by revenue impact:

- **P0** leaks purchases now (broken checkout, forced account creation, shipping sprung at the final step).
- **P1** drags conversion (no PDP reviews, price buried, too many checkout steps, one payment option).
- **P2** compounding polish.

## How to run

```bash
python scripts/ecom_audit_score.py            # built-in sample store
python scripts/ecom_audit_score.py store.json # your own observations
```

Zero dependencies, no API keys. See `demo_output.json` for a real run: 8 findings, 2 P0, ranked and measurable.

## Why it is built this way

B2B and D2C leak revenue in completely different places — a demo form versus a checkout flow — so they get separate skills rather than one blurry "website audit." The scoring is deterministic and lives in `scripts/ecom_audit_score.py`, so every finding traces to a rule and the report is defensible in front of a founder, not a black box. The single biggest D2C lever it enforces: never spring shipping cost at the final step, and never force account creation — the two most documented causes of cart abandonment.
