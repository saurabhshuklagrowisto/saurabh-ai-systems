# featuredev

A guided 7-phase Claude Code `/featuredev` workflow for feature implementation: discovery → codebase exploration (`code-explorer` agents) → clarifying questions → architecture design (`code-architect` agents, multiple trade-off options) → implementation → quality review (`feature-dev-code-reviewer` agents) → summary.

**Source:** [anthropics/claude-code](https://github.com/anthropics/claude-code/tree/main/plugins/feature-dev) `plugins/feature-dev` (Apache-2.0 License).

**Modified:** the original ships an agent named `code-reviewer`, which collides with the identically-named agent in [`reviewpr`](../reviewpr). Renamed to `feature-dev-code-reviewer` (agent file + its one reference inside `commands/featuredev.md`) so both plugins can be installed side by side without one silently overwriting the other.

## Install

Copy `commands/featuredev.md` into `~/.claude/commands/` and everything under `agents/` into `~/.claude/agents/`. Run with `/featuredev [feature description]`.
