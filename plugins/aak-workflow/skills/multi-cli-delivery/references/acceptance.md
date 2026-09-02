# Acceptance-table reference

> Vendored verbatim from dely (© Hieu Phung, MIT) under Golden Rule #4 (AI
> Agentic Kit vendors external artifacts byte-for-byte; see root `NOTICE`).
> Source: `hieuphung97/dely` `skills/delivery/SKILL.md` §Acceptance (+
> `skills/delivery/templates/plan.md` §Acceptance), vendored at dely commit
> `c2fc1a96dce4eabc5b8c9ee9dafbb66fb371d785`.
>
> Only phase-name wiring changed, both one-word swaps: dely's `implement` →
> this kit's `CODE` (in the `templates/plan.md` extract below — "Design
> fills Counterexample; CODE fills Observed red"); dely's `review` → this
> kit's `REVIEW` (in the `SKILL.md` extract below — "...will be found at
> REVIEW"). dely's capitalized `Design` is sentence-initial prose, not a
> phase heading — it refers to the undispatched, Control-authored planning
> work that precedes any dispatch. This kit splits that work across Gate 1
> (human design approval) and the PLAN worker, which is what actually
> carries the acceptance rows and counterexample in its handoff (see
> `SKILL.md` §1) — there is no single clean 1:1 mapping, so dely's original
> wording is left unchanged rather than re-pointed to either alone. Nothing
> else was added, removed, reordered, or reworded — the "Source:" lines
> below and this note are the only non-vendored text in this file.

*Source: `hieuphung97/dely` `skills/delivery/SKILL.md` §Acceptance*

### Acceptance

One table: each requirement, the instrument that proves it, the plausible
wrong implementation that instrument rejects, and where that rejection was
observed.

**An acceptance row is invalid until you have settled that its instrument
discriminates.** A row whose instrument passes both before and after the
change proves nothing and will be found at REVIEW. Baseline-red is
insufficient by itself: an instrument observed red only because the feature
is absent says nothing about whether it can catch an implementation that is
present, runs, returns a pass, and is wrong.

Each row names a plausible wrong implementation its instrument rejects — one
that exists, runs, and returns a pass. "The feature is absent" does not
satisfy Counterexample. Where no counterexample exists, the row says so and
says a human reads the diff.

Record what the available instruments cannot observe. Prefer the simplest
instrument that proves the contract.

*Source: `hieuphung97/dely` `skills/delivery/templates/plan.md` §Acceptance*

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

