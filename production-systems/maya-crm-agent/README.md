# MAYA · CRM Lead Enrichment Agent

An autonomous Claude agent that runs every night at 9:30 PM IST. It fetches new CRM leads with no Target Account linked, resolves each one to the brand's real D2C ecommerce domain, dedupes against existing Target Accounts, writes the link back to Zoho CRM, and emails a digest. Built at [Growisto](https://growisto.com).

## What problem it solves

Sales teams capture leads at the person level. ABM motions need them at the account level. Manually matching every new lead to the right brand entity is slow, error-prone, and gets dropped first when the team is busy. The result is a CRM where half the leads are floating with no account context, ABM reports drift, and a lot of money walks out the door.

MAYA does the matching, every night, for every new lead, without supervision. With a safety net so it never breaks production CRM data.

## What is open here

| File | What it shows |
|---|---|
| [PLAYBOOK.md](./PLAYBOOK.md) | The actual instructions Claude reads every night. The agent is built on top of this. Sanitised of internal emails and live brand examples. |
| [**examples/sample-digest.md**](./examples/sample-digest.md) | A realistic example of the email MAYA sends after a run. Real format, sanitised data. Shows confidence-based routing, flag/skip handling, and the run metadata footer. |

Source code for the Python helper that talks to Zoho is internal to Growisto and not redistributed here. The architecture, the playbook structure and the patterns are all open.

## Architecture in one diagram

```
                       Cron at 9:30 PM IST
                              |
                              v
                   ┌────────────────────────┐
                   │  Claude Code wakes up  │
                   │  reads PLAYBOOK.md     │
                   └──────────┬─────────────┘
                              |
                              v
                   ┌────────────────────────┐
                   │  fetch_unlinked        │  (Python CLI → Zoho REST API)
                   │  → leads with no       │
                   │    Target Account      │
                   └──────────┬─────────────┘
                              |
                              v
              For each lead, Claude reasons:
                   ┌────────────────────────┐
                   │  Junk check            │  empty / "test" / personal name → skip
                   │  Domain resolution     │  WebSearch + WebFetch
                   │  D2C verification      │  add to cart + checkout present?
                   │  Country priority      │  country-matched first, global fallback
                   │  Confidence rating     │  high / medium / low
                   └──────────┬─────────────┘
                              |
              ┌───────────────┼───────────────┐
              v               v               v
       high or medium     low confidence    junk lead
              |               |               |
              v               v               v
       search_ta          flag in digest   queue delete request
              |               |               |
              v               v               v
       link_lead          email Saurabh    email Saurabh
       or create_ta       (no write)       (no write)
              |
              v
       write to Zoho
       (skipped in DRY_RUN)
                              |
                              v
                   ┌────────────────────────┐
                   │  Email digest to       │  Gmail SMTP
                   │  Saurabh + Anurag      │
                   │  signed "— MAYA"       │
                   └────────────────────────┘
```

## The architecture choices that matter

**Brain and hands separated.** Claude Code is the reasoning layer. It reads the playbook, decides what each lead is, picks an action. The Python helper (`zoho_helper.py`) is the action layer. It executes the write to Zoho through a CLI subcommand. This split means Claude cannot break production CRM data even if a prompt change goes wrong. The helper enforces its own rules.

**DRY_RUN safety net.** A `.env` flag the helper reads on every call. When `DRY_RUN=true`, the helper refuses every write. Whatever Claude decides to do, nothing reaches Zoho. The email digest still goes out, with a "DRY RUN" banner, so we can verify the reasoning was correct before flipping the flag. This is a code-level guardrail, not a prompt-level one. The model cannot override it.

**Playbook as the agent contract.** Every run starts fresh. Claude reads `MAYA_PLAYBOOK.md` from scratch each time, then follows its instructions. No chat history dependence. No drift across runs. The playbook is in git, versioned, reviewable. Same discipline engineering teams use for code, applied to the prompt that drives the agent.

**Confidence-based routing.** Claude is asked to score its own confidence on each decision. High and medium auto-associate. Low gets flagged in the digest for human review. The team would rather review five flagged leads a week than fix one wrong association. The threshold is in the playbook, not hardcoded — it can be tuned without redeploying anything.

**Per-run JSON logs.** Every run writes a timestamped JSON file with every lead's input, decision, action and outcome. If the team ever needs to ask "what did MAYA do with this lead last Tuesday" the answer is one file open away.

## The four daily outcomes

The morning after a run, the digest lands in inbox with one of these shapes:

```
MAYA digest · 2026-06-15 09:27 PM IST · live mode

Processed: 7 leads
  ✓ 5 linked to existing Target Accounts
  ✓ 1 new Target Account created and linked
  ⚠ 1 flagged for human review (low confidence)
  
Flagged:
  · Lead "Ramesh K." from "Skyline Trading" — country IN — could not verify D2C ecom 
    presence. Two candidate domains found. Reasoning attached. Please review.

Cleanups requested:
  · 2 junk leads (empty Company, gibberish "test asdf") — recommend delete.
```

The digest is the only human touch point in the normal case. Everything else is silent.

## Numbers

Numbers are from internal CRM data at Growisto. Specific brand examples are redacted from this public repo. The system has been live for several weeks at the time of writing.

- **Coverage** · Every new lead in the rolling 48 hour window gets a decision. None are dropped.
- **Auto-associate rate** · ~80% of leads resolve to high or medium confidence and auto-link.
- **Human flag rate** · ~15% surface as low confidence and need human review. Saurabh prefers this to wrong auto-associations.
- **Junk delete requests** · ~5% are clearly junk and get queued for deletion.
- **Manual time saved** · Estimated 3 to 4 hours per week of analyst time that was previously spent on lead-to-account matching.

## Why this pattern transfers to any agent that touches a system of record

The brain-and-hands split, the DRY_RUN flag, the playbook-as-contract, the confidence threshold and the per-run JSON logs are not specific to CRM. They are the foundation for any agent that writes to a database, a CRM, a billing system, a calendar, or anything else that has real consequences when it goes wrong.

Most agentic AI systems fail not because the model is bad, but because the routing is sloppy and the safety net is missing. MAYA is small but it has both. Once you build the discipline once, the next agent is half the work.

## Stack

Python 3.10 plus · Zoho CRM REST API · Gmail SMTP · Claude Code with the scheduled-tasks plugin · WebSearch and WebFetch tools for domain resolution

## What is in scope, what is not

In scope · Auto-associate leads to Target Accounts. Create new TAs when needed. Flag low confidence cases. Queue junk leads for human delete. Email digest.

Not in scope · Editing other lead fields. Auto-deleting any record. Enriching the Target Account with extra data (traffic, page speed, tech stack) — that is a separate workflow. Editing existing TA names (rename is dangerous and is left manual).
