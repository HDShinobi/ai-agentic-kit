---
description: Turn a scored marketing audit (or a stated goal) into a sequenced, AARRR-based marketing action plan.
---

# /marketing-plan - Marketing Action Plan

> **The bridge between a proposal and execution.** Takes the scored gaps from `/audit`
> (`MARKETING-AUDIT.md`) or a stated goal/stage/budget and produces a prioritized,
> stage-based (AARRR) plan that hands each stage off to the specialist skills — turning
> the agency money-loop into a complete operating system: **audit → context → proposal →
> plan → execute → re-audit → report**.

This command runs the `marketing-plan` skill (in `aak-marketing`).

## Step 1: Gather inputs
- A scored audit (`MARKETING-AUDIT.md`) if `/audit` has been run — its scored gaps seed the plan.
- Otherwise: the product/goal, stage (pre-launch / early / growth / scale), and budget/constraints.
- Optional: `.agents/product-marketing.md` — the shared positioning/ICP/voice doc (created by
  the `product-marketing` skill). If present, the plan reuses it instead of re-asking.

## Step 2: Build the plan
Follow the `marketing-plan` skill: diagnose the measured funnel bottleneck (AARRR), pull a
short **scored** shortlist from the `marketing-ideas` skill (never an exhaustive dump;
note the `marketing-plan` skill's own Section 12 draws from its internal 139-idea library,
while the `marketing-ideas` skill is the interactive MFS-scored selector — use whichever the
current step calls for),
sequence the work stage-by-stage, and hand each stage to its owner skill
(`product-marketing`, `offers`, `pricing-strategy`, `content-marketing`, `sales-enablement`,
`revops`, `churn-prevention`, …). Produce the plan document in-conversation (no filesystem
writes or external publishing unless the user explicitly asks).

## Handoffs
- `/aak-marketing:campaign` · `/aak-marketing:content` · `/aak-marketing:optimize` ·
  `/aak-marketing:seo` — execute the plan's stages.
- `/aak-marketing:report` — render the plan as a polished client PDF.
- Re-run `/aak-marketing:audit` after execution to measure the before/after delta.
