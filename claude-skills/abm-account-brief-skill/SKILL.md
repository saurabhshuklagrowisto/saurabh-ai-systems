---
name: abm-account-brief
description: Generates a hyper-personalized ABM account brief and outbound hook for a target B2B account. Takes a company domain plus optional context (recent signals, persona, ICP fit notes) and returns a structured brief with company snapshot, three personalization hooks ranked by strength, a recommended channel (email / LinkedIn DM / LinkedIn InMail), a 60-word cold email draft, and a confidence score. Use when researching a target account before outbound, when refreshing a stale prospect, or when generating hooks at scale across a target account list.
---

# ABM Account Brief Skill

Generates structured, evidence-based account briefs for B2B outbound. The output is designed to feed directly into a Smartlead / Apollo / LinkedIn Sales Navigator sequence with minimal human editing.

## When to use

- You are about to add a new account to a target list and need a brief before first touch.
- You are refreshing an account that has gone cold and need a new angle.
- You are running a batch (10-500 accounts) and want consistent, scoreable output.

## When NOT to use

- The account is already in active sales conversation — use the CRM record, not a fresh brief.
- The account is outside the defined ICP (see `references/icp-criteria.md`). Do not generate; return `out_of_icp: true` with the reason.
- You do not have at least one recent signal (news, hiring, funding, product launch, leadership change). Without a signal, hooks are generic and rep-time is wasted. Return `insufficient_signal: true` and surface what signal is missing.

## Inputs

Required:
- `company_domain` — root domain (e.g. `acme.com`)
- `persona` — one of: `CTO`, `VP Engineering`, `Director Marketing Technology`, `Head of RevOps`, `VP Sales`

Optional but recommended:
- `recent_signals` — list of {date, type, source_url, summary}; types: `funding`, `hiring`, `product_launch`, `leadership_change`, `press`, `linkedin_post`
- `prior_touches` — list of {date, channel, outcome}
- `account_owner_notes` — free text from the rep

## Output schema (JSON)

```json
{
  "company": {
    "name": "string",
    "domain": "string",
    "industry": "string",
    "size_band": "1-50 | 51-200 | 201-1000 | 1001-5000 | 5000+",
    "hq_country": "string",
    "one_line_what_they_do": "string"
  },
  "icp_fit": {
    "in_icp": true,
    "score_0_to_10": 8,
    "rationale": "string"
  },
  "hooks": [
    {
      "rank": 1,
      "angle": "string (one sentence, what the hook is)",
      "evidence_url": "string (must be a real URL from recent_signals or public web)",
      "why_it_lands_for_persona": "string"
    }
  ],
  "recommended_channel": "email | linkedin_dm | linkedin_inmail",
  "channel_rationale": "string",
  "cold_email_draft": {
    "subject_line": "string (max 50 chars, no emojis, no salesy verbs)",
    "body": "string (max 60 words, plain text, single CTA, no jargon)"
  },
  "confidence_0_to_10": 7,
  "confidence_rationale": "string",
  "guardrails_triggered": []
}
```

## How the model should reason

1. **Verify ICP fit first.** Read `references/icp-criteria.md`. If the company fails any hard criterion (industry exclusion, sub-scale headcount, wrong geo), return `out_of_icp: true` and stop. Do not generate hooks for non-ICP accounts.
2. **Find the strongest signal.** Rank `recent_signals` by recency (last 30 days > last 90 days > older) and specificity (a named person's LinkedIn post > a corporate press release). The top signal anchors hook #1.
3. **Generate three distinct hooks.** Each must cite a different evidence point. No hook may be a paraphrase of "I saw your company is growing" — that is generic and will be rejected by the eval.
4. **Match channel to persona and signal type.** Leadership change or LinkedIn post → LinkedIn DM. Funding or product launch → email with a clear business framing. Hiring signal for a senior role → LinkedIn InMail to the hiring manager.
5. **Write the email.** 60 words MAX. Subject line cannot contain: `quick`, `touching base`, `circling back`, `synergy`, `leverage`, `unlock`. The body must reference the evidence URL's content (not just exist), state one specific value claim, and end with a single low-friction CTA (a question, not a meeting ask).
6. **Score confidence honestly.** If you had to stretch on evidence, say so. Confidence below 5 means the rep should not send this without human review.

## Guardrails

The Skill enforces these before returning output. If violated, add to `guardrails_triggered` and either fix or refuse:

- **No fabricated evidence.** Every `evidence_url` must come from `recent_signals` or be a URL you have been given. Do not invent URLs.
- **No PII inference.** Do not guess personal details (family, health, politics, religion) from the persona's profile.
- **No competitor name-drops** unless they are in the public signal itself.
- **Subject line length** ≤ 50 chars. Body ≤ 60 words. Hard caps.
- **Banned subject-line phrases** (see step 5 above).
- **Output must be valid JSON** matching the schema. No prose outside the JSON.

## Eval loop

This Skill is regression-tested against `golden_set.jsonl`. Run `python scripts/score_output.py` after any prompt change. The eval scores on:
- Schema validity (binary)
- Evidence grounding (every hook's URL appears in the input signals)
- Hook diversity (no two hooks paraphrase the same signal)
- Subject/body length compliance
- LLM-as-judge rating of hook quality vs the golden hook (1-5)

See `prompts/v1.md` and `prompts/v2.md` for version history. v2 added the "no generic growth hooks" instruction after v1 failed the diversity check on 3/10 golden cases.
