<p align="center"><img src="assets/logo-banner.svg" alt="AI Agentic Kit" width="520"></p>

<p align="center"><b>Give Claude Code a full team of specialists — and switch on only the ones each project needs.</b></p>

<p align="center">
  <img src="https://img.shields.io/badge/license-MIT-blue?style=flat-square" alt="License">
  <img src="https://img.shields.io/badge/plugins-10-6f42c1?style=flat-square" alt="Plugins">
  <img src="https://img.shields.io/badge/agents-48-0969da?style=flat-square" alt="Agents">
  <img src="https://img.shields.io/badge/skills-129-1a7f37?style=flat-square" alt="Skills">
  <img src="https://img.shields.io/badge/commands-21-bf8700?style=flat-square" alt="Commands">
  <img src="https://img.shields.io/badge/Claude%20Code-marketplace-d4520f?style=flat-square" alt="Claude Code">
</p>

<p align="center"><b>English</b> · <a href="README.vi.md">Tiếng Việt</a></p>

---

**AI Agentic Kit** is one Claude Code marketplace of **10 domain plugins** — backend, frontend, security, testing, marketing, paid-media/ads, games, Vietnamese writing, and process orchestration. Install once, enable per project. No bloat, no lock-in: what you don't need, you don't turn on.

> **→ Get started:** `/plugin marketplace add HDShinobi/ai-agentic-kit` — then [enable the plugins you need](#-install).

## ✨ Why AI Agentic Kit

- **The right expert shows up on its own** — 48 specialist agents (debugger, security-auditor, frontend-specialist, marketing-strategist, audit-google…) auto-activate when your task matches, no wiring required.
- **Idea → launch without leaving the terminal** — 21 command workflows (`/create`, `/debug`, `/deploy`, `/audit`, `/campaign`, `/seo`) run each job end-to-end.
- **Enable only what a repo needs** — 10 independent, namespaced, self-contained plugins; turn on two, ignore the rest.
- **Safer by default** — a built-in guard blocks high-confidence destructive shell commands before they run.

## Contents

- [✨ Why AI Agentic Kit](#-why-ai-agentic-kit)
- [👥 Who it's for](#-who-its-for)
- [🚀 Install](#-install)
- [🧩 Plugin catalog](#-plugin-catalog)
- [⚙️ How activation works](#️-how-activation-works)
- [🗂 Command use cases](#-command-use-cases)
- [🛡 Safety](#-safety)
- [🧰 Development](#-development)
- [📄 License](#-license)

## 🚀 Install

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

> **Rule of thumb:** always install `aak-core` (foundation + the only safety hook). Add `aak-workflow` **only** when you have no superpowers-style stack.

Local dev without publishing: `claude --plugin-dir ./plugins/aak-core`, then `/reload-plugins`.

## 👥 Who it's for

- **Solo builders & indie hackers** — a whole team's worth of specialists without assembling a toolchain. → start with `aak-core` + the one or two domains your project touches.
- **Full-stack developers** — go from scaffold → deploy → test in one terminal. → `aak-core` + `aak-backend` + `aak-frontend` + `aak-quality`.
- **Builders who also do marketing** — ship the product *and* take it to market (SEO, content, campaigns, analytics). → add `aak-marketing`.
- **Security-conscious teams** — bake offensive + defensive review into the workflow. → add `aak-security`.
- **Already on `superpowers`?** — fully compatible: install everything except `aak-workflow` (its methodology skills overlap yours), and you keep the process *commands*.

## 🧩 Plugin catalog

| Plugin | What it does for you | Agents | Notable skills | Commands |
|--------|----------------------|--------|----------------|----------|
| **aak-core** | Scaffold, plan & ship apps — the foundation every project enables (and the only safety hook) | documentation-writer, product-manager, product-owner | app-builder, architecture, clean-code, code-review-graph, design-spec, simplify-code, i18n-localization | `/create`, `/enhance`, `/plan`, `/brainstorm` |
| **aak-backend** | Design APIs, model data & deploy to production with an expert on each | backend-specialist, database-architect, devops-engineer | api-patterns, database-design, nodejs-best-practices, python-patterns, rust-pro, mcp-builder, server-management, deployment-procedures | `/deploy`, `/preview` |
| **aak-frontend** | Build polished, on-brand UIs for web & mobile | frontend-specialist, mobile-developer | frontend-architecture, frontend-design, nextjs-react-expert, tailwind-patterns, web-design-guidelines, mobile-design, ui-ux-pro-max | — |
| **aak-security** | Find & fix vulnerabilities before attackers do | security-auditor, penetration-tester | vulnerability-scanner, red-team-tactics | — |
| **aak-quality** | Catch bugs, prove changes work & keep code fast | debugger, test-engineer, qa-automation-engineer, performance-optimizer, code-archaeologist, explorer-agent | testing-patterns, webapp-testing, code-review-checklist, performance-profiling, lint-and-validate | `/debug`, `/verify`, `/test` |
| **aak-marketing** | Take a product to market — SEO/GEO, CRO, content, email, growth, analytics, brand & video (44 skills) | marketing-strategist, content-creator, growth-specialist, analytics-specialist, seo-specialist | site-audit (scored site audit), client-proposal, conversion-optimization (CRO router), page-cro, keyword-research-deep, programmatic-seo, analytics-marketing, email-marketing, content-marketing, launch-strategy, brand, vision-analysis, minimax-pdf | `/audit`, `/campaign`, `/content`, `/optimize`, `/analyze`, `/seo`, `/report`, `/brand-report` |
| **aak-ads** | Run paid media like an agency — source-grounded audits + deterministic scoring across 12 ad platforms (Google, Meta, YouTube, LinkedIn, TikTok, Microsoft, Apple, Amazon, Reddit, Pinterest, Snapchat, X); read-only by default, account writes pass a mutation gate (34 skills, 25 agents) | 25 platform/audit/creative agents (audit-google, audit-meta, creative-strategist, copy-writer, visual-designer, source-verifier, …) | ads (router), ads-audit, ads-plan, ads-create, ads-launch, ads-monitor, ads-optimize, ads-test, ads-report, ads-attribution, ads-server-side-tracking, ads-math, + 12 platform skills | `/aak-ads:ads setup\|audit\|plan\|create\|launch\|monitor\|optimize\|experiment\|report` |
| **aak-game** | Ship games across engines & platforms | game-developer | game-development (router → 10 platform guides) | — |
| **aak-workflow** | Systematic process — brainstorm, plan, debug, verify — plus multi-agent orchestration (**skip if you use superpowers**) | project-planner | brainstorming, systematic-debugging, tdd-workflow, plan-writing, verify-changes, parallel-agents, coordinator-mode, intelligent-routing, memory-system, … | `/orchestrate`, `/coordinate`, `/status`, `/remember` |
| **aak-vietnamese** | Write native-quality Vietnamese (vi-VN) a local professional would ship — correct register, advertising-law-safe claims, clean VND/date/Unicode; composes with the content skills | — | vietnamese-landing-copy, vietnamese-business-comms, vietnamese-finance-copy, vietnamese-education-copy, vietnamese-tech-writing | — |

> **Enable only what you need.** Each plugin is self-contained: a command never depends on a skill from a plugin you haven't enabled — where richer cross-plugin capability exists, it is used only if that plugin is enabled, otherwise the work is done inline.

> **`aak-ads` ↔ `aak-marketing`:** they don't collide. `aak-marketing` stays authoritative for organic/SEO/content/brand. When **both** are enabled, `aak-ads` is the deep paid-media system and supersedes `aak-marketing`'s generalist `ppc-advertising` / `ad-creative-variations` for anything account-level (audits, budgets, launches, live-account changes) — those two skills carry a note that defers to `/aak-ads:ads` when it's present.

> **`aak-ads` release tooling is upstream-only.** `aak-ads` is vendored verbatim from the standalone [`claude-ads`](https://github.com/AgriciDaniel/claude-ads) repo. Its `scripts/release.py` (the `audit` / `build` / `verify` subcommands) is that repo's **standalone-repo release/packaging harness** — it expects a self-contained single-plugin repo (own `README.md` + a self-referential one-plugin `.claude-plugin/marketplace.json`), which by design does not exist for a vendored sub-plugin. It is kept byte-verbatim because `scripts/verify_target_lock.py` imports it as a library, but its CLI audit is **not applicable inside this kit**. Release/packaging readiness here is governed by the host marketplace: run `claude plugin validate .` (marketplace) and `claude plugin validate ./plugins/aak-ads` (plugin) at the repo root.

## ⚙️ How activation works

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
   │ no command:                        │ /command:
   │ match a skill/agent by description │ read the workflow in the command body,
   │ → auto-load / auto-spawn           │ delegate per its "Lead agent"
   └────┬───────────────────────────────┘
        │
   spawn subagent(s) via Task tool  (a subagent CANNOT spawn further subagents — one level only)
        │  each agent = its own context + a limited toolset (e.g. product-manager has no Write)
        │
   subagent returns → MAIN THREAD synthesizes → answers you
```

Two structural rules follow from this: **subagents are one level deep** (an agent can't call another agent — multi-agent coordination always runs on the main thread or via `/orchestrate`), and every command follows the **degradation rule** — *delegate to a specialist if its plugin is enabled, otherwise do that role inline* — so a command is never hollow even when you've enabled only `aak-core`.

## 🗂 Command use cases

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

#### The agency money-loop

The audit/report commands aren't standalone tools — they bookend a full **audit → propose → execute → prove → deliver** loop, the way an agency actually bills:

```
/aak-marketing:audit <url>   → 0–100 score + MARKETING-AUDIT.md (dated, kept as history)
        → client-proposal      (findings → a priced proposal)
        → 40+ delivery skills   (copy / email / CRO / SEO … do the real work)
        → /aak-marketing:audit  (re-run) → before/after DELTA   ← proof of the improvement
        → /report               (client-ready PDF)
```

The audit runs on a fixed, transparent scoring model (**rubrics, weights and report format**), and keeps a **dated audit history** so a re-run produces a **before/after delta** — you can *prove* the improvement you were paid for, then hand the client a PDF.

**Agency-loop commands** — run the loop above:

| Command | Use when | Lead / mechanism |
|---------|----------|------------------|
| `/audit` | score a site's marketing (content, CRO, SEO/GEO, brand, competitive, growth) → one dated report; re-run for a before/after delta | `marketing-strategist` |
| `/report` | export the results as a client-ready **PDF** | output tooling (`minimax-pdf`) |
| `/brand-report` | same PDF export, but **clone a brand's site style** from a URL first | output tooling (`minimax-pdf`) |

**Marketing-execution commands** — do the actual work:

| Command | Use when | Lead agent |
|---------|----------|-----------|
| `/campaign` | a **full campaign** end-to-end: brief → strategy → content → launch → optimize | `marketing-strategist` |
| `/content` | a single asset: brief → research → outline → write → optimize | `content-creator` |
| `/optimize` | raise conversion (CRO) for a page/funnel | `growth-specialist` + CRO router |
| `/analyze` | crunch the numbers, find insights, recommend actions | `analytics-specialist` |
| `/seo` | SEO + GEO audit/optimization (incl. AI-search visibility) | `seo-specialist` |

## 🛡 Safety

`aak-core` ships a native `PreToolUse` hook (`hooks/guard.mjs`) that blocks a narrow set of high-confidence destructive Bash commands (root deletion, drive format, raw-disk writes — incl. macOS `/dev/rdisk*`). It is deliberately narrow and anchors commands at their position, so mentions like `echo "rm -rf /"` are not blocked. It is not a general linter.

> **Install `aak-core` in every project.** It is the foundation plugin and the only one that ships the safety hook — enabling other plugins without it leaves Bash unguarded by this kit.

## 🧰 Development

- Validate: `claude plugin validate ./plugins/aak-<name>` (and `claude plugin validate .` for the marketplace).
- Safety-hook tests: `node --test plugins/aak-core/hooks/guard.test.mjs`.
- Migration converter (one-time, for re-deriving from source): `scripts/convert.mjs` + `scripts/mapping.mjs`.

> Built on and credits to prior open-source work — see [NOTICE](NOTICE) for full attribution.

## 📄 License

MIT. See [LICENSE](LICENSE) (root and per-plugin).
