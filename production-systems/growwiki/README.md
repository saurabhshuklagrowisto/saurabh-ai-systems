# Grow Wiki — a linked sales intelligence brain in Obsidian

A company wide sales intelligence wiki built in **Obsidian** and served to Claude through a **custom MCP server** — so the whole sales and marketing team can ask natural language questions ("find testimonials from fashion clients", "what have we done in healthcare?") and get grounded answers pulled from real, curated notes instead of model guesswork.

> All client data in the live vault is confidential — this page documents the architecture only.

## Why it beats a folder of PDFs (and most RAG setups)

Classic RAG chunks documents into a vector database and hopes similarity search finds the right context. Grow Wiki takes the **linked knowledge graph** route instead:

- Every note is small, typed, and **hand curated** — a brand hub, a case study, a testimonial, a key person, or an account history entry.
- Notes connect through `[[wikilinks]]`, so retrieval follows **explicit relationships** (brand → its case studies → the person who gave the testimonial → the account timeline), not fuzzy embedding distance.
- The MCP server exposes the graph itself as tools — search, note reading, link neighbourhoods, and a full **link graph** — so Claude can traverse context the way a salesperson actually thinks: start at the brand, walk outward.

## Structure (live counts from the production vault)

```
Grow Wiki (~1,000 notes)
├── <Sector>/                    ~19 industry sectors (eCommerce, BFSI, Healthcare,
│   ├── <Brand>.md               Fashion, SaaS, EdTech, Beauty, Industrial, ...)
│   │     the hub note: what we did, links to everything below
│   ├── <Brand>-Case-Studies.md  methodology + metrics table
│   ├── <Brand>-Testimonial.md   quote, person, designation
│   └── <Brand>-People.md        key contacts and roles
├── Account-History/             758 dated account interaction notes, linked to brands
├── Growisto-Capability/         65 notes: services, playbooks, proof points
└── link graph                   every [[wikilink]] = a typed edge Claude can walk
```

## The retrieval layer (custom MCP server)

| Tool | What it gives Claude |
|---|---|
| `search_notes` | keyword/brand search across the vault |
| `read_note` | full content of one note |
| `get_note_links` | one note's neighbourhood (what it links to, what links to it) |
| `get_link_graph` | the whole map — nodes + directed edges, scopable to a sector or brand cluster |
| `list_categories` | sector coverage overview with note counts |
| `get_related_notes` / `get_recent_notes` | discovery + freshness |

Guardrail baked into the system prompt: the tools answer **only** questions that name a specific client or Growisto's own work — general questions never touch the vault, so confidential data can't leak into unrelated answers.

## What it's used for

- Sales prep: pull every case study, testimonial and contact for a prospect's sector in one ask
- Outreach personalization: category matched proof points dropped into cold messages
- Onboarding: new teammates query institutional memory instead of asking around

## Stack

Obsidian (vault + wikilinks) · Python MCP server · Claude (Desktop/Code) as the query interface · plain Markdown as the storage format — no vector DB, no embedding pipeline, nothing to re-index.
