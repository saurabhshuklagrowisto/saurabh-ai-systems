# caveman

A Claude Code skill for ultra-compressed, token-efficient responses ("caveman mode") — cuts output tokens while keeping full technical accuracy. Supports intensity levels (`lite`/`full`/`ultra`/`wenyan-lite`/`wenyan-full`/`wenyan-ultra`) and automatically drops the compressed style for security warnings, irreversible-action confirmations, and anywhere fragment-speak would risk misreading.

**Source:** [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) (MIT License). Reproduced here unmodified for convenience.

## Install

Copy `SKILL.md` into `~/.claude/skills/caveman/`. Activate with `/caveman` or "use caveman skill"; deactivate with "stop caveman" / "normal mode".
