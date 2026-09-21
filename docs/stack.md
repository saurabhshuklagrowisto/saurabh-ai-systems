# Stack and Tooling Decisions

## What I use, and why

| Layer | Tool | Why this one |
|---|---|---|
| **Model (build)** | Claude Opus 5, Sonnet 5 | Long-context reasoning and structured-output reliability. Native MCP support, which is what the production agents are built on. |
| **Model (volume)** | Claude Haiku 4.5 via OpenRouter | High-volume filtering and classification where a strict-rule prompt beats reasoning depth. Runs the WhatsApp agent at under $2 a month. |
| **Second opinion** | GPT, Astra | Cross-model checks on prompts and outputs that matter, plus generative media work. When two models disagree on a classification, that case goes straight into the golden set. |
| **Agent runtime** | Claude Code, OpenClaw, custom MCP servers | Claude Code for skills and agents at the desk, OpenClaw for the always-on WhatsApp agent on a VPS, MCP for anything a model needs to call safely. |
| **Orchestration (prod)** | n8n | Self-hostable, low-code but not no-code (drop into JS when needed), good Claude, CRM and Apollo nodes plus custom webhooks. |
| **Orchestration (dev)** | Python + Anthropic SDK | Lets me iterate on prompts and guardrails outside the n8n canvas. The same Python becomes a service when it needs to be. |
| **CRM (hands-on)** | Close CRM, Zoho CRM | Close is where I have built against the API directly: lead, contact and note creation, domain-level dedup, custom fields and status ids, inbound webhooks on SMS and email activity. Zoho is the agency system of record, lifecycle stages, custom modules and workflows. |
| **CRM (model-equivalent)** | HubSpot, Salesforce | Same objects, same lifecycle model, same integration surface as the two above. I have not owned a production instance of either, and I would be productive in days rather than months. |
| **Outbound sending** | SalesBlink, Smartlead, Lemlist, Sendy, Leadbird | SalesBlink and Smartlead for sequenced cold outbound with warmup, Lemlist for warm personalised sequences, Sendy (self-hosted, Amazon SES) for high-volume sends, Leadbird for done-for-you outbound capacity. |
| **Deliverability** | Microsoft 365 mailbox estates, Cloudflare DNS, EmailListVerify | SPF with a hard fail, DKIM two-key rotation, DMARC at quarantine with reporting, DNSBL and URIBL sweeps, warmup ramps per mailbox, and a verification gate in front of the CRM. |
| **Enrichment** | Clay, Apollo, Prospectoo, LinkedIn Sales Navigator | Clay for waterfall enrichment, Apollo and Prospectoo for contact data, Sales Navigator for signals. |
| **Answer engine and SEO** | llms.txt, schema.org JSON-LD, GEO and AEO audits | Structured data and answer-shaped pages so the content is citable by AI search, not just rankable. |
| **Landing pages** | WordPress + Elementor, custom HTML | Elementor for site-resident pages a non-technical teammate can edit later, custom HTML for fast standalone microsites. A Claude skill generates both from one brief. |
| **Creative and collateral** | Claude Design, Canva | Banners, social cards, email headers and speaker cards, generated from the same brief and brand kit as the landing page so a campaign stays visually coherent. |
| **Knowledge** | Markdown wiki, git-backed, MCP-served | Source of truth in git, CI validates schema, MCP serves it into Claude. Anyone with a clone can contribute. |
| **Eval and quality** | Custom Python harness in this repo | A standard harness felt premature, so I rolled my own. It gets replaced by a framework once the requirements stop moving. |
| **Logging and observability** | BigQuery (production), stdout (dev) | Production agent outputs land in BigQuery for replay and post-hoc analysis. |

## What I'm NOT using, and why

- **LangChain / LlamaIndex** · too much abstraction for the workflows I need. Direct SDK calls are clearer and easier to debug.
- **Vector DB for retrieval** · the data I pull from is already structured (CRM, Drive, wiki). Structured retrieval beats embedding similarity in this domain.
- **Fine-tuning** · instruction-following is strong enough that prompt plus skill structure is the right unit of customization.
- **Autonomous agents with no human in the loop** · every customer-facing send goes through a human approval step. Autonomy is for internal-only side effects.

## What I'd add at production scale

- **Prompt registry** · currently versioned in git markdown. At scale, a service that lets non-engineers diff and roll back prompts without a git workflow.
- **Shadow-mode evals** · run v(N+1) and v(N) on live traffic in parallel for a week, compare outputs blind, promote only if v(N+1) wins.
- **Cost tracking per workflow** · token counts, latency and error rate per prompt version. Surface cost regressions the same way quality regressions get gated.
- **Adversarial test cases** · auto-generated edge cases (prompt injections, ambiguous intents, malformed inputs) added to the golden set.

## What I'm honest about NOT being

- Not a full-stack web developer (no React plus backend services at production scale)
- Not a Salesforce or HubSpot admin (production depth is in Close and Zoho, the model carries across, ramp is weeks not months)
- Not a data engineer (I design the analytics surface, I am ramping on BigQuery and dbt for the build)
- Not a security engineer (I build the guardrails my systems need, I do not audit anyone else's)
