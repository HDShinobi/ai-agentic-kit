---
name: verify
description: Prove code changes work by actually running them — evidence before claiming done.
---

# /verify - Verify by Execution

$ARGUMENTS

Prove the work, don't assert it. Follow the best available method:

1. **If a verification skill is available, defer to it** — e.g. `superpowers:verification-before-completion`, or (if `aak-workflow` is enabled) its `verify-changes` skill. If `aak-quality`'s `test-engineer` agent is available, delegate.
2. **Otherwise, verify inline** with this protocol:
   - **Run it** — execute the changed code / the project's test, lint, type-check, and build commands. Never claim success from reading code alone.
   - **Show the evidence** — paste the actual command output (pass/fail), not a summary.
   - **Cover the change** — exercise the specific behavior that changed, including one edge/failure case.
   - **Report honestly** — if something fails or was skipped, say so with the output.

## Output
A short verification report: commands run, their real output, and a clear pass/fail verdict.
