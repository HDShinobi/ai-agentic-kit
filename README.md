# AI Agentic Kit

A broad Claude Code agent toolkit distributed as **one marketplace of eight domain plugins** (prefix `aak-`). Install the marketplace once, then **enable only the slices a given project needs** — breadth is the point; what you don't need, you simply don't enable.

Salvaged from [ag-kit](https://github.com/vudovn/ag-kit) © vudovn (MIT) and expanded with a deep marketing suite adapted from several open-source skill sets (see [NOTICE](NOTICE)). The Antigravity-specific plumbing is rewritten (native safety hook, main-thread orchestration, self-contained commands) or dropped. Current totals across the 8 plugins: **23 agents, 87 skills, 20 command workflows**.

## Install

```bash
# once per machine
/plugin marketplace add HDShinobi/ai-agentic-kit
# per project — enable only what you need
/plugin install aak-core@ai-agentic-kit
/plugin install aak-backend@ai-agentic-kit
```

Commands and skills are **namespaced** per plugin — e.g. `/aak-core:create`, `/aak-backend:deploy`. The `aak-workflow` plugin holds the process methodology **skills** (systematic-debugging, tdd-workflow, plan-writing, …) plus multi-agent orchestration; **skip installing it if you run the `superpowers` stack**, since those skills cover the same ground. The process **commands** (`/plan`, `/brainstorm`, `/debug`, `/verify`, `/test`) live in the active `aak-core`/`aak-quality` plugins and are self-contained (they defer to `superpowers` skills when present, otherwise run inline).

### Recommended install

**If you already run the [superpowers](https://github.com/obra/superpowers) stack** (or any brainstorm/plan/debug/verify/test skill set): install `aak-core` + the domain plugins you need, and **do NOT install `aak-workflow`**. You still get the process **commands** (`/plan`, `/brainstorm`, `/debug`, `/verify`, `/test` — they defer to your superpowers skills), with **zero skill-selection collisions**, because the overlapping methodology *skills* live only in `aak-workflow`.

```bash
/plugin install aak-core@ai-agentic-kit          # always — foundation + safety hook
/plugin install aak-backend@ai-agentic-kit        # pick the domains you need
/plugin install aak-frontend@ai-agentic-kit
/plugin install aak-marketing@ai-agentic-kit
# ...aak-security / aak-quality / aak-game as needed
# aak-workflow: SKIP (superpowers already covers its methodology skills)
```

**If you do NOT run superpowers** and want a full self-contained process layer: also install `aak-workflow` for the methodology skills + orchestration.

> Rule of thumb: **always install `aak-core`** (foundation + the only safety hook). Add `aak-workflow` **only** when you have no superpowers-style stack.

Local dev without publishing: `claude --plugin-dir ./plugins/aak-core`, then `/reload-plugins`.

## Plugin catalog

| Plugin | Covers | Agents | Notable skills | Commands |
|--------|--------|--------|----------------|----------|
| **aak-core** | Foundation — enable always | documentation-writer, product-manager, product-owner | app-builder, architecture, clean-code, code-review-graph, design-spec, simplify-code, i18n-localization | `/create`, `/enhance`, `/plan`, `/brainstorm` |
| **aak-backend** | Backend · data · API · devops · shell | backend-specialist, database-architect, devops-engineer | api-patterns, database-design, nodejs-best-practices, python-patterns, rust-pro, mcp-builder, server-management, deployment-procedures | `/deploy`, `/preview` |
| **aak-frontend** | Frontend · design · mobile | frontend-specialist, mobile-developer | frontend-architecture, frontend-design, nextjs-react-expert, tailwind-patterns, web-design-guidelines, mobile-design, ui-ux-pro-max | — |
| **aak-security** | Offensive + defensive security | security-auditor, penetration-tester | vulnerability-scanner, red-team-tactics | — |
| **aak-quality** | Test · debug · review · performance | debugger, test-engineer, qa-automation-engineer, performance-optimizer, code-archaeologist, explorer-agent | testing-patterns, webapp-testing, code-review-checklist, performance-profiling, lint-and-validate | `/debug`, `/verify`, `/test` |
| **aak-marketing** | Full marketing: SEO/GEO · CRO · content · email · growth · analytics · brand · video (41 skills) | marketing-strategist, content-creator, growth-specialist, analytics-specialist, seo-specialist | conversion-optimization (CRO router), page-cro, signup-flow-cro, keyword-research-deep, programmatic-seo, analytics-marketing, email-marketing, content-marketing, launch-strategy, brand, minimax-pdf | `/campaign`, `/content`, `/optimize`, `/analyze`, `/seo`, `/report`, `/brand-report` |
| **aak-game** | Game development | game-developer | game-development (router → 10 platform guides) | — |
| **aak-workflow** | Process methodology **skills** + orchestration (**skip if you use superpowers**) | project-planner | brainstorming, systematic-debugging, tdd-workflow, plan-writing, verify-changes, parallel-agents, coordinator-mode, intelligent-routing, memory-system, … | `/orchestrate`, `/coordinate`, `/status`, `/remember` |

**Enable only what you need.** Each plugin is self-contained: a command never depends on a skill from a plugin you haven't enabled — where richer cross-plugin capability exists, it is used only if that plugin is enabled, otherwise the work is done inline.

## How activation works

The kit ships three kinds of component, and they activate in **three different ways** — this is the part most people get wrong:

| Component | Lives in | How it fires | Who triggers it |
|-----------|----------|--------------|-----------------|
| **Skill** (`skills/*/SKILL.md`) | every plugin | Claude reads its `description` and loads it when the task matches | the model, automatically |
| **Agent** (`agents/*.md`) | every plugin | Claude spawns it as a subagent (via the Task tool) when the task matches its `description` + `Triggers on …` keywords | the model automatically, **or** a command that names it as lead |
| **Command** (`commands/*.md`) | some plugins | runs **only** when you type `/plugin:command` | you, explicitly — never auto-fires |

### Two ways an agent kicks in

- **Implicit (you just chat).** You describe a task without typing a command. The main thread (Claude) reads the `description` of every *enabled* agent and, when your task matches the keywords, spawns that agent as a subagent. Example: *"the login API throws 500, find it"* matches `debugger` (`Triggers on: bug, error, broken, investigate`) → Claude runs `debugger` with a read/edit toolset, it investigates and reports back.
- **Explicit (you run a command).** A command is a pre-written workflow script. Its body names a `> **Lead agent:**` to drive the phases, which then pulls in other specialists. Example: `/campaign` is driven by `marketing-strategist`, which delegates content to `content-creator`, SEO to `seo-specialist`, and so on.

### Request lifecycle

```
your request / /command
        │
   [MAIN THREAD = Claude]          ← always here; only the main thread can spawn subagents
        │
   ┌────┴───────────────────────────────┐
   │ no command:                         │ /command:
   │ match a skill/agent by description   │ read the workflow in the command body,
   │ → auto-load / auto-spawn            │ delegate per its "Lead agent"
   └────┬───────────────────────────────┘
        │
   spawn subagent(s) via Task tool  (a subagent CANNOT spawn further subagents — one level only)
        │  each agent = its own context + a limited toolset (e.g. product-manager has no Write)
        │
   subagent returns → MAIN THREAD synthesizes → answers you
```

Two structural rules follow from this: **subagents are one level deep** (an agent can't call another agent — multi-agent coordination always runs on the main thread or via `/orchestrate`), and every command follows the **degradation rule** — *delegate to a specialist if its plugin is enabled, otherwise do that role inline* — so a command is never hollow even when you've enabled only `aak-core`.

## Command use cases

Each command is a distinct workflow with a clear "use when". They also chain: `/campaign` calls `/content` for each asset, then hands measurement to `/analyze` → `/report`.

### Dev track

| Command | Use when | Lead / mechanism |
|---------|----------|------------------|
| `/aak-core:create` | starting a brand-new app | `app-builder` skill → scoping → `DESIGN.md` → build |
| `/aak-core:enhance` | adding/changing a feature in an existing app | iterative, no re-scaffold |
| `/aak-core:plan` | you want a **plan file** only (task breakdown), no code yet | `project-planner`, plan-only |
| `/aak-core:brainstorm` | direction unclear — compare multiple approaches first | defers to `superpowers`/`brainstorming` |
| `/aak-backend:deploy`, `/preview` | production release / local dev server | `devops-engineer`, with pre-flight checks |
| `/aak-quality:debug` | a hard bug — **root-cause before fixing** | `systematic-debugging`, evidence-based |
| `/aak-quality:test`, `/verify` | generate & run tests / prove changes actually run | `test-engineer` |
| `/aak-workflow:orchestrate`, `/coordinate` | a big task needing **3+ specialist perspectives** in parallel | main thread spawns multiple agents |

### Marketing track (`aak-marketing`)

| Command | Use when | Lead agent |
|---------|----------|-----------|
| `/campaign` | a **full campaign** end-to-end: brief → strategy → content → launch → optimize | `marketing-strategist` |
| `/content` | a single asset: brief → research → outline → write → optimize | `content-creator` |
| `/optimize` | raise conversion (CRO) for a page/funnel | `growth-specialist` + CRO router |
| `/analyze` | crunch the numbers, find insights, recommend actions | `analytics-specialist` |
| `/seo` | SEO + GEO audit/optimization (incl. AI-search visibility) | `seo-specialist` |
| `/report`, `/brand-report` | export a **professional PDF** (`/brand-report` clones a brand's site style from a URL) | output tooling (`minimax-pdf`) |

## Safety

`aak-core` ships a native `PreToolUse` hook (`hooks/guard.mjs`) that blocks a narrow set of high-confidence destructive Bash commands (root deletion, drive format, raw-disk writes — incl. macOS `/dev/rdisk*`). It is deliberately narrow and anchors commands at their position, so mentions like `echo "rm -rf /"` are not blocked. It is not a general linter.

> **Install `aak-core` in every project.** It is the foundation plugin and the only one that ships the safety hook — enabling other plugins without it leaves Bash unguarded by this kit.

## Development

- Validate: `claude plugin validate ./plugins/aak-<name>` (and `claude plugin validate .` for the marketplace).
- Safety-hook tests: `node --test plugins/aak-core/hooks/guard.test.mjs`.
- Migration converter (one-time, for re-deriving from ag-kit source): `scripts/convert.mjs` + `scripts/mapping.mjs`.

## License

MIT. See [LICENSE](LICENSE) (root and per-plugin). Adapted from [ag-kit](https://github.com/vudovn/ag-kit) © vudovn (MIT).
