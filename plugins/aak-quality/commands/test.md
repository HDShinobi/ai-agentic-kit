---
name: test
description: Generate and run tests for code — unit, integration, and E2E as appropriate.
---

# /test - Test Generation & Execution

$ARGUMENTS

Create and run meaningful tests. Follow the best available method:

1. **If a testing skill is available, defer to it** — e.g. `superpowers:test-driven-development`, or (if `aak-workflow` is enabled) its `tdd-workflow` skill. Use `aak-quality`'s own `testing-patterns` / `webapp-testing` skills and `test-engineer` / `qa-automation-engineer` agents when available.
2. **Otherwise, test inline** with this protocol:
   - **Pick the level** — unit for logic, integration for boundaries, E2E for critical user flows (testing pyramid: many unit, fewer E2E).
   - **Write tests** following the project's existing framework and conventions; use the Arrange-Act-Assert shape.
   - **Cover** the happy path plus edge and failure cases for the code under test.
   - **Run them** and show the real output; fix failures or report them honestly.

## Output
The tests added, the command to run them, and the actual run result.
