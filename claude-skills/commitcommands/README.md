# commitcommands

Three Claude Code git-workflow slash commands:
- `/commit` — stage and commit with a generated message
- `/commitpushpr` — commit, push, and open a PR in one shot (no per-step confirmation — reads git status/diff/branch, then runs commit → push → `gh pr create`)
- `/cleangone` — delete local branches whose remote has been deleted

**Source:** [anthropics/claude-code](https://github.com/anthropics/claude-code/tree/main/plugins/commit-commands) `plugins/commit-commands` (Apache-2.0 License). Reproduced here unmodified for convenience (files renamed to drop hyphens: `commit-push-pr.md` → `commitpushpr.md`, `clean_gone.md` → `cleangone.md`).

## Install

Copy the three files under `commands/` into `~/.claude/commands/`. Requires `gh` installed and authenticated.
