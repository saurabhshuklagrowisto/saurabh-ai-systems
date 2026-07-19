# Third-party tools

These aren't my code — I use them as part of my Claude Code setup, listed here with credit rather than vendored into this repo (they're actively maintained upstream, and copying them in would just go stale).

| Tool | What it is | Source |
|---|---|---|
| **graphify** | Turns a codebase (or docs/PDFs/images/video) into a local, queryable knowledge graph via tree-sitter — `/graphify` to build it, then query/path/explain against it instead of re-reading files from scratch. | [Graphify-Labs/graphify](https://github.com/Graphify-Labs/graphify) (MIT) |
| **ruflo — security-audit plugin** | Security review, dependency/CVE scanning, policy gates for the codebase. | [ruvnet/ruflo](https://github.com/ruvnet/ruflo), plugin `ruflo-security-audit` (MIT) |
| **ruflo — aidefence plugin** | PII detection and prompt-injection/adversarial-input scanning before untrusted data reaches a model or gets executed. | [ruvnet/ruflo](https://github.com/ruvnet/ruflo), plugin `ruflo-aidefence` (MIT) |

`ruflo` ships as a marketplace of 34 independent plugins — I installed only these two rather than the full framework, since the rest overlaps with other tooling already in use.
