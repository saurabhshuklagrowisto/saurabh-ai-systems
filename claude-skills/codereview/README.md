# codereview

A Claude Code `/codereview` slash command for automated pull request review: launches multiple specialized agents in parallel to independently audit changes (CLAUDE.md compliance, obvious bugs, git-blame history), then filters findings by confidence score (threshold 80) to cut false positives.

**Source:** [anthropics/claude-code](https://github.com/anthropics/claude-code/tree/main/plugins/code-review) `plugins/code-review` (Apache-2.0 License), by Boris Cherny. Reproduced here unmodified for convenience.

## Install

Copy `commands/codereview.md` into `~/.claude/commands/`. Requires the GitHub CLI (`gh`) installed and authenticated. Run with `/codereview [--comment]`.
