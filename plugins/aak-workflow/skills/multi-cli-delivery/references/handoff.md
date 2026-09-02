# Handoff block reference

Every worker prompt (PLAN, CODE, REVIEW) instructs the CLI to close its
output with a fixed, structured block. This is the *only* part of a worker's
output Control treats as authoritative — everything else the worker printed
is untrusted narration (see SKILL.md §8) and is read, if at all, for context,
never for control flow.

## The block

```
Status: DONE | BLOCKED | NEEDS_REPLAN
Role: plan | code | review
Model: <model the worker believes it ran as>
Changed paths: <every touched path, on this one line, space- or comma-separated>
Contract coverage: <which acceptance rows this addresses>
Verification: <what was actually run, its output, and the outcome>
Deviations: <where this differs from the contract, and why>
Unresolved: <open questions or risks the worker could not close itself>
Disposition: ACCEPT | CHANGES_REQUESTED | BLOCKED   (REVIEW only)
END OF HANDOFF
```

`END OF HANDOFF` is the load-bearing sentinel. Its absence means the worker's
output was cut off mid-write — Control retries once, then escalates; it never
guesses at a partial block.

## Field by field

- **Status** — the worker's own terminal call for this dispatch: `DONE` (it
  produced a result), `BLOCKED` (it cannot proceed without a decision only
  Control or the human can make), or `NEEDS_REPLAN` (the task as given does
  not hold up and needs replanning). This is what drives SKILL.md's
  status-transition table.
- **Role** — which role the worker believes it was dispatched as. A
  self-report Control can sanity-check against what it actually dispatched,
  not proof of anything on its own.
- **Model** — which model the worker believes it ran as. Also a self-report,
  not proof: Control's real assurance about model identity comes from the
  trusted config/runtime side (SKILL.md §6); this field can only *flag* a
  mismatch, never confirm independence.
- **Changed paths** — every path the worker believes it touched. Control's
  own containment scan (SKILL.md §5) is the actual authority on scope; this
  field is a cross-check and a log line, not the source of truth.
- **Contract coverage** — the worker's account of which of its task
  contract's acceptance rows it addressed. Free text, read directly by
  Control rather than pulled apart by the deterministic parser (see below).
  The acceptance-row discipline itself is documented separately in
  `references/acceptance.md`.
- **Verification** — what the worker actually ran to convince itself the
  change is correct: the command(s), their output, and the outcome. A
  Verification line describing no real command run is a signal to distrust
  the `Status`, not proof of anything.
- **Deviations** — anywhere the worker's approach differs from what the
  contract asked for, and why.
- **Unresolved** — open questions, risks, or gaps the worker could not close
  on its own.
- **Disposition** — REVIEW only. `ACCEPT` (the candidate meets its contract),
  `CHANGES_REQUESTED` (specific, addressable gaps — triggers the single
  remediation pass), or `BLOCKED` (the reviewer cannot render an accept/
  changes-requested verdict at all — an unresolved authority or dependency
  question, not a quality judgment; Control treats it exactly like a REVIEW
  `Status: BLOCKED`).

## What the deterministic parser reads vs. what Control reads

Control's handoff parser mechanically extracts six fields into structured
data — `Status`, `Role`, `Model`, `Changed paths`, `Disposition`, and
`Verification` — because those are the ones automated control flow branches
on. `Contract coverage`, `Deviations`, and `Unresolved` stay as free text
inside the block; Control (the orchestrating session) reads them directly
when deciding whether to commit, escalate, or fold something into its report
— they don't need a rigid grammar because a person or an LLM, not a fixed
parser, is the consumer. PLAN's handoff additionally carries a structured
task-contract payload (the decomposition itself: owned paths, acceptance
rows, counterexample, authority, per-task options) as its own section within
the block; Control reads that directly too rather than through this
field-by-field parser.

## Two hard rules the format depends on

**(a) The block must be one contiguous run of these fields, immediately
before `END OF HANDOFF` — no narration in between.** The parser scopes to
everything before the *last* occurrence of the sentinel in the worker's
output, then for each field name takes the *last* matching line inside that
scope. That is deliberate: it lets the real block win over an earlier
look-alike line buried in untrusted narration (a worker musing about a
"Model:" it considered and rejected, say, earlier in its output). But that
same last-match rule is exactly why the block cannot have narration mixed
into it — a stray line between two fields that happens to start with a
tracked prefix (e.g. a `Deviations:` note that itself mentions "Model:
fallback") would silently become that field's parsed value. So: pack the
nine lines tight, with the sentinel immediately after the last one, and
nothing else in between.

**(b) `Changed paths:` is a single line, not one path per line.** The parser
takes only the text that follows the prefix on that one line; anything on a
following line is not part of the value — at best it's dropped, at worst it
gets matched as a different field if it happens to start with a tracked
prefix. List every changed path on the `Changed paths:` line itself,
separated by spaces or commas.

## The success gate lives outside this file

A syntactically complete block is necessary but not sufficient. A handoff
only counts as a success when the worker's process **also exited 0**
(SKILL.md §4, §7) — a complete `END OF HANDOFF` block from a process that was
killed on timeout or crashed after writing it is diagnostic output, never an
accepted result.

---

Handoff format and status/disposition taxonomy adapted from the dely
protocol (© Hieu Phung, MIT); re-authored. (The acceptance-table discipline
`Contract coverage` refers to is vendored separately, byte-for-byte, in
`references/acceptance.md`.)
