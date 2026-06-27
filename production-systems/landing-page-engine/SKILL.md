---
name: landing-page-generator
description: >
  Turns a one-paragraph event/webinar brief into a publish-ready landing page —
  either a WordPress/Elementor section structure or a standalone custom-HTML page —
  plus a matching set of marketing collaterals. Reads a brand kit on every run so
  every output is on-brand. A human reviews and publishes; the skill never publishes
  on its own.
---

# Landing Page Generator — Skill Contract

This is the sanitised contract for the production skill. The actual brand kit and the
client event pages are internal to Growisto. This file documents what the skill takes
in, what it produces, and the rules it follows.

## Inputs

| Input | Required | Notes |
|---|---|---|
| `brief` | yes | One paragraph: topic, speaker(s), date/time, audience, the single CTA |
| `output_path` | yes | `wordpress_elementor` or `custom_html` |
| `brand_kit` | yes | Colours, fonts, logo URL, tone-of-voice rules. Loaded on demand, not hardcoded. |
| `sections` | no | Override the default section set. Default: hero, agenda, speakers, registration, FAQ, footer |
| `variants` | no | Number of headline/CTA variants to generate for A/B testing. Default 1. |

## Outputs

### Path A — `wordpress_elementor`

1. **Section structure** — ordered list of page sections
2. **Copy per section** — finished, on-brand copy for each section (headline, sub-head, body, CTA)
3. **Widget map** — which Elementor widget holds each piece of content, so a non-technical teammate can assemble it
4. **Form connection note** — where the registration form embeds and what fields it needs

### Path B — `custom_html`

1. **One self-contained HTML file** — inline CSS, mobile-first responsive, no external dependencies
2. **Form embed point** — a clearly marked block ready to wire to the registration backend
3. **Asset slots** — marked positions for the hero banner and speaker cards produced by the collateral step

### Both paths — collateral set (via Claude Design)

- Hero banner
- Social cards in 1:1, 4:5, and 16:9
- Email header
- Speaker card(s)

All generated from the same `brief` + `brand_kit` so the campaign is visually coherent.

## Rules the skill follows

1. **One CTA per page.** A landing page has exactly one job. If the brief implies more than one CTA, the skill picks the primary and flags the rest for a separate page.
2. **Brand kit is law.** Colours, fonts, and tone come from the brand kit. The skill does not invent a palette or a voice.
3. **Mobile-first.** For the HTML path, the layout is designed for phone first, then scaled up. Most webinar registrations come from mobile.
4. **No fabricated proof.** The skill does not invent testimonials, logos, or stats. If the brief does not supply social proof, the section is left as a marked placeholder for the human to fill.
5. **Human publishes.** The skill produces a publish-ready artifact. It never publishes, never connects live forms, never schedules creatives. A marketer reviews against brand and ships.

## The review gate

Every run ends with a checklist the marketer runs before publishing:

- [ ] Copy reads in the brand voice (not generic AI tone)
- [ ] The single CTA is correct and the form is wired
- [ ] Design matches the brand kit (colours, fonts, logo)
- [ ] No placeholder text or fabricated proof left in
- [ ] Mobile layout checked on a real phone

Only after the checklist passes does the page go live. This is the same brain-and-hands
split as the rest of the systems in this portfolio: the skill produces, the human approves.
