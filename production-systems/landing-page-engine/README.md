# Landing Page & Collateral Engine

![Status](https://img.shields.io/badge/status-live-success?style=flat-square)
![Skill](https://img.shields.io/badge/Claude_skill-1-cc785c?style=flat-square)
![Outputs](https://img.shields.io/badge/outputs-WordPress%2FElementor%20%2B%20custom%20HTML-1e40af?style=flat-square)

A Claude skill I built that turns a one-paragraph event brief into a publish-ready landing page (either a WordPress/Elementor layout or a standalone custom-HTML page) plus the matching set of marketing collaterals like banners, social cards and email headers designed in Claude Design. Built at [Growisto](https://growisto.com) to power the webinar and event demand engine.

This is the production system behind the landing pages and creatives in the [Webinar and Podcast Demand Engine](../../marketing-workflows/webinar-podcast-demand).

## What problem it solves

Every webinar, every event and every campaign needs a landing page and a stack of collaterals: a hero banner, social cards in three aspect ratios, an email header, a speaker card. The default way this happens is a designer and a web person take two to three days per event, and the marketer waits. By the time the page is live, half the promotion window is gone.

The bottleneck was never the idea. It was the production lag between "we are running a webinar on X" and "here is the page people can register on, and here are the creatives to promote it."

This skill collapses that lag. A brief goes in, a publish-ready page and a full collateral set come out, in hours instead of days. The marketer stays in control of the message and Claude does the production.

## The architecture

```
   Event brief (one paragraph)
   topic · speakers · date · CTA · audience
            │
            v
   ┌────────────────────────────────┐
   │  Claude skill · landing-page   │  Reads the brief
   │  generator                     │  Reads the brand kit (colours,
   │                                │  fonts, logo, tone)
   └───────────────┬────────────────┘
                   │
         ┌─────────┴─────────┐
         v                   v
   ┌──────────────┐   ┌──────────────────┐
   │  Path A      │   │  Path B          │
   │  WordPress / │   │  Custom HTML      │
   │  Elementor   │   │  (standalone)     │
   │              │   │                   │
   │  Section     │   │  Single self-     │
   │  structure + │   │  contained file,  │
   │  copy +      │   │  inline CSS,      │
   │  widget map  │   │  responsive,      │
   │              │   │  form embed       │
   └──────┬───────┘   └────────┬──────────┘
          │                    │
          └─────────┬──────────┘
                    v
   ┌────────────────────────────────┐
   │  Claude Design · collaterals   │  From the same brief + brand kit:
   │                                │  - hero banner
   │                                │  - social cards (1:1, 4:5, 16:9)
   │                                │  - email header
   │                                │  - speaker card(s)
   └───────────────┬────────────────┘
                   │
                   v
   ┌────────────────────────────────┐
   │  Human review + publish        │  Marketer checks copy + design
   │  - WordPress: paste into        │  Edits anything off-brand
   │    Elementor, connect form      │  Publishes the page
   │  - HTML: deploy to host         │  Schedules the creatives
   └───────────────┬────────────────┘
                   │
                   v
   ┌────────────────────────────────┐
   │  Feeds the demand engine       │  Registration page → Zoho Forms
   │                                │  Creatives → LinkedIn + email +
   │                                │  Sendy invite sequence
   └────────────────────────────────┘
```

## The two output paths, and when to use each

**Path A · WordPress / Elementor.** Use this when the page needs to live on the main marketing site, be editable by a non-technical teammate later, and inherit the site's existing theme and tracking. The skill outputs a section-by-section structure (hero, agenda, speakers, registration, FAQ, footer), the finished copy for each section, and a widget map that says which Elementor widget holds what. The marketer pastes it into Elementor, connects the registration form, and publishes. No developer needed.

**Path B · Custom HTML.** Use this when the page needs to be fast, standalone and disposable. Think a one-off event microsite, a page that has to load in under a second, or a page hosted away from the main site. The skill outputs one self-contained HTML file with inline CSS, a responsive layout, no external dependencies, and a form embed point ready to wire to the registration backend. Deploy it anywhere static hosting works.

Same brief, same brand kit, two production targets. The marketer picks the path based on where the page needs to live.

## The architecture choices that matter

**The brand kit is an input, not a hardcode.** Colours, fonts, logo and tone-of-voice live in a brand-kit file the skill reads on every run. Change the brand kit once and every future page and collateral inherits it. This is what keeps fifty pages consistent without fifty manual style passes.

**Copy and structure are generated together, not bolted on.** The skill does not produce a layout and then ask for copy. It reads the brief and produces the section structure and the copy for each section in one pass, so the headline, the sub-head, the agenda bullets and the CTA all sing the same note. The marketer edits voice and the skill handles the scaffold.

**Collaterals come from the same brief as the page.** Because the hero banner, the social cards and the email header are generated from the same brief and brand kit as the landing page, the campaign is visually coherent end to end. The person clicking the LinkedIn card lands on a page that looks like the card. That coherence usually takes a designer holding the whole set in their head; here it falls out of the shared input.

**Human review is the publish gate.** Nothing goes live without a marketer reading the copy and checking the design against brand. The skill produces the 90% and the human owns the last 10% and the publish button. This is the same brain-and-hands split as the rest of the systems in this repo: Claude produces, the human approves and ships.

## Where AI plugs in

- **Landing page structure and copy** · Claude reads the brief and the brand kit, then produces the section layout and the finished copy for both the WordPress/Elementor path and the custom-HTML path.
- **Responsive HTML generation** · for Path B, Claude writes the self-contained, mobile-first HTML file with inline CSS and a form embed point.
- **Collateral design** · Claude Design produces the banner, social cards, email header and speaker cards from the shared brief and brand kit.
- **Variant generation** · headline and CTA variants for A/B testing the page, and multiple social-card angles for the same event.

## Numbers

- **Powered the landing pages and creatives** for the 12 webinars and the event activations in the [demand engine](../../marketing-workflows/webinar-podcast-demand)
- **Production lag** · brief to a publish-ready page plus a full collateral set in hours, down from the two-to-three-day designer-plus-web-person cycle
- **Two output targets** · WordPress/Elementor for site-resident pages and custom HTML for standalone microsites, off the same brief and the same brand kit
- **Brand consistency** · every page and every creative inherits one brand kit, so the whole campaign is visually coherent without a manual style pass per asset

## Why this pattern transfers

Any "brief in, branded asset out" need fits this shape:

- Product launch pages
- Case-study microsites
- Recruiting and hiring pages
- Sales one-pagers and leave-behinds
- Paid-campaign landing pages with per-audience variants

In every case the architecture is the same. A short brief plus a brand kit goes in. Claude produces the structure, the copy and the matching creatives. A human reviews against brand and publishes. The brand kit keeps everything consistent and the human keeps everything on-message.

## Stack

Claude · landing page structure, copy, and responsive HTML generation
Claude Design · banners, social cards, email headers, speaker cards
WordPress + Elementor · the site-resident publishing target (Path A)
Custom HTML + static hosting · the standalone microsite target (Path B)
Brand kit file · the single source of colours, fonts, logo, and tone the skill reads on every run
Zoho Forms · registration backend the pages connect to

## What is open here

| File | What it shows |
|---|---|
| [README.md](./README.md) | This doc. Architecture and workflow. |
| [SKILL.md](./SKILL.md) | The skill contract: the inputs it takes, the two output paths, the brand-kit dependency, and the review gate. Sanitised of the actual brand kit. |
| [examples/webinar-landing-page.html](./examples/webinar-landing-page.html) | A **real production landing page** for a live Growisto webinar, shipped on WordPress + Elementor with a Contact Form 7 registration form (Path A). Open it in any browser. Sanitised: embedded photos removed, the CF7 shortcode point left in place. |
| [examples/sendy-invite-email.html](./examples/sendy-invite-email.html) | A **real production HTML email** built for Sendy (self-hosted on Amazon SES). It is the kind of collateral that drives registrations into the landing page above. Email-client-safe, mobile-responsive, bulletproof CTA buttons. |

The actual brand kit, the production skill source, and the unedited live pages are internal to Growisto. The skill contract, the architecture, the workflow, and two representative sanitised outputs are open.

> The two example files are genuine production artifacts (sanitised), not mockups. The landing page is the real WordPress/Elementor page that ran the webinar, and the email is the real Sendy newsletter that promoted it.

## Infrastructure

- [elementor_mcp_setup_runbook.md](./elementor_mcp_setup_runbook.md) — step-by-step runbook to connect Claude Code to WordPress/Elementor via MCP so pages can be built programmatically. Placeholder credentials only; no secrets.
