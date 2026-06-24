# Marketing Workflows

The marketing programs I have shipped at [Growisto](https://growisto.com) for B2B SaaS and services clients in the US and India. Each one is a real production system that ran (or still runs) for a paying client.

Where `production-systems/` documents the AI agents and infrastructure, this folder documents the marketing motions those agents and tools support. Different level of abstraction, same standard of proof.

The case study narratives live on the portfolio website: **[shivsaurabh.netlify.app](https://shivsaurabh.netlify.app)**. This folder documents the workflow architecture, the tools wired together, and where AI plugs in.

## The six workflows

| # | Workflow | Outcome | Cost / Speed |
|---|---|---|---|
| 01 | [US CTO Outbound Stack](./us-cto-outbound-stack) | 25+ qualified meetings/month, ~$1.2M influenced pipeline (6 months) | Under $2/month all-in |
| 02 | [ABM Playbook · 100 Named US Accounts](./abm-100-named-accounts) | 32/100 first meetings in 90 days, 3x engagement lift on tier-1, ~$410K influenced pipeline | 4 US conferences activated |
| 03 | [Email and Newsletter Operations Overhaul](./email-newsletter-overhaul) | Open rate 14% → 29%, CTR 1.4% → 3.8%, 12,000 contacts under management | 6 sends/month cadence |
| 04 | [Webinar and Podcast Demand Engine](./webinar-podcast-demand) | 12 webinars, 8 podcast episodes, ~150 avg registrants/webinar, 10% registrant → qualified meeting | Closed-loop content engine |
| 05 | [Upwork CTO Account · End-to-End Motion](./upwork-cto-account) | 22 qualified inbound leads, ~$380K pipeline generated, 100% account ownership | Built from zero, Day 1 |
| 06 | [Marketing Ops Automation Layer](./marketing-ops-automation) | ~12 hrs/week saved, 14 workflows in production, 0 routing errors/quarter | Self-hosted n8n on Railway |

## How to read each one

Each subfolder has a README with the same five sections:

1. **The outcome** · numbers, defended honestly
2. **The architecture** · which tools wired which way (ASCII diagram)
3. **The workflow** · step-by-step what happens
4. **Where AI plugs in** · where Claude or other AI does the work
5. **The stack** · every tool with what it does

Below each main README, where applicable, you will find linked artifacts — sanitised workflow exports, screenshots, prompt examples.

## Why both folders matter

Some interviewers want to see the systems (production-systems/) and stop there. Some want to see the outcomes (marketing-workflows/) and stop there. The strongest signal is when both are visible in the same repo, and you can trace any outcome back to the system that produced it and any system back to the outcome it serves.
