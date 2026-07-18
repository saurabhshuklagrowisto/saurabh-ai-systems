# transcriptsummary

A Claude Code skill that turns a single B2B sales-call transcript into a structured deal-stage diagnostic using the "5 Agreements" framework (Mark Kosoglow / *30 Minutes to President's Club*), layered with SPIN discovery notes and a BANT scorecard. Designed to tell a rep the truth about where a deal actually stands, rather than mistaking activity (a proposal sent, a friendly call) for real progress — strict evidence-only scoring, defaults to the lower confidence status when unclear.

Auto-translates Hindi/Hinglish transcripts to formal English before analysis.

Generic sales-methodology skill — the `[Your Company]` placeholder should be swapped for your own org name (search-replace) before use.

## Install

Copy `SKILL.md` into `~/.claude/skills/transcriptsummary/`.
