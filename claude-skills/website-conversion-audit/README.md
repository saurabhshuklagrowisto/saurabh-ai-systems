# Website Conversion Audit

Audits a B2B web page from the buyer's point of view and returns findings ranked by revenue impact, not effort. Turns "this page feels off" into a scored, measurable action list.

## What it does

Input: a URL plus a structured set of observations from a manual pass (hero clarity, CTA count, whether the CTA works, form fields, trust signals, mobile, broken links).

Output: a one-line verdict, a per-pillar count, and findings sorted most-severe first. Every finding carries **what** was found, **why** it costs conversions, a concrete **fix**, and how to **measure** the fix.

## The method

Five conversion pillars — Clarity, CTA, Form, Trust, Flow — each scored by revenue impact:

- **P0** leaks conversions right now (broken CTA, hidden primary asset, unrouteable form). Fix this week.
- **P1** drags on conversion (weak hero, buried proof). Fix this month.
- **P2** compounding polish.

## How to run

```bash
python scripts/audit_score.py             # built-in sample page
python scripts/audit_score.py page.json   # your own observations
```

Zero dependencies, no API keys. See `demo_output.json` for a real run: 6 findings, 3 P0, ranked and measurable.

## Why it is built this way

The scoring is deterministic and lives in `scripts/audit_score.py` — every finding is traceable to a rule, so the output is defensible in front of a stakeholder rather than a black box. The judgment layer (a human or an LLM doing the manual pass) produces the observations; the engine turns them into a consistent, prioritised, scoreable report.
