# Atlas, the Orchestrator

Atlas is the one agent that runs everything else. The five employees are specialists. Atlas is the layer that decides when each of them runs, moves every lead through a strict state machine so nothing is lost or contacted twice, retries its own failures, holds the budget, and only wakes a human when a decision genuinely needs one.

## Runtime

The orchestrator and the five employees all run on the Claude Agent SDK. Atlas is the supervisor. Scout, Finder, Scribe, the Librarian, and the Publicist are subagents with scoped tools. The Python scripts in [`code/`](./code) are the deterministic hands that do the actual scraping, scoring, and file work. Agents call them, they never reinvent them. Scheduling is cron, on Windows Task Scheduler now and a small VPS later. Lead state lives in SQLite now and Postgres at scale. Memory is the git backed markdown the Librarian maintains.

## The daily and weekly schedule

Atlas owns the clock. Employees never schedule themselves.

| When | What Atlas dispatches |
|---|---|
| 07:00 daily | Scout scrapes every source, deduplicates, and scores each posting against the relevancy rubric. |
| 08:00 daily | Finder runs the free company size check on every score of 70 or above, then pushes the survivors to Clay for enrichment. |
| 09:00 daily | Scribe drafts a personalized sequence for every newly enriched lead and places it in the approval inbox. |
| On approval | Scribe pushes the approved sequence to the sending tool with the personalization fields attached. |
| Continuous | Reply, open, and bounce events arrive by webhook at any hour. A positive reply creates the lead in Close, assigns a rep, and starts the rep call sequence within the hour. |
| 17:00 daily | A digest goes to the founder. Postings found, qualified, enriched, sequenced, replies, calls booked, and spend against the monthly caps. |
| Friday | The Publicist runs its weekly content cycle. Research, calendar, creatives, approval, publish. |
| Sunday | The Librarian consolidates company memory. Files the week's outcomes, removes duplicates, flags anything stale. |
| Monday | The weekly evaluation runs and any rubric or template updates are written back into memory. |

## The lead state machine

Every single lead moves through the same fixed sequence of states, and only Atlas is allowed to change a lead's state. This one rule is what prevents duplicate outreach and lost leads as volume grows.

```
scraped -> scored -> enriching -> enriched -> draft -> approved -> in_sequence
        -> replied -> handed_off -> call_booked -> won | lost | suppressed
```

The rules that make it safe:

1. Only Atlas writes a state transition. Employees return results. Atlas commits them.
2. A lead can never skip the approved state. The human gate is a structural checkpoint in the code, not a step someone has to remember.
3. Suppressed is permanent and global. Once a company opts out or a contact bounces, it is checked before every future send and can never re enter the pipeline by accident.
4. Deduplication happens twice. Once on company and job title at intake, and again on company domain after enrichment, so one company never receives two live sequences at once.
5. Every transition is logged with a timestamp, the agent that made it, and its cost, so the full history of any lead can be reconstructed at any time.

## How errors are handled

The bot never silently stops. That is the whole point of having an orchestrator instead of a cron of loose scripts.

- Every external call gets three automatic retries with increasing delay before Atlas gives up on it.
- If one job source fails, that source is skipped and logged. The rest of the run continues. The daily digest notes which sources succeeded.
- Anything that fails twice in a row is placed in a holding queue with full context and surfaced to a human, rather than silently dropped.
- Before every sending batch, the sender domain health is checked. If bounce rate or spam complaints spike, sending pauses automatically and an alert goes out.

## Budget caps

Clay credits, Claude usage, sending volume, and Wonda credits each have a monthly cap set by the founder. When a cap is reached, Atlas pauses only that one stage and sends an alert. It never quietly stops the whole system or silently drops leads to stay under budget. A live running total against each cap appears in the daily digest, so there are no surprises at the end of the month.

## The two human approval gates

Everything else Atlas handles on its own and only escalates when something has genuinely gone wrong. In practice the human spends about ten minutes a day here.

1. **Outreach copy.** The first two hundred or so sequences are reviewed one by one. Once quality is proven, this moves to a ten percent spot check, and reverts to full review automatically if reply quality drops.
2. **Weekly content batch.** The Publicist calendar and creatives are reviewed once a week before anything is published.

## The weekly evaluation loop

The system grades itself every Monday rather than running on trust.

- **Scoring accuracy.** Fifty postings are hand labeled each week and checked against the automatic score. The target is over ninety percent agreement. Below that, a rubric fix is proposed automatically.
- **Sequence testing.** Different wording variants are compared on open and reply rate. The winner is promoted into the master template in memory. The loser is archived with its numbers, not deleted.
- **Content performance.** Whatever performed best on social the prior week gets more weight in the next week's calendar.
- **Drift check.** Any large organization that slipped through and reached Clay, caught later by its staff count, is added to the exclusion list automatically so it never happens twice.

## Integrations

| System | Direction | Mechanism |
|---|---|---|
| Job sources | in | JobSpy plus free APIs for Indeed, ZipRecruiter, Google Jobs, and the remote boards. Apify for LinkedIn. |
| NPPES registry | in | Free government lookup for provider count, official phone, and address. A size check before any paid step. |
| Clay | out and in | Webhook table in. Enriched rows returned by webhook or export. |
| Smartlead or Instantly | out and in | API push with custom fields. Reply and bounce webhooks in. |
| Close | out | Create the lead, assign the rep, and start the call task on a positive reply. |
| Wonda AI | out and in | Content generation, editing, publishing, and analytics for the Publicist. |
| Founder | out | The 17:00 digest by email or chat, plus real time alerts for failures and budget breaches. |

## Build order

1. Scout scrape and score, already live and proven on a real run. Clay table and webhook.
2. The state store and the Atlas skeleton. The schedule, the transitions, the digest. The orchestrator exists from day one, even while some stages are still supervised by hand.
3. The Clay webhook and Finder. The approval sheet and the Scribe push to the sender.
4. The reply webhooks and the Close handoff. Then the Publicist. Then the evaluation loop.
