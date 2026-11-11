# Acceptance-table reference

> `Design` below refers to the planning work that precedes any dispatch: Gate 1 (human design
> approval) plus the PLAN worker (see `SKILL.md` §1).

### Acceptance

One table: each requirement, the instrument that proves it, the plausible
wrong implementation that instrument rejects, and where that rejection was
observed.

**An acceptance row is invalid until its instrument discriminates.** A row
that passes both before and after the change proves nothing and will be
found at REVIEW. Baseline-red is not enough: red only because the feature
is absent says nothing about catching an implementation that is present,
runs, returns a pass, and is wrong. Each row names such a wrong
implementation. "The feature is absent" does not satisfy Counterexample.
Where none exists, the row says so and a human reads the diff.

Record what the instruments cannot observe. Prefer the simplest instrument
that proves the contract. Any claim about extent — a scope, a count, a set
of call sites — names the command that produced it, reports its output, and
enumerates rather than samples. Naming the command is not the measurement;
the command must have been run.


## Acceptance

| Requirement | Instrument | Counterexample | Observed red |
| --- | --- | --- | --- |
| | | | |

Design fills Counterexample; CODE fills Observed red. An empty cell is an
unfinished row. "The feature is absent" does not satisfy Counterexample. A row
with no counterexample must say so and say a human reads the diff — that escape
stays legal and is worth keeping only when someone actually reads it.

Every row's instrument must tell a pass from a failure. A row that cannot
discriminate is not acceptance; either replace the instrument or record that no
instrument exists and that a human reads the diff.

**Cannot be observed:** what the available instruments do not cover. A green suite
that never exercises a surface is not evidence about that surface.

