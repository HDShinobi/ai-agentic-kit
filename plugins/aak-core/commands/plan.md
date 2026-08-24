---
name: plan
description: Create a project plan file (task breakdown, dependencies, verification) — no code writing, plan only.
---

# /plan - Project Planning

$ARGUMENTS

Produce a plan file only — **no code**. Follow the best available method:

1. **If a planning skill is available, defer to it** — e.g. `superpowers:writing-plans`, or (if `aak-workflow` is enabled) its `plan-writing` skill and `project-planner` agent.
2. **Otherwise, plan inline** with this protocol:
   - **Scope gate:** ask 2–3 clarifying questions if anything material is unclear (goal, users, constraints).
   - **Break down** the work into ordered, verifiable tasks with dependencies.
   - **Name the file** from 2–3 keywords of the request: lowercase, hyphenated, ≤30 chars (e.g. "e-commerce cart" → `ecommerce-cart.md`).
   - **Write `{task-slug}.md`** at the project root containing: goal, task breakdown, dependencies, and a verification checklist.
   - Do **not** write any code files; report the exact plan filename created.

## After planning
Tell the user the plan file name and suggest next steps (review it, then `/aak-core:create` to implement, or edit the plan).
