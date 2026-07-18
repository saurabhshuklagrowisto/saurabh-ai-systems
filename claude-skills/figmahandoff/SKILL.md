---
name: figma-handoff
description: >
  Use this skill EVERY TIME a Figma URL is mentioned or pasted in any message.
  Triggers on any figma.com link, any mention of "figma", or any request to
  implement/build/code a design. Before writing any code or reading any design,
  this skill intercepts the request and asks two required questions:
  (1) which tech stack — React or Shopify Liquid, and
  (2) whether to show the Figma design system first or proceed directly.
  Do NOT skip these questions. Do NOT write any code before both are answered.
  This is mandatory for all Figma-related implementation tasks at Acme.
---

# Figma Handoff Skill

## Purpose

Every time a developer shares a Figma URL, Claude must **stop and ask two questions** before doing anything else. No code. No design reading. No assumptions. Questions first.

This ensures:
- Code is generated in the right tech stack (React vs Shopify Liquid)
- Developer can inspect the design system before committing to implementation
- Output is consistent across all engineers on the team

---

## Trigger

This skill activates when:
- A message contains a `figma.com` URL
- A message contains the word "figma" alongside any implementation intent ("build", "implement", "code", "create", "make")
- A developer says "here is the design" or "use this design" or similar

---

## Step 1 — Ask the Two Required Questions

The moment a Figma URL is detected, respond with **exactly this** — no code, no design analysis yet:

---

**Got the Figma link. Before I start, two quick questions:**

**1. Which tech stack should I use?**
- `A` — React
- `B` — Shopify Liquid

**2. How would you like to proceed?**
- `C` — Show me the Figma design system first (components, tokens, styles)
- `D` — Go straight to implementation

*Reply with your choices (e.g. "A, D" or "B, C") and I'll get started.*

---

Do not deviate from this format. Do not add extra questions. Wait for the developer's reply before doing anything with the Figma URL.

---

## Step 2 — Handle the Response

### If they chose C (Show Design System First)

Read the Figma file using the MCP Server and display a full design system breakdown in this structure:

```
## Design System — [Frame/File Name]

### Components
List every named component Claude can identify from the file:
- ComponentName — description of what it is / how it's used

### Colour Tokens
- token-name: #hexvalue — usage note

### Typography
- style-name: Font Family, Size, Weight, Line Height — usage note

### Spacing & Layout
- spacing scale values
- border radius values
- shadow / elevation values

### Notes
Anything unusual, missing, or worth flagging before implementation starts
```

After displaying this, ask:
> "Which components do you want me to implement? You can name them or say 'all'."

Wait for confirmation before writing any code.

---

### If they chose D (Go Straight to Implementation)

Proceed directly to reading the Figma URL and generating code.

---

## Step 3 — Generate Code Based on Tech Stack

### If React (A)

- Read the full React patterns reference before generating: `references/react.md`
- Generate a functional React component using TypeScript if the codebase uses it
- Use Tailwind CSS utility classes for styling — map Figma values to Tailwind scale (see reference file)
- Check `tailwind.config.js` for project colour tokens before hardcoding any hex values
- Import existing components from the codebase — do not reinvent them (check `src/components/ui/` first)
- Use `cn()` utility for conditional or merged class names
- Use `cva` for components with multiple Figma variants
- If Code Connect is set up, use mapped component imports automatically

### If Shopify Liquid (B)

- Generate valid Liquid template syntax (`.liquid` file)
- Use Shopify section schema where relevant (`{% schema %}`)
- Reference Shopify theme settings variables (`{{ settings.color_background }}`) over hardcoded values
- Use `{{ 'style.css' | asset_url | stylesheet_tag }}` pattern for styles
- Keep logic in Liquid, styles in a companion `.css` file unless told otherwise
- Read the references file for detailed Shopify Liquid patterns: `references/shopify-liquid.md`

---

## Step 4 — After Code Generation

Always end with:

```
## Implementation Notes
- [List any design tokens that were hardcoded because they weren't in the Figma variables]
- [List any components that were created from scratch because Code Connect isn't set up]
- [List any design decisions made due to ambiguity in the Figma file]

## To improve accuracy
- Set up Code Connect to map Figma components to your codebase (see the Figma MCP Evaluation doc)
- Share the frame URL for any specific sub-component you want refined
```

---

## Rules — Never Break These

1. **Never write code before both questions are answered**
2. **Never assume React** — always ask, even if it looks like a React project
3. **Never hardcode colours or spacing** if design tokens exist in the Figma file
4. **Never skip the Design System view** if the developer asks for it — show everything Claude can read
5. **Never write to the Figma file** — read only, always (write-to-canvas is off until the team agrees a protocol)

---

## Reference Files

- `references/react.md` — React patterns, TypeScript interfaces, Tailwind token mapping, layout patterns, common mistakes
  - Load this when tech stack answer is A (React)
- `references/shopify-liquid.md` — Shopify Liquid patterns, schema structure, theme settings usage
  - Load this when tech stack answer is B (Shopify Liquid)
