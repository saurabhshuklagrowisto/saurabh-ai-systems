# Job Scraping & Scoring for the Staffing Industry

A signal-scored outbound pipeline for a US healthcare-staffing agency (placing offshore virtual admin staff — receptionists, billers, schedulers, records clerks — into US medical and dental practices). Built as a demonstrably better rework of an existing open-source outbound dashboard, with a feedback-driven, eval-gated learning loop the original never had.

**Full build, live demo, and code:** [lead-scraping-plan](https://github.com/saurabhshuklagrowisto/lead-scraping-plan) · **Live demo:** [outbound command center](https://saurabhshuklagrowisto.github.io/outbound/) · **Production GTM home:** [QuickteamGTM/-lead-scraping-plan](https://github.com/QuickteamGTM/-lead-scraping-plan) (private — access on request)

## The core finding

The original AI scored postings against a **job-seeker** objective — it disqualified any posting that "requires US work authorization." But for a staffing *seller*, those US practices hiring junior admin roles **are the customers**, not a disqualifier.

Re-scoring 61 real human-rated postings against the corrected, staffing-seller objective:

| | Original AI | Re-oriented scorer |
|---|---|---|
| Agreement with human judgment | 67.2% | **77.0%** |
| Qualified leads wrongly discarded | 20 of 61 (33%) | **4 of 61 (6.6%)** |

One flipped assumption, re-derived from real human corrections rather than assumed, recovered 16 of 20 lost leads on the same data.

## What the system does

1. **Scrape** — JobSpy (Indeed) + a LinkedIn actor, free job-board APIs, deduped by company+title hash.
2. **Score** — a single, versioned rubric (`rubric.config.json`) read by both the Python scraper and the web app: hard disqualifiers (clinical duties, hospitals, over-senior titles), red/green signal weights, a free-text keyword pass with a Claude-refined ambiguous band, gated at ≥70 qualified / 40–69 nurture.
3. **Free size gate** — a public government registry (NPPES) check confirms company size *before* any paid enrichment credit is spent — catches large orgs masquerading as small practices.
4. **Account-centric CRM** — one account per company, open roles grouped as opportunities (not duplicate leads per posting); 3+ open roles boosts the account score, since one conversation can close multiple placements.
5. **Feedback → learning → eval gate** — every review writes structured feedback (verdict + reason tags + note). A candidate rubric/rule change must beat the current version on a locked, human-labeled holdout set before it's promoted — so "learning" can't silently regress, unlike prompt-stuffing approaches with no gate.
6. **MCP server** — the whole pipeline (`list_leads`, `submit_feedback`, `run_eval`, `teach_rule`, `pipeline_status`) is exposed as Claude tools, so it can be operated conversationally instead of only through a UI.

## Stack
Python (JobSpy scraper, deterministic scorer), a config-driven rubric shared across languages, a mobile-first dashboard (vanilla React via CDN-free vendored bundle, deployable as static or wired to Supabase/Next.js), and a Claude MCP server (Node).

## What's demonstrated vs. what's designed for scale
The public repo runs a full **DRY-RUN** demo end to end on real seed data (259 scraped postings, 61 real feedback labels) — scraping, scoring, the eval gate, and the account-centric CRM all work today with zero paid credentials. Enrichment, verified sending, and CRM sync are integration-ready (Clay, a verification tool, a sending platform, a CRM) and clearly labeled as stubbed until credentials are supplied — nothing sends or spends silently.

---
*Company-identifying details have been generalized; the architecture, numbers, and code are unchanged from the working build.*
