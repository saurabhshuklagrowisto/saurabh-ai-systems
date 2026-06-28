# GTM Workflow Demos

Three live-recorded workflow walkthroughs covering Clay enrichment, lead deduplication, and n8n automation. Each one is a pattern I run or have adapted from production at Growisto.

---

## Flow 01 · ICP Scoring & Personalized Hooks (Clay)

**Watch:** [loom.com/share/997c367778694035a9b237e48021178c](https://www.loom.com/share/997c367778694035a9b237e48021178c)

**Stack:** Clay · Apollo · Lemlist · Claude

**What it does:**  
Score inbound eCommerce brand lists across 5 ICP dimensions in Clay, then route qualified accounts straight into personalised outbound sequences.

**The 5 scoring dimensions:**

| Dimension | Signal | Source |
|---|---|---|
| Platform tier | Shopify Plus vs base Shopify vs other | BuiltWith / Clay tech check |
| Monthly traffic | 50K+ threshold | SimilarWeb enrichment |
| Employee count | 11–200 range | Apollo / Clay enrichment |
| Replatforming signal | Recent platform switch | BuiltWith history |
| Industry fit | eCommerce / DTC / retail | Apollo industry tag |

**Scoring formula:**  
Each dimension scores 1 point. Threshold rules applied per dimension. Total 0–5:  
- 4–5 → **Tier 1 / Outbound Now**  
- 2–3 → **Tier 2 / Nurture**  
- 0–1 → **Not a Fit**

**Personalisation hook (AI Generate column):**  
Claude reads platform tier + traffic + recent company signals and writes a one-sentence opening hook specific to each account. Fed directly to Lemlist as a variable.

**Why this matters:**  
Without scoring, SDRs reach out to every name on a list. With scoring, only accounts that pass all 5 dimensions move forward. The personalisation column means every email opens with a sentence that could only be written about that specific company.

---

## Flow 02 · Multi-Source Dedup & 28-Day Cooling (Clay)

**Watch:** [loom.com/share/fff500d822e14e109e9d4cffd9aeb960](https://www.loom.com/share/fff500d822e14e109e9d4cffd9aeb960)

**Stack:** Clay · Google Sheets

**What it does:**  
Merge leads from 5 sources (ABM, Cold Outreach, Event, Webinar, Website), detect duplicate companies, rank POCs by source priority, suppress accounts contacted in the last 28 days, and surface one clean outreach-ready record per company.

**Source priority (pre-calculated before Clay import):**

| Source | Priority score |
|---|---|
| ABM Outreach | 5 |
| Cold Outreach | 4 |
| Event Lead | 3 |
| Webinar | 2 |
| Website Lead | 1 |

**The key insight — what Clay can and cannot do:**  
Clay formula columns process row by row. They cannot count across rows (no COUNTIF equivalent). Complex cross-row logic — duplicate detection, priority ranking — must be pre-calculated before import. Clay handles single-row math (date calculations, routing logic) reliably. This demo shows exactly where to split the work.

**Pre-calculated in CSV (before Clay):**
- `Duplicate Flag` — Unique / Duplicate (count of domain in full list)
- `Email Check` — OK / Duplicate (uniqueness of email address)
- `Source Priority` — numeric score from source name
- `Contact Role` — Primary / Secondary based on Duplicate Flag + Source Priority

**Clay formula columns (single-row, reliable):**
- `Days Since Contact` — `TODAY() - Last Contacted Date` → numeric
- `Cooling Status` — `IF Days Since Contact < 28 THEN "In Cooling" ELSE "OK"` (or blank if never contacted)
- `Route` — final routing decision: Enrich & Sequence / Review / Skip (Cooling) / Skip (Secondary)

**Demo data template:** [`demo-data-template.csv`](./demo-data-template.csv)

---

## Flow 03 · AI Meeting Summary Pipeline (n8n)

**Watch:** [loom.com/share/0b27759116c9460789147810a4391261](https://www.loom.com/share/0b27759116c9460789147810a4391261)

**Stack:** n8n · Claude · Fireflies · Google Drive

**What it does:**  
A webhook-triggered n8n workflow that fires the moment Fireflies finishes processing a recording. It disambiguates which client the meeting belongs to using Claude, files the transcript to the right Google Drive folder, generates a context-aware summary, and emails it to the team.

**Node-by-node breakdown:**

| Stage | Nodes | What happens |
|---|---|---|
| **Trigger & intake** | Fireflies Webhook → Extract Meeting ID → Fetch Transcript → Internal call filter | Fireflies POSTs on recording completion. Pull full transcript via API. Skip internal team calls. |
| **Brand disambiguation** | Extract Brand Hint → Check Folder Cache → Claude disambiguation → Low confidence gate | Claude gets attendee list + meeting title + client list. Returns brand name + confidence score. Low confidence → flag email to human. New brand → auto-create Drive folder. |
| **File structure** | Check/create Transcripts subfolder → Check/create Summaries subfolder → Upload transcript | Ensure folder structure exists before writing. |
| **Summary & delivery** | Check for previous summary → Download if exists → Claude generate summary → Upload summary → Internal check → Send email | Previous summary fed as context so Claude writes a continuation, not a one-off. Email only sent if Growisto team was on the call. |

**The canonical key pattern:**  
Claude's output brand name becomes the key that links transcript filing, summary storage, and CRM records. Without a consistent canonical brand name, you cannot join across systems. This is the same pattern the Brand Name Normalizer (separate workflow) enforces at ingestion.

**Why context-aware summaries matter:**  
A summary written with no knowledge of prior meetings lists facts. A summary written with the last summary as context identifies what changed, flags broken commitments, and surfaces the decision trajectory. This is the meaningful difference for account managers reviewing 8–10 client meetings a week.

---

## The pattern these three flows share

All three are examples of the same underlying architecture:

1. **Pre-process outside the tool** — put complex cross-row or cross-system logic in a script or CSV before it enters Clay or n8n. The tool handles the last mile.
2. **Route, don't act** — every output is a routing decision (Enrich, Nurture, Skip, Flag). The action happens downstream once a human or system has reviewed the route.
3. **Confidence gates** — ambiguous or low-confidence outputs get flagged to a human rather than silently filed or sequenced. Nothing reaches a customer without a clear-confidence result.

These are the same principles documented in [ARCHITECTURE.md](../ARCHITECTURE.md) and across the production systems.
