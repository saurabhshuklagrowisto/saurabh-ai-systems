# ICP Scoring Formula — eCommerce ABM List Builder

Each dimension contributes 1 point. Total score is 0–5. Routing is determined by threshold.

---

## Dimension 1 — Platform Tier

**Source:** BuiltWith enrichment via Clay (or Clay Tech Checker)  
**Signal:** Is the brand on Shopify Plus?

**Clay formula:**
```
IF Platform contains "Shopify Plus" THEN 1 ELSE 0
```

**Why Shopify Plus matters:**  
Shopify Plus brands have crossed $1M+ GMV, have a dedicated merchant success manager, and have budget for agency relationships. Base Shopify is a different buyer entirely.

---

## Dimension 2 — Monthly Traffic

**Source:** SimilarWeb enrichment via Clay  
**Signal:** 50,000+ monthly visitors

**Clay formula:**
```
IF Monthly Traffic >= 50000 THEN 1 ELSE 0
```

**Why 50K:**  
At 50K+ monthly visitors, conversion rate improvements (CRO, email, SEO) generate meaningful revenue upside. Below this the absolute dollar impact is too small to justify agency spend.

---

## Dimension 3 — Employee Count

**Source:** Apollo enrichment via Clay  
**Signal:** 11–200 employees

**Clay formula:**
```
IF Employee Count >= 11 AND Employee Count <= 200 THEN 1 ELSE 0
```

**Why 11–200:**  
This range captures brands that are past founder-only stage (enough budget and process to work with an agency) but not yet enterprise (where procurement and long sales cycles make the motion uneconomic for us).

---

## Dimension 4 — Replatforming Signal

**Source:** BuiltWith technology history via Clay  
**Signal:** Platform change detected in the last 12 months

**Clay formula:**
```
IF Replatform Signal is not empty THEN 1 ELSE 0
```

**Why replatforming:**  
A brand that just moved platforms is in active re-evaluation mode. They have budget unlocked, new vendor relationships open, and a team actively thinking about their tech stack. Warm signal.

---

## Dimension 5 — Industry Fit

**Source:** Apollo enrichment via Clay  
**Signal:** Industry tag matches eCommerce / DTC / Retail / Consumer Goods

**Clay formula:**
```
IF Industry contains "eCommerce" OR "Direct to Consumer" OR "Retail" OR "Consumer Goods" OR "Apparel" OR "Health" THEN 1 ELSE 0
```

**Why explicit industry check:**  
Apollo sometimes tags brands under Software or Services when their SaaS layer is more prominent than their retail operation. This check ensures we are targeting brands that actually sell physical or digital products to consumers.

---

## Total score and routing

**Total score column (Clay formula):**
```
Platform Score + Traffic Score + Employee Score + Replatform Score + Industry Score
```

**Tier routing column:**
```
IF ICP Score >= 4 THEN "Tier 1 — Outbound Now"
ELSE IF ICP Score >= 2 THEN "Tier 2 — Nurture"
ELSE "Not a Fit"
```

---

## What Tier 1 means downstream

Tier 1 accounts flow to the AI Generate column (Claude hook) and then into Lemlist automatically. Tier 2 accounts go into a separate Clay table for re-enrichment in 60 days. Not a Fit accounts are archived.

The hook generation prompt only fires on Tier 1 accounts — no point generating a personalised hook for a brand that will not be sequenced.
