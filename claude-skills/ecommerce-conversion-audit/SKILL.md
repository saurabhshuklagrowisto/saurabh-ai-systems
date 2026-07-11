---
name: ecommerce-conversion-audit
description: Audits a D2C / eCommerce store for conversion leaks along the path to purchase and returns findings ranked by revenue impact. Takes a URL plus observed elements across the product page, cart, and checkout (imagery, price clarity, add-to-cart, guest checkout, steps, payment options, shipping surprises, reviews, returns, urgency, mobile) and returns P0/P1/P2 findings, each with what was found, why it costs revenue, a concrete fix, and how to measure it. Use before a store redesign, when the add-to-cart or checkout conversion rate is low, or to turn a store review into a prioritised action list. This is the D2C counterpart to the B2B website-conversion-audit skill.
---

# eCommerce (D2C) Conversion Audit Skill

The B2B audit optimises the path to a booked demo. This one optimises the path to a completed purchase — a different funnel entirely: product page, add-to-cart, and checkout, where most revenue leaks between "interested" and "paid."

## When to use

- Before a store redesign, so effort goes where revenue actually leaks.
- When traffic is healthy but add-to-cart or checkout completion is low.
- To turn a store review into a ranked, measurable action list for a D2C brand.

## When NOT to use

- For a B2B lead-gen / demo funnel — use the `website-conversion-audit` skill instead.
- For pure site speed / Core Web Vitals — use Lighthouse; this assumes the store loads and looks at the buying funnel.

## Method: six D2C conversion pillars

1. **Product (PDP)** — imagery, benefit-led copy, price clarity.
2. **Cart** — is add-to-cart obvious and frictionless; is the cart easy to reach and edit.
3. **Checkout** — guest checkout, step count, payment options, no forced account creation.
4. **Cost transparency** — shipping and total shown early, not sprung at the final step (the #1 abandonment cause).
5. **Trust** — reviews on the PDP, visible returns policy, secure-payment badges.
6. **Urgency + Mobile** — scarcity/offers where honest, and a mobile-first experience (most D2C traffic is mobile).

## Severity

- **P0** — directly blocks or leaks purchases now (broken checkout, no guest checkout, shipping surprise at the final step).
- **P1** — meaningful drag (no reviews on PDP, price buried, too many checkout steps).
- **P2** — compounding polish.

## Inputs

Required:
- `url` — the store / product page audited
- `observations` — structured findings from a manual pass (schema in `scripts/ecom_audit_score.py`)

## Output (JSON)

A `verdict`, a per-pillar count, and `findings[]` sorted most-severe first, each with `pillar`, `severity`, `what`, `why`, `fix`, `measure`.

## Run it

```bash
python scripts/ecom_audit_score.py           # built-in sample store
python scripts/ecom_audit_score.py store.json # your own observations
```

Zero dependencies, no API keys. Deterministic scoring in `scripts/ecom_audit_score.py`.
