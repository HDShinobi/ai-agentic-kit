---
name: brainstorm
description: Structured idea exploration — generate and compare multiple approaches before committing to an implementation.
---

# /brainstorm - Structured Idea Exploration

$ARGUMENTS

Explore options before building. Follow the best available method:

1. **If a brainstorming skill is available, defer to it** — e.g. `superpowers:brainstorming`, or (if `aak-workflow` is enabled) its `brainstorming` skill.
2. **Otherwise, brainstorm inline** with this protocol:
   - **Understand the goal** — the problem, the user, the constraints.
   - **Generate ≥3 distinct approaches** — including at least one unconventional one; give each pros, cons, and an effort estimate (Low/Medium/High).
   - **Compare and recommend** — summarize the tradeoffs and recommend one with reasoning.

## Output format
```markdown
## 🧠 Brainstorm: [Topic]
### Context
[problem statement]
### Option A / B / C: [name]
[description] — ✅ pros / ❌ cons / 📊 effort
### Recommendation
[choice + reasoning]
```
