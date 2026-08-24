# AI Agentic Kit

A broad Claude Code agent toolkit distributed as **one marketplace of eight domain plugins** (prefix `aak-`). Install the marketplace once, then **enable only the slices a given project needs** — breadth is the point; what you don't need, you simply don't enable.

Salvaged from [ag-kit](https://github.com/vudovn/ag-kit) © vudovn (MIT) and expanded with a deep marketing suite adapted from several open-source skill sets (see [NOTICE](NOTICE)). The Antigravity-specific plumbing is rewritten (native safety hook, main-thread orchestration, self-contained commands) or dropped. Current totals across the 8 plugins: **23 agents, 87 skills, 19 command workflows**.

## Install

```bash
# once per machine
/plugin marketplace add HDShinobi/ai-agentic-kit
# per project — enable only what you need
/plugin install aak-core@ai-agentic-kit
/plugin install aak-backend@ai-agentic-kit
```

Commands and skills are **namespaced** per plugin — e.g. `/aak-core:create`, `/aak-backend:deploy`. The `aak-workflow` plugin holds the process methodology **skills** (systematic-debugging, tdd-workflow, plan-writing, …) plus multi-agent orchestration; **skip installing it if you run the `superpowers` stack**, since those skills cover the same ground. The process **commands** (`/plan`, `/brainstorm`, `/debug`, `/verify`, `/test`) live in the active `aak-core`/`aak-quality` plugins and are self-contained (they defer to `superpowers` skills when present, otherwise run inline).

Local dev without publishing: `claude --plugin-dir ./plugins/aak-core`, then `/reload-plugins`.

## Plugin catalog

| Plugin | Covers | Agents | Notable skills | Commands |
|--------|--------|--------|----------------|----------|
| **aak-core** | Foundation — enable always | documentation-writer, product-manager, product-owner | app-builder, architecture, clean-code, code-review-graph, design-spec, simplify-code, i18n-localization | `/create`, `/enhance`, `/plan`, `/brainstorm` |
| **aak-backend** | Backend · data · API · devops · shell | backend-specialist, database-architect, devops-engineer | api-patterns, database-design, nodejs-best-practices, python-patterns, rust-pro, mcp-builder, server-management, deployment-procedures | `/deploy`, `/preview` |
| **aak-frontend** | Frontend · design · mobile | frontend-specialist, mobile-developer | frontend-architecture, frontend-design, nextjs-react-expert, tailwind-patterns, web-design-guidelines, mobile-design | — |
| **aak-security** | Offensive + defensive security | security-auditor, penetration-tester | vulnerability-scanner, red-team-tactics | — |
| **aak-quality** | Test · debug · review · performance | debugger, test-engineer, qa-automation-engineer, performance-optimizer, code-archaeologist, explorer-agent | testing-patterns, webapp-testing, code-review-checklist, performance-profiling, lint-and-validate | `/debug`, `/verify`, `/test` |
| **aak-marketing** | Full marketing: SEO/GEO · CRO · content · email · growth · analytics · brand · video (42 skills) | marketing-strategist, content-creator, growth-specialist, analytics-specialist, seo-specialist | conversion-optimization, page-cro, signup-flow-cro, keyword-research-deep, programmatic-seo, analytics-marketing, email-marketing, content-marketing, launch-strategy, brand, minimax-pdf | `/campaign`, `/content`, `/optimize`, `/analyze`, `/report`, `/brand-report` |
| **aak-game** | Game development | game-developer | game-development (router → 10 platform guides) | — |
| **aak-workflow** | Process methodology **skills** + orchestration (**skip if you use superpowers**) | project-planner | brainstorming, systematic-debugging, tdd-workflow, plan-writing, verify-changes, parallel-agents, coordinator-mode, intelligent-routing, memory-system, … | `/orchestrate`, `/coordinate`, `/status`, `/remember` |

**Enable only what you need.** Each plugin is self-contained: a command never depends on a skill from a plugin you haven't enabled — where richer cross-plugin capability exists, it is used only if that plugin is enabled, otherwise the work is done inline.

## Safety

`aak-core` ships a native `PreToolUse` hook (`hooks/guard.mjs`) that blocks a narrow set of high-confidence destructive Bash commands (root deletion, drive format, raw-disk writes — incl. macOS `/dev/rdisk*`). It is deliberately narrow and anchors commands at their position, so mentions like `echo "rm -rf /"` are not blocked. It is not a general linter.

## Development

- Validate: `claude plugin validate ./plugins/aak-<name>` (and `claude plugin validate .` for the marketplace).
- Safety-hook tests: `node --test plugins/aak-core/hooks/guard.test.mjs`.
- Migration converter (one-time, for re-deriving from ag-kit source): `scripts/convert.mjs` + `scripts/mapping.mjs`.

## License

MIT. See [LICENSE](LICENSE) (root and per-plugin). Adapted from [ag-kit](https://github.com/vudovn/ag-kit) © vudovn (MIT).
