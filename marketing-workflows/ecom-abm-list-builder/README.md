# eCommerce ABM List Builder (Clay)

**Flow 01 of the GTM workflow demos.**  
**Watch:** [loom.com/share/997c367778694035a9b237e48021178c](https://www.loom.com/share/997c367778694035a9b237e48021178c)

---

## What it does

Takes a raw list of eCommerce brand domains, enriches each one through Clay, scores them across 5 ICP dimensions, and routes qualified accounts into personalised outbound sequences in Lemlist with AI-generated hooks.

The output is not just a scored list — it is a list where every Tier 1 account has a ready-to-send personalised hook that references something specific to that company.

---

## Stack

| Tool | Role |
|---|---|
| Clay | Enrichment orchestration, formula columns, AI Generate |
| BuiltWith (via Clay) | Platform detection (Shopify Plus vs base) |
| SimilarWeb (via Clay) | Monthly traffic |
| Apollo (via Clay) | Employee count, industry tag |
| Claude (via Clay AI Generate) | Personalised hook generation |
| Lemlist | Outbound sequence, receives hook as variable |

---

## Architecture

```
Raw domain list (CSV or manual input)
         │
         v
┌────────────────────────────────────┐
│  Clay enrichment layer             │
│  ─────────────────────────────     │
│  BuiltWith → platform tier         │
│  SimilarWeb → monthly traffic      │
│  Apollo → employees, industry      │
└──────────────┬─────────────────────┘
               │
               v
┌────────────────────────────────────┐
│  ICP scoring (formula columns)     │
│  5 dimensions → score 0–5          │
│  Route: Tier 1 / Tier 2 / No Fit  │
└──────────────┬─────────────────────┘
               │
               v
┌────────────────────────────────────┐
│  AI Generate (Claude)              │
│  Reads enrichment data             │
│  Writes 1-sentence account hook    │
│  Output → Lemlist variable field   │
└──────────────┬─────────────────────┘
               │
               v
┌────────────────────────────────────┐
│  Routing                           │
│  Tier 1 → push to Lemlist sequence │
│  Tier 2 → hold for nurture         │
│  No Fit → archive                  │
└────────────────────────────────────┘
```

---

## ICP scoring logic

See [`icp-scoring-formula.md`](./icp-scoring-formula.md) for the full formula breakdown per dimension.

**Summary:**

| Dimension | Signal | Threshold |
|---|---|---|
| Platform tier | Shopify Plus | 1 point if Shopify Plus |
| Monthly traffic | SimilarWeb | 1 point if 50K+ visits/month |
| Employee count | Apollo | 1 point if 11–200 employees |
| Replatforming signal | BuiltWith history | 1 point if platform change detected |
| Industry fit | Apollo industry tag | 1 point if eCommerce / DTC / retail |

**Total → Tier:**  
- 4–5 → Tier 1 (Outbound Now)  
- 2–3 → Tier 2 (Nurture)  
- 0–1 → Not a Fit

---

## Personalisation hook prompt (Clay AI Generate)

```
You are writing the opening line of a cold outbound email to {{Company Name}}.

Context:
- Platform: {{Platform}}
- Monthly visitors: {{Monthly Traffic}}
- Employees: {{Employee Count}}
- Industry: {{Industry}}
- Replatforming signal: {{Replatform Signal}}

Write one sentence (under 20 words) that references something specific to this company's growth or tech setup. 
Sound curious, not salesy. Do not mention Growisto. Do not use generic phrases like "I noticed" or "I came across".
Output only the sentence. No quotes, no punctuation at the end.
```

---

## Proof

Screenshot of the working Clay table with all columns visible in [`proof/clay-screenshot.png`](./proof/clay-screenshot.png).

Company names blurred in the screenshot. Columns visible: Platform, Traffic, Employees, Replatform Signal, Industry, ICP Score, Tier, Hook.

---

## Related

- [ICP scoring formula detail](./icp-scoring-formula.md)
- [Loom demo](https://www.loom.com/share/997c367778694035a9b237e48021178c)
- [GTM workflow demos overview](../../gtm-workflow-demos)
