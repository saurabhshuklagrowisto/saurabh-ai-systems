<div align="center">

# Saurabh Shukla

### AI-Powered Marketing Specialist · Mumbai · Open to remote roles

**Production AI systems for sales and marketing teams. Built at [Growisto](https://growisto.com).**

[![Portfolio](https://img.shields.io/badge/Portfolio-shivsaurabh.netlify.app-2b6cb0?style=flat-square)](https://shivsaurabh.netlify.app)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-shivsaurabh-0a66c2?style=flat-square&logo=linkedin&logoColor=white)](https://linkedin.com/in/shivsaurabh)
[![Email](https://img.shields.io/badge/Email-contact-d93025?style=flat-square&logo=gmail&logoColor=white)](mailto:officialsaurabhshukla@gmail.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg?style=flat-square)](./LICENSE)

</div>

---

## TL;DR

I build the AI systems my marketing team uses every day. Autonomous CRM enrichment agents, WhatsApp opportunity scanners, ABM scoring pipelines, eval-gated Claude skills, and the boring guardrail layer that keeps it all from breaking. Most teams pay for the stack I run for under two dollars a month.

This repo is the proof. Every system here is either running live in production for a real team right now, or is a scoped-down packaging of a pattern I run in production. Code where I can share it. Architecture where I can't.

---

## By the numbers

<table>
<tr>
<td align="center"><b>5</b><br>production systems live</td>
<td align="center"><b>4</b><br>standalone Claude skills with eval harness</td>
<td align="center"><b>6</b><br>marketing case studies on portfolio</td>
</tr>
<tr>
<td align="center"><b>~$1/mo</b><br>US CTO outbound stack</td>
<td align="center"><b>25+</b><br>qualified meetings / month</td>
<td align="center"><b>$15 → $2</b><br>monthly cost on the WhatsApp agent</td>
</tr>
</table>

---

## Production systems

Real systems running live for real teams. Click into any folder for the full architecture, the patterns, and what's open versus described.

| System | Description | Status |
|---|---|---|
| [**MAYA · CRM Enrichment Agent**](./production-systems/maya-crm-agent) | Autonomous daily agent that links new CRM leads to the right Target Account by resolving the brand's real D2C domain. Self-running playbook, DRY_RUN safety, email digest. | ![Live](https://img.shields.io/badge/status-live-success?style=flat-square) |
| [**WhatsApp AI Agent on VPS**](./production-systems/whatsapp-ai-agent) | A WhatsApp Claude agent on a Contabo VPS that scans group messages on a cron, filters opportunities, alerts the user. Includes the case study of cutting cost from $15 to under $2 a month. | ![Live](https://img.shields.io/badge/status-live-success?style=flat-square) |
| [**ABM Automation Pipeline**](./production-systems/abm-automation) | Three-workflow ABM system: ICP scoring on inbound brand lists, POC extraction via Apollo, and a real-time Cliq bot that returns verified contacts on demand. 92 brands scored, codified ICP rules for India and USA. | ![Live](https://img.shields.io/badge/status-live-success?style=flat-square) |
| [**Fireflies Summary Pipeline**](./production-systems/fireflies-pipeline) | n8n automation that runs every external meeting through a Claude brand-disambiguation step and files the transcript plus an English summary to the right Drive folder. Multi-language friendly. | ![Live](https://img.shields.io/badge/status-live-success?style=flat-square) |
| [**Upwork Proposal Automation**](./production-systems/upwork-proposals) | Claude plugin with two live skills (`upwork-scan` + `upwork-proposal`) that scans Upwork, scores jobs on a 16-dimension rubric, runs a brand-permission audit, and generates expertise-first PDF proposals. Architecture and patterns documented. Code is employer IP. | ![Live](https://img.shields.io/badge/status-live-success?style=flat-square) |

## Claude skills and evals

Standalone runnable Claude skills with golden-set eval harnesses. Each runs in `--demo` mode without an API key. The eval harness ships with both a passing fixture and a deliberately broken fixture, so you can watch the regression gate fire on a real failure.

| Skill | What it proves | Run it |
|---|---|---|
| [ABM Account Brief Skill](./claude-skills/abm-account-brief-skill) | Skill packaging, ICP gate, evidence grounding, prompt versioning, eval as a CI gate | `python claude-skills/abm-account-brief-skill/scripts/score_output.py` |
| [Reply Triage Agent](./claude-skills/reply-triage-agent) | Schema-first agent design, critical-safety rules, regression-gated eval harness, n8n deployable | `python claude-skills/reply-triage-agent/reply_triage.py --demo` |
| [Signal Monitor](./claude-skills/signal-monitor) | Sales Copilot pattern: signal capture, persona match, recency cliff, ranked digest for SDRs | `python claude-skills/signal-monitor/signal_rater.py --demo` |
| [Pre-Meeting Brief Generator](./claude-skills/meeting-brief) | Identity resolution with confidence, data-freshness warnings, no-fabrication rule | `python claude-skills/meeting-brief/meeting_brief.py --demo` |

## Systems thinking

How I think about building agentic systems, distilled into the patterns I reuse across projects.

- [**ARCHITECTURE.md**](./ARCHITECTURE.md) · the 5-stage shape every workflow follows · input guardrail → Claude call → output guardrail → routing → eval feedback loop
- [**docs/eval-pattern.md**](./docs/eval-pattern.md) · golden sets, zero-tolerance safety rules, threshold gates that block promote on regression
- [**docs/stack.md**](./docs/stack.md) · what I use weekly, what I deliberately do not use, what I would add at scale
- [**docs/how-to-run.md**](./docs/how-to-run.md) · 30-second quickstart for any demo

---

## The mental model

Most teams ship AI demos. Production AI needs five things this repo demonstrates concretely.

1. **A schema.** Every output is JSON, every field has a contract, malformed equals dead letter queue.
2. **Guardrails as code.** PII scrub, banned phrases, confidence thresholds enforced before output reaches a human or a CRM. Same module reused across every agent.
3. **An eval harness.** Hand-labeled golden set, critical safety rules, threshold gates. CI exit code blocks promote when anything regresses.
4. **Prompt versioning.** v1 deprecated with a documented reason. v2 in production. v3 must pass the golden set before promote.
5. **Brain and hands separated.** The reasoning layer (Claude) is one component. The action layer (Python, n8n, SQL) is another. The brain calls the hands through clean contracts.

The four Claude skills demonstrate each of these in isolation. The five production systems show what they look like once they are wired together for a real team.

---

## Stack at a glance

**Models**
![Claude](https://img.shields.io/badge/Claude-Sonnet%204.6%20%2B%20Haiku-cc785c?style=flat-square)
![OpenRouter](https://img.shields.io/badge/via-OpenRouter-7c3aed?style=flat-square)

**Languages**
![Python](https://img.shields.io/badge/Python-3.10%2B-3776ab?style=flat-square&logo=python&logoColor=white)
![JavaScript](https://img.shields.io/badge/JS-n8n%20nodes-f7df1e?style=flat-square&logo=javascript&logoColor=black)
![Markdown](https://img.shields.io/badge/Markdown-prompts%20%2B%20configs-000000?style=flat-square&logo=markdown&logoColor=white)

**Orchestration**
![n8n](https://img.shields.io/badge/n8n-production-ea4b71?style=flat-square)
![Make.com](https://img.shields.io/badge/Make-scenarios-6d00cc?style=flat-square)
![Zoho Flow](https://img.shields.io/badge/Zoho_Flow-workflows-cf2e2e?style=flat-square)

**CRM and data**
![Zoho CRM](https://img.shields.io/badge/Zoho_CRM-system_of_record-cf2e2e?style=flat-square)
![Zoho Cliq](https://img.shields.io/badge/Zoho_Cliq-real--time_intake-cf2e2e?style=flat-square)
![Google Drive](https://img.shields.io/badge/Google_Drive-storage-4285f4?style=flat-square&logo=googledrive&logoColor=white)
![BigQuery](https://img.shields.io/badge/BigQuery-logs-669df6?style=flat-square)

**Outbound and enrichment**
![Smartlead](https://img.shields.io/badge/Smartlead-cold_email-3b82f6?style=flat-square)
![Lemlist](https://img.shields.io/badge/Lemlist-sequences-22c55e?style=flat-square)
![Apollo](https://img.shields.io/badge/Apollo-people_data-1e40af?style=flat-square)
![Clay](https://img.shields.io/badge/Clay-enrichment-000000?style=flat-square)
![LinkedIn Sales Nav](https://img.shields.io/badge/LinkedIn_Sales_Nav-prospecting-0a66c2?style=flat-square)

**Hosting**
![Contabo](https://img.shields.io/badge/Contabo-VPS-1c4e80?style=flat-square)
![Railway](https://img.shields.io/badge/Railway-services-0b0d0e?style=flat-square)
![Netlify](https://img.shields.io/badge/Netlify-portfolio_site-00c7b7?style=flat-square)

---

## What I claim, what I am not

I am a marketing specialist running an AI-powered GTM stack, who treats marketing operations as an engineering problem. I architect the systems, write the routing and the guardrails, and ship production workflows in Claude, n8n and Python orchestration. I work with sales and marketing teams in B2B SaaS and services.

I am not a CS-trained full-stack web engineer. I do not build React frontends or backend services at production scale. I write Python for orchestration and automation. Heavier engineering is something I would partner with engineers on.

If you need a builder who can hold the architecture, write the prompts, write the evals, build production workflows on top of Claude and the modern marketing stack, and partner cleanly with engineers when the work needs them, that is the role I fit. If the role you have needs the React plus Python backend generalist, that is not me, and I would rather we both know that early.

---

## How to run any of the standalone demos

```bash
git clone https://github.com/saurabhshuklagrowisto/saurabh-ai-systems.git
cd saurabh-ai-systems

# Every demo runs without an API key. They replay recorded Claude outputs.
python claude-skills/reply-triage-agent/reply_triage.py --demo
python claude-skills/signal-monitor/signal_rater.py --demo
python claude-skills/meeting-brief/meeting_brief.py --demo

# Run the eval harness. First the passing fixture, then the deliberately broken one.
python claude-skills/reply-triage-agent/eval.py
python claude-skills/reply-triage-agent/eval.py --outputs claude-skills/reply-triage-agent/broken_output.json
# The second exits with code 1. That is the regression gate firing on a real failure.

# Live mode against Claude
pip install anthropic
export ANTHROPIC_API_KEY="sk-ant-..."   # macOS / Linux
$env:ANTHROPIC_API_KEY = "sk-ant-..."   # Windows PowerShell
python claude-skills/reply-triage-agent/reply_triage.py --live
```

Python 3.10 or newer. Windows users may need `$env:PYTHONIOENCODING = "utf-8"` once per session.

---

## The portfolio website

For the marketing-side case studies with full numbers, the thesis on where AI agents fit inside the B2B GTM stack, and the contact form, see **[shivsaurabh.netlify.app](https://shivsaurabh.netlify.app)**.

Six case studies covering the $1 per month US CTO outbound stack, the 100-account ABM playbook, the email and newsletter overhaul, the webinar and podcast demand engine, the Upwork account, and the marketing ops automation layer.

---

## Currently in flight

Things I am actively building or extending right now.

- Wiring an LLM-as-judge call into the standalone eval harness so subjective quality has a measurable score
- Adding an MCP server wrapper around the ABM Account Brief Skill so it is callable from Claude Desktop
- Onboarding the second sales team to MAYA in DRY_RUN mode before flipping their lead-pool to live
- A shadow-mode harness that runs prompt v(N+1) against prompt v(N) on live traffic for a week before promote

---

## Open to

- **Remote AI-powered marketing roles** in GTM systems, agentic AI for sales and marketing, marketing engineering
- **Consulting engagements** for teams ramping a Claude-driven GTM motion from zero
- **Conversations** with founders and operators thinking about the next layer of AI in sales and marketing

If something here fits a problem you are working on, the [contact form on the portfolio site](https://shivsaurabh.netlify.app#contact) is the fastest path.

---

## License

MIT. Fork it, study it, adapt it. Attribution is appreciated, not required.

<div align="center">

**Saurabh Shukla** · Mumbai, India
[Portfolio](https://shivsaurabh.netlify.app) · [LinkedIn](https://linkedin.com/in/shivsaurabh) · [Email](mailto:officialsaurabhshukla@gmail.com) · [GitHub](https://github.com/saurabhshuklagrowisto)

</div>
