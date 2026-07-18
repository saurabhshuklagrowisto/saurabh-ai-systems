# reviewpr

A deeper Claude Code `/reviewpr` slash command backed by six specialist review agents: `code-reviewer` (CLAUDE.md compliance + bugs + security), `code-simplifier`, `comment-analyzer`, `pr-test-analyzer`, `silent-failure-hunter`, and `type-design-analyzer`.

**Source:** [anthropics/claude-code](https://github.com/anthropics/claude-code/tree/main/plugins/pr-review-toolkit) `plugins/pr-review-toolkit` (Apache-2.0 License). Reproduced here unmodified for convenience.

## Install

Copy `commands/reviewpr.md` into `~/.claude/commands/` and everything under `agents/` into `~/.claude/agents/`. Run with `/reviewpr`.

**Note:** if you're also installing [`featuredev`](../featuredev) from this collection, its `code-reviewer` agent was renamed to `feature-dev-code-reviewer` to avoid clobbering this plugin's `code-reviewer` agent — both ship an agent with that same name.
