# Stack & Tooling Decisions

## What I use, and why

| Layer | Tool | Why this one |
|---|---|---|
| **Model** | Claude (Sonnet 4.6) | Best-in-class on long-context reasoning + structured output reliability. Native MCP support for the production system. |
| **Orchestration (prod)** | n8n | Self-hostable, low-code-but-not-no-code (you can drop into JS when needed), good Claude + Zoho + Apollo + custom webhook nodes. |
| **Orchestration (dev)** | Python + Anthropic SDK | Lets me iterate on prompts and guardrails outside the n8n canvas. Same Python becomes a service when needed. |
| **CRM** | Zoho CRM | What Growisto runs. Concepts (lifecycle stages, custom modules, workflows) map cleanly to HubSpot/Salesforce. |
| **Outbound** | Sendy, Lemlist, Apollo, Clay, Prospectoo | Sendy (self-hosted, Amazon SES backend) for high-volume cold sends; Lemlist for warm personalized sequences; Apollo + Prospectoo + Clay for enrichment. |
| **Enrichment** | Clay + Apollo + LinkedIn Sales Nav | Clay for waterfall enrichment, Apollo for contact data, LiSN for signals. |
| **Landing pages** | WordPress + Elementor, custom HTML | Elementor for site-resident pages a non-technical teammate can edit later; custom HTML for fast standalone event microsites. A Claude skill generates both from one brief. |
| **Creative / collateral** | Claude Design, Canva | Banners, social cards, email headers, speaker cards — generated from the same brief + brand kit as the landing page so the campaign is visually coherent. |
| **Knowledge** | Markdown wiki, git-backed, MCP-served | Source of truth in git. CI validates schema. MCP serves into Claude. Anyone with a clone can contribute. |
| **Eval / Quality** | Custom Python harness in this repo | Standard harness needs felt premature; rolled my own. Replaces with a framework once requirements stabilize. |
| **Logging / Observability** | BigQuery (production), stdout (dev) | Production agent outputs land in BigQuery for replay + post-hoc analysis. |

## What I'm NOT using, and why

- **LangChain / LlamaIndex** — too much abstraction for the workflows I need. Direct SDK calls are clearer and easier to debug.
- **Vector DB for retrieval** — the data I'm pulling from is already structured (CRM, Drive, wiki). Structured retrieval beats embedding similarity for this domain.
- **Fine-tuning** — Claude's instruction-following is strong enough that prompt + Skill structure is the right unit of customization.
- **Autonomous agents (no human-in-the-loop)** — every customer-facing send requires a one-click human approval. Autonomy is for internal-only side effects.

## What I'd add at production scale

- **Prompt registry** — currently versioned in git markdown. At scale, a service that lets non-engineers diff and roll back prompts without a git workflow.
- **Shadow-mode evals** — run v(N+1) and v(N) on live traffic in parallel for a week, compare outputs blind, promote only if v(N+1) wins.
- **Cost tracking per workflow** — token counts, latency, error rate per prompt version. Surface regressions on cost the same way we gate on quality.
- **Adversarial test cases** — auto-generated edge cases (prompt injections, ambiguous intents, malformed inputs) added to the golden set.

## What I'm honest about NOT being

- Not a full-stack web developer (no React + Python backend services at production scale)
- Not a Salesforce or HubSpot specialist (Zoho-equivalent depth; ramp ~2-3 weeks)
- Not an MCP server framework author (consume MCPs, architect them; teammate implements the server)
- Not a data engineer (designing the analytics surface; ramping on BigQuery + dbt for the build)
