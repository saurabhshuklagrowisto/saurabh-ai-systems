# The Five AI Employees and Company Memory

Each employee is an agent with a written job description, a schedule, its own scoped tools, and a contract with memory that says what it reads and what it must write back. Atlas coordinates them. None of them talk to each other directly. They read from and write to one shared company memory, which is what keeps them coordinated and what makes the system compound.

## Scout, the data scraper

Runs daily at 07:00. Fills the top of the funnel.

- Scrapes the target admin job titles across Indeed, ZipRecruiter, Google Jobs, and the free remote boards. US employers only.
- Deduplicates and scores every posting 0 to 100 against the ICP rubric it reads from memory.
- Watches practice owner communities for hiring intent, the "we are drowning, we need help" posts, and flags the good ones to a human. It never posts on its own.

Reads: the ICP and scoring rules from memory. Writes: qualified companies for Finder, and the day's scrape stats for the digest.

## Finder, the prospector

Runs daily after Scout. Turns companies into contactable buyers.

- Runs the free NPPES size check on every qualified company before any paid step.
- Runs the survivors through Clay for firmographics and a decision maker waterfall keyed to practice size.
- Does light LinkedIn research per contact to fuel personalization.

Reads: the decision maker matrix from memory. Writes: verified contacts for Scribe, and the enrichment match rate for the weekly review.

## Scribe, the outreach writer

Runs daily, human gated. Starts and nurtures every conversation.

- Personalizes the master five touch sequence to the exact posting and contact.
- Sends through the warmed inboxes and enforces the deliverability playbook automatically.
- Routes replies to the sales rep with a full context card and logs every outcome.

Reads: the current best template and the deliverability playbook from memory. Writes: send and reply outcomes back to memory, so the templates improve from real data.

## Publicist, the content engine

Runs a weekly cycle, human gated at the batch. Builds the brand that warms the cold outreach.

- Studies competitor profiles and ad libraries through Wonda to see which hooks and formats work.
- Drafts a weekly content calendar from the brand voice and case studies in memory.
- Generates the video or post with Wonda, edits it, and publishes it on schedule after a human approves the batch.
- Reads the analytics back into memory so next week's calendar favors what performed.

Reads: brand voice and case studies from memory. Writes: competitor intel and content performance back to memory.

## Librarian, the memory keeper

Runs continuously, with a weekly consolidation. Keeps the whole system smart.

- Files call notes, reply threads, and learnings into the right place in memory with tags.
- Consolidates weekly. Deduplicates, retires stale facts, updates the index.
- Answers the team's questions from memory, and serves the current best playbook to every other agent.

This is the single source of truth for every agent. When Scribe asks for the best template, or the Publicist asks for the brand voice, the Librarian is what answers.

## Company memory

Memory is a git backed set of structured markdown files, mirrored to a shared drive for humans. It is agent native, versioned, and free. The structure the Librarian maintains:

| Directory | What lives there | Who reads it |
|---|---|---|
| `icp-and-scoring/` | The ICP definition, the 0 to 100 scoring rubric, the target job titles, and the decision maker matrix. | Scout, Finder |
| `email-templates/` | The master five touch sequence and the winning copy variants, with performance notes. | Scribe |
| `brand-voice/` | Tone, vocabulary, positioning, and the compliance guardrails for public content. | Publicist |
| `case-studies/` | Client proof. Placements, savings numbers, testimonials. Every public claim traces to a real number here. | Scribe, Publicist |
| `competitor-intel/` | Competitor hooks, ad angles, and formats. Written weekly by the Publicist. | Publicist |
| `lead-history/` | One file per company. Every touch, outcome, and opt out. Also the suppression source. | Scout, Scribe |
| `playbooks/` | The operating rules. Deliverability, approval gates, escalation. | Scribe |
| `experiment-log/` | Every test with its result and decision. Checked before repeating an experiment. | Atlas, the Librarian |

The rules that keep memory clean:

1. One fact, one place. Link instead of duplicating.
2. Date every entry.
3. Outcomes over opinions. Log the numbers, open rate, reply rate, calls booked.
4. The Librarian consolidates weekly and updates the index.

A genericized copy of this structure is in [`memory/`](./memory).

## What the human does

About thirty minutes a day, on judgment, not busywork.

- Approve outreach copy in the early weeks, then the weekly social batch.
- Take the booked calls and jot the outcomes. The Librarian files them.
- Review the board each morning and nudge priorities.

Agents draft. Humans decide.
