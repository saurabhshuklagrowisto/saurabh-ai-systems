# Scout pipeline, the code that is open

The two scripts that make up Scout, the data scraper and qualifier. This is the part of the system that is safe to share and runs on a fresh clone. Everything downstream, Clay enrichment, the sender, and the CRM, is credential bound and lives behind the orchestrator.

## What is here

| File | What it does |
|---|---|
| `scrape.py` | Pulls the target admin job titles across Indeed, ZipRecruiter, Google Jobs through JobSpy, plus Remotive, Jobicy, and RemoteOK through their free APIs. Normalizes everything into one schema, deduplicates on company and title, and writes a dated CSV. |
| `score.py` | The deterministic ICP scorer. Implements the full red flag and green flag rubric from `memory/icp-and-scoring/icp.md`. Reads the newest scrape, scores every posting 0 to 100, and writes a sorted, verdict tagged CSV. |

In production the scorer hands its ambiguous middle to Claude for a judgment pass. The rubric, the weights, and the output shape are identical, so the deterministic scorer here produces the same output structure the live system does, minus the language model refinement.

## Run it

```bash
python -m pip install python-jobspy requests
python scrape.py     # writes data/jobs_raw_<date>.csv
python score.py      # writes data/scored_<date>.csv
```

The scrape hits live job boards, so counts vary by day. A representative run pulled 259 unique US postings across 15 title queries and returned 10 qualified, 131 deprioritized, and the rest disqualified, with hospitals and large health systems filtered out automatically.

## How the scorer thinks

Every posting starts at 50. Hard blockers drop it to 0 immediately, clinical duties, licensed roles, hospitals and large systems, in person only requirements. Red flags subtract, on site language, must live in a state, W2 only as a soft signal. Green flags add, remote language, remote scope duties, a named cloud EHR, growth and pain signals, a small or mid sized employer. The gate is 70. An ambiguous remote signal caps the score at 69 so it lands in the nurture pool rather than paid enrichment. The full rubric and reasoning is in [OUTBOUND-ENGINE.md](../OUTBOUND-ENGINE.md).
