#!/usr/bin/env python3
"""Thin CLI over mcd_core.dispatch. Composes adapter argv, wires prompt
delivery per adapter.prompt_via (Ruling B: "arg" adapters get the prompt file
path as a trailing CLI arg; "stdin" adapters — codex — get it piped to the
child's stdin), runs the worker headless, then deterministically parses the
handoff out of stdout (mcd_core.handoff.parse_handoff — the tested exit0 +
sentinel + last-match untrusted-output gate) so Control never hand-parses raw
worker output. Any mcd_core config/spawn error (bad config, unknown adapter,
spawn failure) is caught and reported as structured JSON with a non-zero exit
rather than a raw traceback. A worker that ran but produced no valid handoff
(truncated output, killed on timeout, nonzero exit) is reported inline as
`"success": false` — the CLI process itself still exits 0, because it did its
job (ran the worker, tried to parse); the worker's outcome is data for
Control, not a failure of this script. Usage:
    python3 "${CLAUDE_PLUGIN_ROOT}/scripts/dispatch_worker.py" \
        --role code --repo <path> --prompt-file <p> --cwd <workspace> \
        [--cli <id>] [--model <name>]
`--cli`/`--model` (spec §11 per-run override) supersede the config's binding
for this one dispatch only — they never edit .aak/delivery.yml.
"""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from mcd_core.config import load_delivery_config, RoleBinding
from mcd_core.adapters import get_adapter
from mcd_core.dispatch import run_worker
from mcd_core.errors import McdError, HandoffError
from mcd_core.handoff import parse_handoff

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--role", required=True)
    ap.add_argument("--repo", required=True, type=Path)
    ap.add_argument("--prompt-file", required=True, type=Path)
    ap.add_argument("--cwd", required=True, type=Path)
    ap.add_argument("--cli", default=None,
                    help="per-run override: supersede the config's cli for this dispatch only (spec §11)")
    ap.add_argument("--model", default=None,
                    help="per-run override: supersede the config's model for this dispatch only (spec §11)")
    args = ap.parse_args()
    try:
        cfg = load_delivery_config(args.repo)
        if cfg is None or args.role not in cfg.roles:
            print(json.dumps({"error": f"no config/role for {args.role!r}"}))
            return 1
        binding = cfg.roles[args.role]
        # spec §11 per-run override: --cli/--model win for THIS dispatch only;
        # applied before get_adapter() so an override can even dodge a config
        # binding to an unknown/unavailable cli id. Never written back to
        # .aak/delivery.yml — that file stays the reproducible default.
        binding = RoleBinding(args.cli or binding.cli, args.model or binding.model, binding.effort)
        adapter = get_adapter(binding.cli)
        argv = adapter.compose_argv(binding, args.prompt_file)
        # Ruling B: only "stdin" adapters (codex) get the prompt piped to
        # stdin; every other adapter already has the prompt file in argv, and
        # the child's stdin stays /dev/null (dispatch.py's hang-prevention
        # default).
        stdin_file = args.prompt_file if adapter.prompt_via == "stdin" else None
        tp = cfg.timeouts.get(args.role)
        wall = tp.wall_sec if tp else 60 * 60
        idle = tp.idle_sec if tp else 10 * 60
        out = run_worker(argv, cwd=args.cwd, wall_sec=wall, idle_sec=idle,
                         prompt_file=args.prompt_file, stdin_file=stdin_file)
    except McdError as exc:
        # Config errors, unknown adapters, spawn failures (DispatchError) —
        # every typed mcd_core failure becomes structured JSON, never a
        # traceback, so Control can always parse stdout.
        print(json.dumps({"error": str(exc)}))
        return 1
    result = {"stdout": out.stdout, "exit_code": out.exit_code,
             "tripped": out.tripped, "forensics": out.forensics}
    # Deterministic success gate (spec §4.6/§6.1): a handoff is a SUCCESS only
    # when the worker exited 0 AND emitted the END OF HANDOFF sentinel. A
    # tripped (wall/idle) run kills the worker -> exit_code != 0 ->
    # parse_handoff raises HandoffError -> success is False here, correctly:
    # a hung worker is never a success.
    try:
        h = parse_handoff(out.stdout, out.exit_code)
        result["success"] = True
        result["handoff"] = {"status": h.status, "role": h.role, "model": h.model,
                             "disposition": h.disposition, "changed_paths": h.changed_paths,
                             "verification": h.verification}
    except HandoffError as exc:
        result["success"] = False
        result["handoff_error"] = str(exc)
    print(json.dumps(result))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
