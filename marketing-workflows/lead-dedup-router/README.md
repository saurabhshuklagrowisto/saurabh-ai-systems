# Lead Dedup & 28-Day Cooling Router (Clay)

**Flow 02 of the GTM workflow demos.**  
**Watch:** [loom.com/share/fff500d822e14e109e9d4cffd9aeb960](https://www.loom.com/share/fff500d822e14e109e9d4cffd9aeb960)


## What it does

Merges leads arriving from 5 different sources (ABM, Cold Outreach, Events, Webinars, Website), detects duplicate companies, ranks contacts by source priority, suppresses anyone contacted in the last 28 days, and surfaces one clean routing decision per row.

The output is a Clay table where every row has a `Route` column: **Enrich & Sequence**, **Skip (Cooling)**, or **Skip (Secondary)**. Only the primary contact for a unique company outside the cooling window moves forward.


## The core problem this solves

When leads come from multiple sources, the same company appears multiple times and often different contacts for the same company. Without dedup logic:
- The same company gets multiple outreach sequences running simultaneously
- Low-priority sources (website lead) block high-priority contacts (ABM) from being surfaced
- Recently contacted accounts (day 14 of a 28-day window) get hit again

This workflow enforces the rules automatically.


## Stack

| Tool | Role |
|---|---|
| Google Sheets / CSV | Pre-calculation of cross-row logic (dedup, priority ranking) |
| Clay | Single-row formula columns (date math, routing) |

**Key architectural insight:** Clay formula columns process row by row. They cannot do COUNTIF-style cross-row comparisons. Complex dedup and priority logic must be pre-calculated before import. Clay handles the last mile (date math, routing output) reliably.


## Architecture

```
Raw leads from 5 sources (CSV)
         │
         v
┌──────────────────────────────────────┐
│  Pre-calculation (outside Clay)      │
│  ────────────────────────────────    │
│  Duplicate Flag (per domain)         │
│  Email Check (unique email?)         │
│  Source Priority (1–5 score)         │
│  Contact Role (Primary / Secondary)  │
└───────────────┬──────────────────────┘
                │
                v
┌──────────────────────────────────────┐
│  Clay import                         │
│  ────────────────────────────────    │
│  Pre-calc columns come in as-is      │
│  Clay adds formula columns:          │
│    Days Since Contact                │
│    Cooling Status                    │
│    Route (final routing decision)    │
└───────────────┬──────────────────────┘
                │
                v
        Route determines action:
        ─────────────────────────
        Enrich & Sequence → push to outbound
        Skip (Cooling) → re-queue after 28 days
        Skip (Secondary) → hold, primary contact handles
```


## Pre-calculated columns (done before Clay import)

These are computed in a script or spreadsheet before the CSV is imported into Clay.

| Column | Logic |
|---|---|
| `Duplicate Flag` | Count of identical domains in the full dataset. `Duplicate` if count > 1, else `Unique` |
| `Email Check` | Is this email address unique? `OK` if unique, `Duplicate` if the same email appears twice |
| `Source Priority` | ABM=5, Cold Outreach=4, Event=3, Webinar=2, Website Lead=1 |
| `Contact Role` | If `Duplicate Flag` is Unique → Primary. If Duplicate and Source is ABM or Cold Outreach → Primary. Otherwise → Secondary |


## Clay formula columns (single-row, added inside Clay)

| Column | Formula |
|---|---|
| `Days Since Contact` | `TODAY() - Last Contacted Date` (blank if never contacted) |
| `Cooling Status` | `IF Days Since Contact < 28 THEN "In Cooling" ELSE "OK"` (blank if never contacted = OK) |
| `Route` | See routing logic below |

**Routing formula logic:**
```
IF Contact Role = "Secondary" → "Skip (Secondary)"
ELSE IF Cooling Status = "In Cooling" → "Skip (Cooling)"
ELSE → "Enrich & Sequence"
```


## Source priority why this order

| Source | Priority | Reasoning |
|---|---|---|
| ABM Outreach | 5 | Highest intent signal, handpicked account |
| Cold Outreach | 4 | Active outreach, warm |
| Event Lead | 3 | Met in person, short memory window |
| Webinar | 2 | Passive interest, lower signal |
| Website Lead | 1 | Earliest stage, lowest intent |

When two contacts exist for the same company, the one from the higher-priority source is marked Primary and sequenced first. The Secondary contact is held if the Primary doesn't reply, it can be promoted later.


## Demo data template

[`../../gtm-workflow-demos/demo-data-template.csv`](../../gtm-workflow-demos/demo-data-template.csv) 15 rows covering all routing scenarios: unique contacts, duplicate companies, cooling accounts, primary vs secondary contacts.


## Related

- [GTM workflow demos overview](../../gtm-workflow-demos)
- [Loom demo](https://www.loom.com/share/fff500d822e14e109e9d4cffd9aeb960)
