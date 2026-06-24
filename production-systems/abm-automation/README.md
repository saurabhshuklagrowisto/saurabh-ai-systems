# ABM Automation Pipeline

Three coordinated workflows that take a list of brand domains and turn them into a CRM-loaded, contact-enriched, sales-team-actionable ABM pipeline. Built at [Growisto](https://growisto.com) for the inbound and outbound ABM motion.

## What problem it solves

The default ABM workflow at most agencies looks like this. Sales drops a list of brands in a sheet. An analyst manually checks each one against ICP criteria. Then manually pulls contacts via Apollo or LinkedIn Sales Navigator. Then manually pushes both to the CRM. Bottlenecks at every step.

This system replaces all three manual passes with three automated workflows, with humans only on the approval gates between them.

## The three workflows

| Workflow | Trigger | What it does |
|---|---|---|
| **1 · ICP Scoring & CRM Push** | Sales drops a CSV | Scores each brand against ICP, classifies it Cat 1–4 (India) or Cat 1–5 (USA), pushes approved accounts to Zoho CRM |
| **2 · POC Extraction** | Run after Workflow 1 approval | For each Target Account, pulls 1-2 marketing decision-maker contacts via Apollo (CMO, VP Marketing, Head of Growth, etc.) and pushes them to CRM Leads |
| **3 · Cliq Bot for real-time POC on demand** | Sales drops a brand name, LinkedIn URL or domain in the #abm-leads channel | Bot returns verified contact details in the channel, stages them to JSON, batches them to CRM at end of day |

## What is open here

| File | What it shows |
|---|---|
| [README.md](./README.md) | This doc. Architecture and patterns. |
| [methodology.md](./methodology.md) | How ICP scoring works, the title priority ladder, the Zoho field mapping, data sources, manual judgment calls |
| [icp-criteria-example.json](./icp-criteria-example.json) | Sample ICP criteria structure for India and USA (sanitised, generic categories) |
| [**code-samples/cliq-bot-parsing.py**](./code-samples/cliq-bot-parsing.py) | Sanitised Python showing the four parsing patterns (LinkedIn profile, LinkedIn company, domain, plain name), the skip-domain list, the title priority ladder, and how each parsed input routes to Apollo. Runnable example included at the bottom. |

The Python source files that talk to Apollo, Zoho and Cliq are internal to Growisto and not redistributed. The architecture and the methodology are open.

## Architecture in one diagram

```
   ┌──────────────────────────────────────────────────────────────────┐
   │  WORKFLOW 1 · ICP Scoring & CRM Push                             │
   │                                                                  │
   │   Sales CSV  ──►  Score against ICP  ──►  Approval table         │
   │                   (Cat 1-4 IN /                                  │
   │                    Cat 1-5 USA)             │                    │
   │                                              v                   │
   │                                       Push to Zoho               │
   │                                       Target_Accounts            │
   └──────────────────────────────┬───────────────────────────────────┘
                                  │
                                  v
   ┌──────────────────────────────────────────────────────────────────┐
   │  WORKFLOW 2 · POC Extraction                                     │
   │                                                                  │
   │   Approved TAs  ──►  Apollo people search  ──►  Title priority   │
   │                      (org domain +              ladder (CMO=1,   │
   │                       title list)               VP Marketing=2,  │
   │                                                  Founder/CEO=9)  │
   │                                                  │               │
   │                                                  v               │
   │                                            Push 1-2 POCs per TA  │
   │                                            to Zoho Leads         │
   └──────────────────────────────────────────────────────────────────┘

   ┌──────────────────────────────────────────────────────────────────┐
   │  WORKFLOW 3 · Cliq Bot for real-time POC on demand               │
   │                                                                  │
   │   #abm-leads channel  ──►  Cliq monitor polls every 5 min        │
   │                              │                                   │
   │                              v                                   │
   │                       Parse the message:                         │
   │                       - LinkedIn profile URL → people enrich     │
   │                       - LinkedIn company URL → company + people  │
   │                       - Domain → org enrich + people search      │
   │                       - Plain company name → company search      │
   │                              │                                   │
   │                              v                                   │
   │                       Reply in Cliq with contact card            │
   │                       Stage to daily JSON file                   │
   │                              │                                   │
   │                              v at 6:00 PM IST                    │
   │                       Daily batch push to Zoho Leads             │
   └──────────────────────────────────────────────────────────────────┘
```

## The architecture choices that matter

**Separate workflows, separate approval gates.** Workflow 1 is account-level (score and approve a set of brands). Workflow 2 is contact-level (pull POCs for approved accounts). Workflow 3 is real-time (a single brand, instant turnaround). Splitting them this way means each workflow has a clean input, a clean output, and a single owner. Mixing them would mean every change to one breaks the others.

**Human in the loop on every CRM write.** No workflow writes to CRM without a human approval step. The system can score 100 brands in 10 minutes but pushes nothing until the sales team reviews and approves. This is a guardrail against bad data flooding the CRM and against an enthusiastic LLM creating duplicate Target Accounts.

**ICP rules in JSON, not code.** The ICP criteria for India (Cat 1-4) and USA (Cat 1-5) live in `config/icp_criteria.json`. Sales can edit thresholds without touching Python. When the team decides "Cat 2 should require 100 employees not 80", it's one number in a JSON file, not a code deploy. Same separation of policy from mechanism that lets a marketing-led decision happen at marketing speed.

**Title priority ladder for POCs.** The system asks Apollo for many roles. Then it ranks the returned people by a priority ladder. CMO is priority 1. VP Marketing is priority 2. Head of Growth is priority 5. CEO and Founder are priority 9 (used as a fallback). The result is each Target Account gets the best-fit 1-2 contacts, not whoever Apollo happened to return first.

**Dedup against existing CRM before write.** Every Target Account write checks if the domain exists in the CRM. Every POC write checks if the email exists. The system never creates a duplicate, even when sales runs the same brand list twice by accident.

**Cliq Bot reuses Workflows 1 and 2 logic.** The real-time bot is not a separate codebase. It calls into the same Apollo-search and title-priority-ladder functions as the batch workflows. When the ladder gets updated, the bot gets the update for free.

**Daily batch push, not real-time push.** The Cliq bot stages POCs to a JSON file during the day, then pushes them all to CRM at 6 PM IST. This batches the writes (one CRM connection instead of many) and means humans can audit the day's POCs before they hit the CRM.

## Numbers

These numbers are from the system being live for several months at Growisto.

| Metric | Value |
|---|---|
| Brands scored against ICP | 92 in the first full batch |
| ICP categories codified | India Cat 1-4, USA Cat 1-5 |
| Apollo title queries cached | Priority-ranked list of 25+ titles |
| Cliq bot turnaround | ~30 to 90 seconds from drop to reply |
| Workflow 2 throughput | ~1 to 2 POCs per Target Account, 30+ TAs per batch |
| Manual time saved | An estimated full analyst day per week, moved to higher-leverage work |

## Why this pattern transfers

Any sales motion that involves "score a list, find contacts, push to CRM" fits this shape. The components — Apollo for people data, Zoho for CRM, Cliq for the real-time interface — are interchangeable. Replace Apollo with ZoomInfo or Hunter, replace Zoho with HubSpot or Salesforce, replace Cliq with Slack. The three-workflow split and the human-in-the-loop approval pattern stay the same.

The interesting bit is not the tools. It is that the system treats scoring, contact enrichment and real-time intake as three separate concerns with three separate approval gates, instead of trying to do all three in one big agent.

## Stack

Apollo.io · people search and enrichment, organization enrichment
Zoho CRM · Target_Accounts and Leads modules, with a dedup gate on every write
Zoho Cliq · the real-time channel where sales drops brand names
Python 3.10 · workflow runners
Claude · used in Workflow 1 for tech stack verification and in Workflow 3 for parsing messy Cliq messages

## Open items, honest scope

These are real items in the project tracker, included here so the picture is honest:

- Ahrefs MCP not connected; traffic data is manual or estimated, not automated yet
- USA brand batch has the config ready but has not been run end-to-end
- Workflow 3 has a `test_mode: true` flag that needs to flip to false for full production
- Lead assignment is single-owner; territory and vertical routing logic is not yet implemented
- Workflow 1 approval interface is a CLI table; a web UI would be friendlier for sales

These are real next steps. Building the system means knowing exactly where the seams are.
