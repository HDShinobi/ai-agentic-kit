---
name: clean-code
description: Pragmatic coding standards - concise, direct, no over-engineering, no unnecessary comments Always active for ALL code writing. Enforces concise, direct coding standards, testing pyramid, and performance best practices.
allowed-tools: Read, Write, Edit
---

# Clean Code - Pragmatic AI Coding Standards

> **CRITICAL SKILL** - Be **concise, direct, and solution-focused**.

---

## Core Principles

| Principle | Rule |
|-----------|------|
| **SRP** | Single Responsibility - each function/class does ONE thing |
| **DRY** | Don't Repeat Yourself - extract duplicates, reuse |
| **KISS** | Keep It Simple - simplest solution that works |
| **YAGNI** | You Aren't Gonna Need It - don't build unused features |
| **Boy Scout** | Leave code cleaner than you found it |

---

## Naming Rules

| Element | Convention |
|---------|------------|
| **Variables** | Reveal intent: `userCount` not `n` |
| **Functions** | Verb + noun: `getUserById()` not `user()` |
| **Booleans** | Question form: `isActive`, `hasPermission`, `canEdit` |
| **Constants** | SCREAMING_SNAKE: `MAX_RETRY_COUNT` |

> **Rule:** If you need a comment to explain a name, rename it.

---

## Function Rules

| Rule | Description |
|------|-------------|
| **Small** | Max 20 lines, ideally 5-10 |
| **One Thing** | Does one thing, does it well |
| **One Level** | One level of abstraction per function |
| **Few Args** | Max 3 arguments, prefer 0-2 |
| **No Side Effects** | Don't mutate inputs unexpectedly |

---

## Code Structure

| Pattern | Apply |
|---------|-------|
| **Guard Clauses** | Early returns for edge cases |
| **Flat > Nested** | Avoid deep nesting (max 2 levels) |
| **Composition** | Small functions composed together |
| **Colocation** | Keep related code close |

---

## AI Coding Style

| Situation | Action |
|-----------|--------|
| User asks for feature | Write it directly |
| User reports bug | Fix it, don't explain |
| No clear requirement | Ask, don't assume |

---

## Anti-Patterns (DON'T)

| ❌ Pattern | ✅ Fix |
|-----------|-------|
| Comment every line | Delete obvious comments |
| Helper for one-liner | Inline the code |
| Factory for 2 objects | Direct instantiation |
| utils.ts with 1 function | Put code where used |
| "First we import..." | Just write code |
| Deep nesting | Guard clauses |
| Magic numbers | Named constants |
| God functions | Split by responsibility |

---

## 🔴 Before Editing ANY File (THINK FIRST!)

**Before changing a file, ask yourself:**

| Question | Why |
|----------|-----|
| **What imports this file?** | They might break |
| **What does this file import?** | Interface changes |
| **What tests cover this?** | Tests might fail |
| **Is this a shared component?** | Multiple places affected |

**Quick Check:**
```
File to edit: UserService.ts
└── Who imports this? → UserController.ts, AuthController.ts
└── Do they need changes too? → Check function signatures
```

> 🔴 **Rule:** Edit the file + all dependent files in the SAME task.
> 🔴 **Never leave broken imports or missing updates.**

---

## Summary

| Do | Don't |
|----|-------|
| Write code directly | Write tutorials |
| Let code self-document | Add obvious comments |
| Fix bugs immediately | Explain the fix first |
| Inline small things | Create unnecessary files |
| Name things clearly | Use abbreviations |
| Keep functions small | Write 100+ line functions |

> **Remember: The user wants working code, not a programming lesson.**

---

## 🔴 Self-Check Before Completing (MANDATORY)

**Before saying "task complete", verify:**

| Check | Question |
|-------|----------|
| ✅ **Goal met?** | Did I do exactly what user asked? |
| ✅ **Files edited?** | Did I modify all necessary files? |
| ✅ **Code works?** | Did I test/verify the change? |
| ✅ **No errors?** | Lint and TypeScript pass? |
| ✅ **Nothing forgotten?** | Any edge cases missed? |

> 🔴 **Rule:** If ANY check fails, fix it before completing.

---

## Verification Scripts (MANDATORY)

> 🔴 **CRITICAL:** Each agent runs ONLY their own skill's scripts after completing work.

### Domain audit scripts (each ships with the skill that owns it)

Each audit script lives inside its owning skill, which usually sits in **another plugin**. Because `${CLAUDE_PLUGIN_ROOT}` resolves to the invoking plugin only, you cannot call another plugin's script by path. Instead: **run a domain's audit only if that plugin is enabled** (invoke it through that plugin's skill/agent), and **otherwise fall back to the project's own equivalent command**. Only the i18n check ships in this same `aak-core` plugin.

| Domain | Owning skill · plugin | If plugin enabled | Fallback |
|--------|-----------------------|-------------------|----------|
| UX / A11y audit | `frontend-design` · `aak-frontend` | run its UX/accessibility audit | project's a11y linter |
| API validation | `api-patterns` · `aak-backend` | run its API validator | project's API/contract tests |
| Mobile audit | `mobile-design` · `aak-frontend` | run its mobile audit | platform linters |
| Schema validate | `database-design` · `aak-backend` | run its schema validator | migration/ORM checks |
| Security scan | `vulnerability-scanner` · `aak-security` | run its security scan | project's SAST/audit |
| SEO / GEO check | `seo-fundamentals` / `geo-fundamentals` · `aak-marketing` | run its checker | manual SEO review |
| Lighthouse / perf | `performance-profiling` · `aak-quality` | run its Lighthouse audit | `lighthouse` CLI |
| Test / Playwright | `testing-patterns` / `webapp-testing` · `aak-quality` | run its runner | project's `test` command |
| Lint / type coverage | `lint-and-validate` · `aak-quality` | run its lint/type check | project's linter/type-checker |
| i18n check | `i18n-localization` · **`aak-core`** (this plugin) | `python3 "${CLAUDE_PLUGIN_ROOT}/skills/i18n-localization/scripts/i18n_checker.py" .` | — |

> Each domain runs its **own** audit — e.g. the UX audit belongs to the frontend role, not the test role.

---

### 🔴 Script Output Handling (READ → SUMMARIZE → ASK)

**When running a validation script, you MUST:**

1. **Run the script** and capture ALL output
2. **Parse the output** - identify errors, warnings, and passes
3. **Summarize to user** in this format:

```markdown
## Script Results: [script_name.py]

### ❌ Errors Found (X items)
- [File:Line] Error description 1
- [File:Line] Error description 2

### ⚠️ Warnings (Y items)
- [File:Line] Warning description

### ✅ Passed (Z items)
- Check 1 passed
- Check 2 passed

**Should I fix the X errors?**
```

4. **Wait for user confirmation** before fixing
5. **After fixing** → Re-run script to confirm

> 🔴 **VIOLATION:** Running script and ignoring output = FAILED task.
> 🔴 **VIOLATION:** Auto-fixing without asking = Not allowed.
> 🔴 **Rule:** Always READ output → SUMMARIZE → ASK → then fix.


---

## Universal standards (folded from ag-kit `universal-rules` + `code-rules`)

These are the concrete, always-applicable standards. (The dispatcher/agent-routing and always-on protocol prose from the original rules is intentionally dropped — it duplicated and fought native selection.)

### Language handling
- When the user's prompt is not in English: understand it, and **respond in the user's language**.
- **Code, identifiers, and comments stay in English.**

### Code / testing / performance / safety
- **Code:** concise, direct, self-documenting. No over-engineering, no speculative abstraction.
- **Testing:** mandatory. Follow the testing pyramid (Unit > Integration > E2E) and the AAA (Arrange-Act-Assert) pattern.
- **Performance:** measure first; meet current Core Web Vitals where relevant.
- **Infra/Safety:** verify secrets are not committed; treat deployment as a staged, verified process.

### Plan-first for non-trivial work (4 phases)
1. **Analysis** — research and clarifying questions (ask before assuming when anything material is unclear).
2. **Planning** — a short `{task-slug}.md` task breakdown.
3. **Solutioning** — architecture/design decisions (no code yet).
4. **Implementation** — code + tests.

### Final-check order
When asked to "run the final checks," run the project's own tooling in this priority order and fix blockers before proceeding:

1. **Security** → 2. **Lint / static analysis** → 3. **Schema** (if a DB changed) → 4. **Tests** → 5. **UX / accessibility** (if UI changed) → 6. **SEO** (if pages changed) → 7. **Performance / E2E** (before deploy).

A task is not finished until the relevant checks pass. Use each domain plugin's own tooling when that plugin is enabled (see the audit-script table above); otherwise run the repository's configured commands.
