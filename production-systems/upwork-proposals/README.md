# Upwork Proposal Automation

A Claude plugin built at [Growisto](https://growisto.com) that scans Upwork for Shopify and ecommerce jobs, scores them on a 16-dimension rubric, runs a brand-permission audit before any client name is cited, and generates expertise-first PDF proposals with industry-matched portfolio examples.

**Note on what is open here.** The plugin source code is internal to Growisto. This README describes the architecture and the patterns that are reusable. The actual prompts, the portfolio database, and the permission audit content are not redistributed.

## What problem it solves

Upwork is a viable channel for B2B agency work, but two things make it hard at scale. First, the volume of available jobs makes ranking what to bid on a real triage problem. Second, the cost of getting a single proposal wrong (citing a client without permission, attaching a portfolio that does not match, missing a TOS rule) is high enough that proposals end up taking 30 to 45 minutes each. At low conversion rates, that math does not work.

This plugin automates the triage and the proposal so a real human only spends time on the parts that matter — the bid amount, the qualifying question, the final review before send.

## The two skills

| Skill | Trigger | What it does |
|---|---|---|
| `upwork-scan` | Manual or scheduled | Scans Upwork across 19 saved queries (9 Tier 1). Scores each job with the 100-point rubric. Posts ranked results to a Zoho Cliq channel. Presents per-job recommendations for what to research next. |
| `upwork-proposal` | Given a job URL | Generates a tight cover letter, a multi-page PDF proposal with 3 industry-matched portfolio examples, and a step-by-step "how to apply on Upwork" terminal summary. |

## Architecture in one diagram

```
   ┌────────────────────────────────────────────────────────────────────┐
   │  /upwork-scan                                                      │
   │                                                                    │
   │   Phase 0 · Preflight (dedup load, date folder)                    │
   │   Phase 1 · Search 19 queries via Chrome MCP                       │
   │   Phase 2 · Score with the 100-point system (16 dimensions)        │
   │   Phase 3 · Notify · Post to Zoho Cliq                             │
   │   Phase 4 · Per-job recommendations (interactive)                  │
   │                                                                    │
   └────────────────────────────┬───────────────────────────────────────┘
                                │
                                v  user picks a job
                                │
   ┌────────────────────────────────────────────────────────────────────┐
   │  /upwork-proposal [job URL]                                        │
   │                                                                    │
   │   Phase 0 · Preflight (type detect, check pre-existing analysis)   │
   │   Phase 1 · Research (conditional store-auditor +                  │
   │              attachment-reviewer)                                  │
   │   Phase 2 · Strategy (scope and price)                             │
   │              │                                                     │
   │              v                                                     │
   │   ┌──────────────────────────────────────────┐                     │
   │   │  Brand Permission Audit Gate             │                     │
   │   │  Every cited client name must clear      │                     │
   │   │  the permissions_audit.json file         │                     │
   │   │  · approved · denied · unconfirmed       │                     │
   │   │  Denied brands are silently skipped      │                     │
   │   └──────────────────────────────────────────┘                     │
   │              │                                                     │
   │              v                                                     │
   │   Phase 3 · Content (cover letter + PDF + work deck attachment)    │
   │   Phase 4 · Terminal summary                                       │
   │              · Job link and client details                         │
   │              · Bid amount + milestones + boost                     │
   │              · Cover letter (copy-paste ready)                     │
   │              · Screening answers                                   │
   │              · Step-by-step "how to apply on Upwork"               │
   │              · Local PDF path                                      │
   └────────────────────────────────────────────────────────────────────┘
```

## The architecture choices that matter

**16-dimension scoring system, transparently weighted.** The 100-point scoring rubric is the result of running real proposals through it and tuning the weights based on which factors actually predicted "the client viewed the proposal". Sample weights:

| Factor | Points | Why |
|---|---|---|
| Client open rate above 70% | +15 | Strongest single predictor of being viewed at all |
| Brief specificity | +10 | Specific briefs convert at multiples of vague ones |
| Portfolio match on key stack (Klaviyo, ReCharge, etc.) | +3 | Higher hit rate on listings the agency has done before |
| AU and NZ client | +5 | Over-index on Shopify spend in this market |
| Screening questions present | +5 | Signals an engaged buyer |
| Fixed price + 100+ proposals already | -8 | Low ROI even with heavy boost spend |

The full rubric lives in source. Sharing the structure here so the pattern is reproducible.

**Brand Permission Audit Gate is the most important guardrail.** Many agencies cite client work in proposals freely. This is a real legal and ethical risk. Some clients have explicitly denied permission to use their name in marketing. Others have approved logo use but not case study text. The plugin runs every cited brand through a permission audit file (`permissions_audit.json`) before it ever ends up in a cover letter. Denied brands are silently skipped. Unconfirmed brands are skipped. Only `approved` and `team_override` (where the team has verbal confirmation) get cited.

This means a wrong cover letter cannot ship even if a sales rep would have manually included a denied brand by mistake. The discipline is enforced in code, not in prompt instructions.

**TOS-compliant proposal format, hard rules in source.** Upwork's TOS bans certain content in cover letters (off-platform contact, LinkedIn URLs in proposals, phone numbers, personal emails). The plugin enforces these as hard rules:

- LinkedIn URL banned in cover letter and signature
- Phone numbers and personal emails banned
- Domain URLs banned for past-client examples (NAME ONLY allowed, no `discoverpilgrim.com`)
- One highlighted external link per cover letter, pointing to the Growisto-hosted portfolio

These are not soft suggestions in a prompt. They are validation rules the plugin applies before the proposal is finalised.

**Per-user Zoho Cliq integration via personal MCP.** The plugin does not ship a Zoho Cliq token. Instead, each teammate adds their own Cliq MCP URL as a personal Claude connector. The reason: messages posted to channels appear under the actual person who scanned, not a shared bot account. The team can see who is bidding on what, instead of every message looking like it came from a robot.

**Industry-matched portfolio rotation.** The plugin holds a 44-brand portfolio database segmented by industry. When generating a proposal for a beauty brand, it cites 3 beauty portfolio examples. For a fashion brand, 3 fashion examples. Same industry match logic applies to tech stack (Shopify expertise, Magento expertise, etc.). The portfolio choice is data-driven, not LLM-generated.

**Expertise-first cover letter format, not problem-first.** The default agency cover letter starts with "We understand your challenges around..." and feels generic. The expertise-first format starts with one tight paragraph mirroring the problem, then immediately moves to credentials (years of experience, project count, key client examples). The qualifying question goes at the end, not the beginning. Tested against the problem-first format; the expertise-first version had a higher response rate.

## Numbers

| Metric | Value |
|---|---|
| Queries scanned per run | 19 (9 Tier 1 + 10 secondary) |
| Scoring dimensions | 16, weighted to a 100-point total |
| Permission audit base | 600+ CRM records audited, every cited brand checked |
| Portfolio database | 44 brands, segmented by industry and tech stack |
| Proposal turnaround | From job URL to ready-to-send PDF in under 5 minutes |
| Manual time saved per proposal | Roughly 25 to 35 minutes versus writing from scratch |

## Why this pattern transfers

Any agency or service business that bids on a marketplace (Upwork, Fiverr, Toptal, Catalant, even RFPs) faces the same shape of problem: triage incoming opportunities, run a compliance gate on what can be cited, generate a tailored proposal that does not break platform rules. The architecture in this plugin is reusable for any of these.

The permission audit gate is especially transferable. Any business that cites past work in marketing should have a single source of truth for what is approved versus denied. Without it, the path from "I think we have permission" to "we cited a client we did not have permission for" is one careless cover letter.

## Stack

Claude plugin format · standard `commands.toml` + `agents/` + `references/` + `skills/` layout
Chrome MCP · live browser for Upwork search and form fill
Playwright MCP · headless browser for store audit screenshots
PageSpeed API · baked into the proposal pipeline for performance audits
Zoho Cliq MCP · per-user connector for channel posts (not shipped)
PDF generation · Chrome headless print-to-PDF
Output structure · per-scan and per-proposal date-stamped folders so runs are auditable
