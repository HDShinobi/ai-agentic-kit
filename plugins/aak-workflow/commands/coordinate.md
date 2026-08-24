---
name: coordinate
description: Advanced multi-agent coordination with parallel dispatch and synthesis. Use for complex tasks requiring multiple specialist perspectives.
---

# /coordinate — Advanced Multi-Agent Coordination

$ARGUMENTS

---

## 🔴 CRITICAL RULES

1. **Load coordinator-mode skill** — Read `${CLAUDE_PLUGIN_ROOT}/skills/coordinator-mode/SKILL.md` first
2. **Phase-based execution** — Research → Synthesis → Implementation → Verification
3. **Never delegate understanding** — Write specific prompts, not vague instructions
4. **Parallel reads, sequential writes** — Read-only tasks can run in parallel

---

## Delegation scope (degradation rule)

> **Delegate only to agents from plugins that are currently enabled** (`aak-backend:backend-specialist`, `aak-frontend:frontend-specialist`, `aak-security:security-auditor`, etc.). If a needed specialist's plugin is not enabled, **perform that role inline** rather than failing. Never assume a cross-plugin agent exists.

## Task

You run on the main thread — coordinate workers yourself using the **Task tool** (this command *is* the coordinator; there is no separate coordination subagent). Follow the `coordinator-mode` skill loaded above.

```
CONTEXT:
- User Request: $ARGUMENTS
- Mode: COORDINATOR (advanced orchestration)
- Skill: coordinator-mode (loaded from this plugin)

WORKFLOW:
1. DECOMPOSE the request into worker subtasks
2. CLASSIFY each subtask: Research | Implementation | Verification
3. DISPATCH workers via the Task tool (parallel for reads, sequential for writes)
4. SYNTHESIZE results — don't copy-paste, add insight
5. VERIFY completeness before reporting to user

RULES:
1. Follow coordinator-mode/SKILL.md protocol
2. Brief workers like smart colleagues — full context, specific scope
3. Never write "based on your findings, fix it" — prove YOU understood
4. Start with 2-3 workers, add more after synthesis if needed
5. Research before implementation — ALWAYS
6. Delegate only to enabled-plugin agents; otherwise do the role inline
```

---

## Expected Output

| Deliverable | Description |
|-------------|-------------|
| Worker Dispatch | List of agents invoked with task descriptions |
| Synthesis Report | Consolidated findings with YOUR analysis |
| Action Items | Specific next steps with file paths |

---

## After Coordination

```
[OK] Coordination complete

Agents dispatched: [count]
Phases completed: Research → Synthesis → [Implementation] → [Verification]

Key findings:
- [Finding 1]
- [Finding 2]

Next steps:
- [ ] [Action item 1]
- [ ] [Action item 2]
```
