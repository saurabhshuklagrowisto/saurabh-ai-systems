---
name: website-conversion-audit
description: Audits a B2B website page for conversion leaks from a buyer's lens and returns findings ranked by revenue impact. Takes a URL plus a set of observed page elements (hero message, CTAs, form fields, trust signals, mobile behaviour) and returns P0/P1/P2 findings, each with what was found, why it costs conversions, a concrete fix, and how to measure the fix. Use before a redesign, when diagnosing why demo requests are low, or to turn a landing page review into a prioritised action list.
---

# Website Conversion Audit Skill

Turns a subjective "this page feels off" into a scored, prioritised, measurable action list. Built from the buyer's point of view: the only question that matters is what stands between a qualified visitor and the action you want them to take.

## When to use

- Before a redesign, so effort goes to the findings that actually move revenue.
- When demo requests or sign-ups are lower than traffic justifies.
- To turn an informal landing-page review into a ranked, defensible plan.

## When NOT to use

- For pure performance/Core Web Vitals work — use Lighthouse/PageSpeed; this skill assumes the page loads fine and looks at the funnel.
- For content/SEO ranking — this is about converting the visitor who already arrived.

## Method: five conversion pillars

Every finding maps to one pillar and is scored by revenue impact, not effort:

1. **Clarity** — can a buyer tell what this is and who it is for within 5 seconds?
2. **CTA** — is the primary action obvious, singular, and low-friction?
3. **Form** — does the form ask only for what is needed, and can marketing route/score the lead?
4. **Trust** — is proof (logos, numbers, security) visible before the ask?
5. **Flow** — broken links, hidden assets, mobile breakage, dead ends.

## Severity

- **P0** — directly blocks or leaks conversions right now (broken CTA, hidden primary asset, form that can't be routed). Fix this week.
- **P1** — meaningful drag on conversion (weak hero, buried proof). Fix this month.
- **P2** — polish that compounds over time.

## Inputs

Required:
- `url` — the page audited
- `observations` — structured findings from a manual pass (see `scripts/audit_score.py` for the schema)

## Output (JSON)

A `verdict` line, a `pillar_scores` map, and `findings[]` sorted most-severe first, each with `pillar`, `severity`, `what`, `why`, `fix`, `measure`.

## Run it

```bash
python scripts/audit_score.py         # runs the built-in sample page
python scripts/audit_score.py page.json   # audits your own observations file
```

Runs with zero dependencies and no API keys. The scoring logic is deterministic and inspectable in `scripts/audit_score.py`.
