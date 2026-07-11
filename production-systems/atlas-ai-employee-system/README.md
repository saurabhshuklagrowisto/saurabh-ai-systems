# ATLAS · AI Employee System

One orchestrator agent running a team of five specialist agents end to end. Atlas schedules the work, moves every lead through a strict state machine so nothing is ever lost or contacted twice, retries its own failures, and only wakes a human when a decision actually needs one. The five employees underneath it run an outbound engine and a content engine, both feeding one shared company memory that makes the whole system smarter every week.

Built as a full agentic system for a staffing company that places remote talent with US businesses. Client identity is anonymized throughout. The architecture, the code that is safe to share, and the real scraper output are all here.

## What problem it solves

Small go to market teams lose their week to the same repetitive work. Finding opportunities, qualifying them, researching the buyer, writing the outreach, publishing content, and keeping track of what actually worked. Hiring more people to do that work is slow and expensive. Automating one piece of it with a single script solves one tenth of the problem and creates a new one, an unmonitored job that silently breaks.

Atlas treats the whole motion as an org chart instead of a script. Each job goes to a focused agent that does one thing well. One orchestrator owns the schedule, the state, the retries, the budget, and the escalations. A human stays in control at exactly two points, and the system grades itself against real numbers every week rather than running on trust.

## The roster

| Agent | Job | Runs on |
|---|---|---|
| **Atlas** | The orchestrator. Schedules every run, dispatches the five employees, tracks every lead through the state machine, retries failures, escalates blockers, sends the daily digest. | Claude Agent SDK, cron |
| **Scout** | Finds the buying signal. Scrapes fresh job postings across the US every morning and scores each one 0 to 100 against the ideal customer profile. | Claude, JobSpy, free job APIs |
| **Finder** | Turns a qualified posting into a contactable buyer. Confirms company size for free, then enriches the decision maker with a verified email and phone. | NPPES registry, Clay |
| **Scribe** | Writes the outreach. A five touch sequence built from the exact posting, never a generic blast, sent from warmed inboxes. | Claude, Smartlead or Instantly |
| **Publicist** | Runs the content engine. Studies competitors, drafts a weekly calendar, generates the video or post, and publishes it on schedule. | Wonda AI |
| **Librarian** | Keeps the whole system smart. Files every outcome into company memory, consolidates weekly, and serves fresh playbooks to every other agent. | Claude, git backed markdown |

## The outbound engine

The core motion runs daily, in six stages. A fresh job posting is one of the most honest buying signals a company puts on the internet. It means an open seat, an approved budget, and a real pain today. The engine catches that signal early and acts on it while it is still live.

```
  Scout            Scout            Finder           Scribe          Scribe          Sales rep
  scrape    -->    qualify   -->    enrich    -->    write    -->    send     -->    book the call
  25 titles        score 0-100      NPPES + Clay     5 touch         warmed          Close CRM
  US only          gate at 70       verified buyer   from posting    domains         call sequence
                        |                                 |                                |
                        v                                 v                                v
                   only 70+ spends              a human approves               every outcome logged
                   any money                    the copy                       back to memory
```

Full detail, including the complete red flag and green flag scoring rubric, the free company size check that protects the enrichment budget, and the deprioritized nurture track, is in [OUTBOUND-ENGINE.md](./OUTBOUND-ENGINE.md).

## What is open here

| File | What it shows |
|---|---|
| [**ATLAS-ORCHESTRATOR.md**](./ATLAS-ORCHESTRATOR.md) | The full orchestration spec. The daily and weekly schedule, the lead state machine, the retry and budget rules, the two human approval gates, and the weekly evaluation loop that lets the system grade itself. |
| [**OUTBOUND-ENGINE.md**](./OUTBOUND-ENGINE.md) | The six stage outbound engine in depth, with every scoring rule, the tool decisions and the reasons behind them, and the budget guardrails. |
| [**AI-EMPLOYEES.md**](./AI-EMPLOYEES.md) | The five employees and the company memory in detail. What each reads, what it writes back, and the contract that keeps them coordinated. |
| [**code/**](./code) | The working Scout pipeline. A real scraper across Indeed and the free job boards, and the deterministic ICP scorer that implements the rubric. Runs on a fresh clone. |
| [**memory/**](./memory) | The company memory structure the Librarian maintains. ICP and scoring rules, the master email sequence, the decision maker matrix, and the deliverability playbook. Genericized. |
| [**diagrams/**](./diagrams) | The system diagram, the outbound engine diagram, and a five slide LinkedIn carousel of the engine. |

The Clay tables, the sending infrastructure, and the client specific memory are not redistributed. The architecture, the scraper, the scorer, and the patterns are all open.

## Proof it is real, not a slide

The Scout pipeline in [`code/`](./code) was run live against Indeed and the free job boards. In one morning it pulled 259 unique US job postings across 15 title queries and scored every one against the rubric. 10 came back qualified, 131 deprioritized into the nurture track, and the rest disqualified, with hospitals and large health systems filtered out automatically. One company that read as a small billing shop on its name turned out to be a two thousand person firm, caught by the company size check before a single enrichment credit was spent. That miss is exactly why the free size check sits before any paid step, and why the weekly evaluation loop keeps tightening the filter instead of treating it as solved.

## Stack

Claude Agent SDK for the agents. Python for the deterministic pipelines. SQLite moving to Postgres for the lead state. Git backed markdown for company memory. Wonda AI for content generation and publishing. Clay for enrichment, with the free NPPES provider registry as a size check in front of it. Smartlead or Instantly for warmed cold sending, with Close as the CRM and the rep call sequence. New tooling spend lands around $135 to $400 a month, since the scraping is free and the scoring gate keeps the paid enrichment small.

## The one honest caveat

Company size detection by name alone will always miss some large organizations. That is why the free registry check runs before any paid enrichment, and why every large organization that slips through and reaches Clay is added to the exclusion list automatically. The system is built to catch what slips, not to pretend nothing does.

<div align="center">

Part of [Saurabh Shukla · AI Systems](../../README.md)

</div>
