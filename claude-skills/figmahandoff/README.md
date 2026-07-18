# figmahandoff

A Claude Code skill that intercepts any Figma-URL implementation request and asks two required questions first — target stack (React or Shopify Liquid) and whether to show the design system before coding — before writing anything. Includes reference files for React (Tailwind token mapping, `cn()`/`cva` conventions) and Shopify Liquid (section schema, theme settings) patterns.

Generic dev-workflow skill, not tied to any specific company's data.

## Install

Copy `SKILL.md` and `references/` into `~/.claude/skills/figmahandoff/`.
