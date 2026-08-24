---
name: debug
description: Systematic, evidence-based debugging — root-cause a bug before proposing a fix.
---

# /debug - Systematic Debugging

$ARGUMENTS

Debug by evidence, not by guessing. Follow the best available method:

1. **If a debugging skill is available, defer to it** — e.g. `superpowers:systematic-debugging`, or (if `aak-workflow` is enabled) its `systematic-debugging` skill. If `aak-quality`'s `debugger` agent is available, delegate the investigation to it.
2. **Otherwise, debug inline** with this protocol:
   - **Reproduce** — establish a reliable repro and the exact expected-vs-actual.
   - **Isolate** — narrow the failure with logs/bisection; find the smallest failing case.
   - **Hypothesize** — form one testable hypothesis about the root cause; gather evidence for/against it before changing code.
   - **Fix at the root** — not the symptom.
   - **Verify** — prove the fix by running it (see `/aak-quality:verify`); confirm no regression.

## Output
Report: root cause (with evidence), the fix, and the verification result.
