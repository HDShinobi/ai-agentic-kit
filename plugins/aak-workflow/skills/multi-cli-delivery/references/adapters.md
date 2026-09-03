# Adapter reference

An adapter is everything Control needs to run one CLI **headless**: how to
invoke it, how to pin a model on it, whether it has a real effort knob, and
how it wants its prompt delivered. The protocol core is adapter-agnostic —
adding a new CLI is adding a new row here (and to the registry it mirrors),
never a change to the dispatch/containment/handoff machinery in `SKILL.md`.

This table mirrors `mcd_core/adapters.py`. **`claude` and `codex` are
live-verified against real installed CLIs on the machine that wrote this
table; `command-code`/`opencode`/`gemini`/`kiro` remain illustrative (not
installed there) — their prompt-delivery is UNVERIFIED (likely also stdin,
like claude and codex, but unconfirmed). Exact flags per CLI *version*
drift.** The registry module is the source of truth; update it first when a
CLI changes its interface, then bring this table in sync.

| Adapter id | Binary | Headless invocation | Model flag | Effort support | `prompt_via` |
|---|---|---|---|---|---|
| `claude` | `claude` | `claude -p --model <model>` (+ `--permission-mode acceptEdits` when writable) | `--model` | no | `stdin` |
| `codex` | `codex` | `codex exec -m <model> [-c model_reasoning_effort=<effort>] --skip-git-repo-check --sandbox <workspace-write\|read-only> -` | `-m` | yes — `-c model_reasoning_effort=<effort>` | `stdin` |
| `command-code` | `command-code` | `command-code -p --model <model> <prompt-file>` | `--model` | no | `arg` |
| `opencode` | `opencode` | `opencode run --model <model> <prompt-file>` | `--model` | no | `arg` |
| `gemini` | `gemini` | `gemini -p --model <model> <prompt-file>` | `--model` | no | `arg` |
| `kiro` | `kiro-cli` | `kiro-cli chat --no-interactive --trust-all-tools --model <model> <prompt-file>` | `--model` | no | `arg` |

`<model>` and `<prompt-file>` are placeholders filled in per dispatch from
the role's binding and the workspace-local prompt file — never a literal
model name baked into the adapter (Golden Rule #1: this kit ships no
hardcoded model list). Neither `claude` nor `codex` takes a `<prompt-file>`
CLI argument at all — both read the prompt from stdin, so the dispatcher
pipes the prompt file's bytes into the child's stdin for them instead (see
`prompt_via` below).

**Role-aware sandbox/permission (spec §4.5):** only the CODE role is
workspace-write; PLAN and REVIEW stay read-only. `compose_argv` takes a
`writable` keyword so the dispatcher — `dispatch_worker.py`, which sets
`writable = (role == "code")` — can tell each adapter which case applies.
`claude` appends `--permission-mode acceptEdits` only when writable (headless
claude otherwise cannot edit files); `codex` always passes `--sandbox`, set to
`workspace-write` when writable and `read-only` otherwise. The other four
adapters accept the same `writable` keyword (so the dispatcher can call all
six uniformly) but ignore it — they have no analogous flag today.

> claude + codex are live-verified; gemini/command-code/kiro prompt-delivery
> is UNVERIFIED (likely also stdin) — verify when installed.

## Reading the columns

- **Binary** — the executable name preflight/dispatch actually look for on
  `PATH`. It usually matches the adapter id; today `kiro` is the one
  exception, resolving to the `kiro-cli` binary. A new adapter whose package
  name differs from the id it's registered under sets this the same way.
- **`prompt_via`** — how the dispatcher hands the worker its prompt.
  - `arg` — the prompt file's path is appended to argv as a trailing
    argument; the child's own stdin is left at `/dev/null` (the
    hang-prevention default — see SKILL.md §7).
  - `stdin` — the dispatcher opens the prompt file itself and pipes its
    bytes into the child's stdin instead. `claude` and `codex` are wired this
    way today, because both read their prompt from stdin rather than an
    argument. Every adapter still exposes the same `compose_argv(binding,
    prompt_file, *, writable=False)` shape regardless of which mode it uses
    or whether it acts on `writable`, so the dispatcher never special-cases
    argv construction — only which file descriptor the prompt goes into and
    which role gets write access.
- **Effort support** — whether the adapter has a real, native reasoning-
  effort knob to translate a role's `effort:` setting into. Only `codex` has
  one today. Setting `effort:` on a role bound to an adapter with no such
  knob is never silently dropped: preflight reports it in `effort_warnings`
  (SKILL.md §2) so the human sees it. There is no effort→model-tier
  substitution anywhere in the registry — an adapter only ever translates a
  *real* native flag, never fakes one by picking a different model.

## Two rules every adapter follows

- **Model and effort are named on every dispatch** — a worker is never left
  on the CLI's own default; an unpinned dispatch is an unpinned environment.
- **The prompt is written to a temp file outside the run workspace**, never
  inline in a shell argument (prompts routinely carry backticks, quotes, and
  newlines that would break argv construction or shell-escape unsafely). For
  `stdin` adapters the dispatcher pipes that file's bytes to the worker on
  stdin — the worker never sees the file path; `arg` adapters instead receive
  the path itself as a trailing argument (see `prompt_via` above).

## First-party vs. foreign models

`claude` and `codex` are expected to run against their own first-party
endpoints — nothing in this registry redirects them to a foreign base URL. A
third-party or self-hosted model is reached through one of the multi-model-
shell adapters (`command-code`, `opencode`) instead. Dispatching through one
of those carries the data-egress acknowledgement described in SKILL.md §8 —
first-party dispatches need none.
