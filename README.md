# Saurabh Shukla · AI Marketing Engineer

GTM engineer and ABM operator at [Growisto](https://growisto.com). I build the AI systems my marketing team uses every day. CRM enrichment agents, WhatsApp opportunity scanners, ABM scoring pipelines, eval-gated Claude skills, the boring guardrail layer that keeps it all from breaking.

Portfolio site: **[shivsaurabh.netlify.app](https://shivsaurabh.netlify.app)** · Based in Mumbai · Open to remote roles

---

## What this repo is

Production systems and patterns I've built for sales and marketing teams. Each project here is either running live in production right now, or is a scoped down packaging of a pattern I run in production. Everything is documented honestly. Where code is open, you can clone it and run it. Where I cannot share code because of client or employer IP, the README describes the architecture so you can rebuild the pattern yourself.

Most of what is here was built at [Growisto](https://growisto.com) where I run demand generation, ABM and outbound for B2B teams. The portfolio website has the marketing-side case studies with numbers. This repo has the systems behind those numbers.

## What is inside

### Production systems

Real systems running live for real teams. Each folder has a README that explains what it does, the architecture, what's open, what's described.

| System | What it does | Status |
|---|---|---|
| [MAYA · CRM Enrichment Agent](./production-systems/maya-crm-agent) | Autonomous daily agent that links new CRM leads to the right Target Account by resolving the brand's real D2C domain. Self-running playbook, DRY_RUN safety, email digest. | Live in production |
| [WhatsApp AI Agent on VPS](./production-systems/whatsapp-ai-agent) | A WhatsApp Claude agent on a Contabo VPS that scans group messages on a cron, filters by rules, alerts the user, and drafts replies on approval. Cost cut from $15 to under $2 a month through careful tuning. | Live in production |
| [ABM Automation Pipeline](./production-systems/abm-automation) | Three-workflow ABM system: ICP scoring on inbound brand lists, POC extraction via Apollo, and a real-time Cliq bot that returns verified contacts on demand. 92 brands scored, codified ICP rules for India and USA. | Live in production |
| [Fireflies Summary Pipeline](./production-systems/fireflies-pipeline) | n8n automation that catches meetings, runs Claude through a brand disambiguation step, files the transcript and an English summary to the right Drive folder, and emails the team. Multi-language friendly. | Live in production |
| [Upwork Proposal Automation](./production-systems/upwork-proposals) | Claude plugin that scans Upwork for fit jobs, scores them on a 16-dimension rubric, runs a brand-permission gate, and generates expertise-first PDF proposals. Code is employer IP. Architecture and patterns documented. | Live in production |

### Claude skills and evals

Standalone runnable Claude skills with golden-set eval harnesses. Each runs in `--demo` mode without an API key. The eval gates a deliberate broken output to prove the regression check fires.

| Skill | What it proves | Run it |
|---|---|---|
| [ABM Account Brief Skill](./claude-skills/abm-account-brief-skill) | Skill packaging, ICP gate, evidence grounding, prompt versioning, eval as a CI gate | `python claude-skills/abm-account-brief-skill/scripts/score_output.py` |
| [Reply Triage Agent](./claude-skills/reply-triage-agent) | Schema-first agent design, critical-safety rules, regression-gated eval harness, n8n deployable | `python claude-skills/reply-triage-agent/reply_triage.py --demo` |
| [Signal Monitor](./claude-skills/signal-monitor) | Sales Copilot pattern: signal capture, persona match, recency cliff, ranked digest for SDRs | `python claude-skills/signal-monitor/signal_rater.py --demo` |
| [Pre-Meeting Brief Generator](./claude-skills/meeting-brief) | Identity resolution with confidence, data-freshness warnings, no-fabrication rule | `python claude-skills/meeting-brief/meeting_brief.py --demo` |

### Systems thinking

How I think about building agentic systems, distilled into the patterns I reuse across projects.

| Doc | The idea |
|---|---|
| [ARCHITECTURE.md](./ARCHITECTURE.md) | The 5-stage shape every workflow in this repo follows: input guardrail → Claude call → output guardrail → routing → eval feedback loop |
| [docs/eval-pattern.md](./docs/eval-pattern.md) | Golden set, zero-tolerance safety rules, threshold gates that block promote on regression |
| [docs/stack.md](./docs/stack.md) | What I use weekly, what I deliberately do not use, what I would add at scale |

## The mental model

Most teams ship AI demos. Production AI needs five things this repo demonstrates concretely.

1. **A schema.** Every output is JSON, every field has a contract, malformed equals dead letter queue.
2. **Guardrails as code.** PII scrub, banned phrases, confidence thresholds enforced before output reaches a human or a CRM. Same module reused across every agent.
3. **An eval harness.** Hand-labeled golden set, critical safety rules, threshold gates. CI exit code blocks promote when anything regresses.
4. **Prompt versioning.** v1 deprecated with a documented reason. v2 in production. v3 must pass the golden set before promote.
5. **Brain and hands separated.** The reasoning layer (Claude) is one component. The action layer (Python, n8n, SQL) is another. The brain calls the hands through clean contracts. This is how you keep the system reliable and the agent honest.

The four Claude skills in this repo demonstrate each of these in isolation. The five production systems show what they look like once they are wired together for a real team.

## What I am claiming, and what I am not

I am a marketer who treats GTM like an engineering problem. I architect the systems, write the routing and the guardrails, and ship production workflows in Claude, n8n and Python orchestration. I work with sales and marketing teams in B2B SaaS and services.

I am not a CS-trained full-stack web engineer. I do not build React frontends or backend services at production scale. I write Python for orchestration and automation. The frontend and the heavier backend services are something I would partner with engineers on.

If you need a builder who can hold the architecture, write the prompts, write the evals, build production workflows on top of Claude and the modern marketing stack, and partner cleanly with engineers when the work needs them, that is the role I fit. If the role you have needs the React plus Python backend generalist, that is not me, and I would rather we both know that early.

## How to run any of the standalone demos

```bash
git clone https://github.com/saurabhshuklagrowisto/saurabh-ai-systems.git
cd saurabh-ai-systems

# All skills run in --demo mode without an API key — they replay recorded Claude outputs
python claude-skills/reply-triage-agent/reply_triage.py --demo
python claude-skills/signal-monitor/signal_rater.py --demo
python claude-skills/meeting-brief/meeting_brief.py --demo

# Run the eval harness — first the passing fixture, then the deliberately broken one
python claude-skills/reply-triage-agent/eval.py
python claude-skills/reply-triage-agent/eval.py --outputs claude-skills/reply-triage-agent/broken_output.json
# Second one exits with code 1. That is the regression gate firing on a real failure.

# To run any skill live against the Claude API
pip install anthropic
$env:ANTHROPIC_API_KEY = "sk-ant-..."
python claude-skills/reply-triage-agent/reply_triage.py --live
```

Python 3.10 or newer. Windows users may need `$env:PYTHONIOENCODING = "utf-8"` once per session.

## The portfolio website

For the marketing-side case studies with numbers, the thesis on where AI agents fit inside the B2B GTM stack, and the contact form, see **[shivsaurabh.netlify.app](https://shivsaurabh.netlify.app)**.

Six case studies covering the $1 per month US CTO outbound stack, the 100-account ABM playbook, the email and newsletter overhaul, the webinar and podcast demand engine, the Upwork account, and the marketing ops automation layer. Each one has the tools used, the outcomes and what I learned.

## Stack

Models · Claude (Sonnet 4.6 and Haiku 4.5) via Anthropic and via OpenRouter
Languages · Python 3.10 plus, JavaScript in n8n, Markdown and YAML for prompts and configs
Orchestration · n8n in production, Anthropic SDK directly, Zoho Flow, Make
CRM and data · Zoho CRM, Zoho Cliq, Google Drive, BigQuery for logs
Outbound · Smartlead, Lemlist, Apollo, Clay, LinkedIn Sales Navigator
Eval and quality · Custom harness in this repo, golden sets per workflow, LLM as judge for subjective quality
Hosting · Contabo VPS for the WhatsApp agent, Railway for the older CRO audit tool, n8n cloud for the marketing automations

## About me

Three plus years at Growisto running demand generation, ABM and lifecycle marketing for B2B teams in SaaS and services. Most of my work lives at the intersection of marketing operations and AI automation. The thesis is on the website. The systems are in this repo.

License is MIT. Fork it, study it, adapt it. Attribution is appreciated, not required.

**Saurabh Shukla** · Mumbai, India · [shivsaurabh.netlify.app](https://shivsaurabh.netlify.app) · [LinkedIn](https://linkedin.com/in/shivsaurabh) · [GitHub](https://github.com/saurabhshuklagrowisto)
