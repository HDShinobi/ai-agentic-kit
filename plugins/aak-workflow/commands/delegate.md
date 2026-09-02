---
name: delegate
description: Deliver an approved change via heterogeneous multi-CLI dispatch — plan/code/review on different AI-CLIs+models, headless, in an isolated git worktree, with Control (Claude) owning every git write and humans owning the two approval gates. Use when you have a substantial change you want implemented by one model and independently reviewed by another. NOT for single-model multi-perspective analysis — that is /orchestrate.
---

# Multi-CLI Delivery — /aak-workflow:delegate

Invoke the **multi-cli-delivery** skill and follow its playbook (SKILL.md) for
this request, passing the request through unchanged.

## Request
$ARGUMENTS

---

## Distinct from `/orchestrate`

This command and `/orchestrate` share no code path — pick the one that matches the work:

| | `/aak-workflow:delegate` (this command) | `/orchestrate` |
|---|---|---|
| Actors | Multiple **models**, each in its own headless CLI **process** | One model (Claude), in-process **subagents** via the Task tool |
| Use for | A change to be *implemented* by one model and *independently reviewed* by another | Multi-perspective analysis/review from a single model wearing different specialist hats |
| Isolation | Runs in an isolated git worktree; Control owns every git write | Runs on the main thread; the orchestrator owns the diff directly |

If what you want is several angles on one problem from Claude itself, use
`/orchestrate` instead — this command is for cross-model, cross-process
delivery specifically.

## Per-run role overrides (spec §11)

`.aak/delivery.yml` (if present) is the reproducible default for every role.
To override a role for **this run only**, pass `--code cli:model` and/or
`--review cli:model` on the command line — a per-run override takes
precedence over the config for that run, but never edits the file:

```
/aak-workflow:delegate --code codex:gpt-5.6-terra --review claude:opus \
  Add rate limiting to the /api/upload endpoint
```

`codex:gpt-5.6-terra` and `claude:opus` above are illustrative CLI:model
pairs, not a mandated choice — bind each role to whatever `cli`/`model` you
actually have installed and authenticated (Golden Rule #1: this kit
hardcodes no project's model). Timeout and workspace policy are **not**
overridable per-run — those stay config-first in `.aak/delivery.yml`, where
reproducibility matters more than one-off convenience.

## Degradation

- **No `.aak/delivery.yml`** — the skill is inert: there is nothing to
  dispatch. Say so and stop; do not guess a config or silently fall back to
  another workflow.
- **A role's `cli` binary is absent** — that role degrades to a Claude Task
  subagent instead of failing the run (Golden Rule #1: a Claude-only install
  still completes every role, just without a heterogeneous model for it).
  Preflight's other outcomes (e.g. a configured-but-unauthenticated CLI)
  follow SKILL.md §2 — this command does not repeat that table.
