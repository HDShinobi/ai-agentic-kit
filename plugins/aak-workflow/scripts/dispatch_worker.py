#!/usr/bin/env python3
"""Thin CLI over mcd_core.dispatch. Composes adapter argv, wires prompt
delivery per adapter.prompt_via (Ruling B: "arg" adapters get the prompt file
path as a trailing CLI arg; "stdin" adapters — codex — get it piped to the
child's stdin), runs the worker headless, prints JSON. Any mcd_core error
(bad config, unknown adapter, spawn failure) is caught and reported as
structured JSON with a non-zero exit rather than a raw traceback. Usage:
    python3 "${CLAUDE_PLUGIN_ROOT}/scripts/dispatch_worker.py" \
        --role code --repo <path> --prompt-file <p> --cwd <workspace>
"""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from mcd_core.config import load_delivery_config
from mcd_core.adapters import get_adapter
from mcd_core.dispatch import run_worker
from mcd_core.errors import McdError

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--role", required=True)
    ap.add_argument("--repo", required=True, type=Path)
    ap.add_argument("--prompt-file", required=True, type=Path)
    ap.add_argument("--cwd", required=True, type=Path)
    args = ap.parse_args()
    try:
        cfg = load_delivery_config(args.repo)
        if cfg is None or args.role not in cfg.roles:
            print(json.dumps({"error": f"no config/role for {args.role!r}"}))
            return 1
        binding = cfg.roles[args.role]
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
    print(json.dumps({"stdout": out.stdout, "exit_code": out.exit_code,
                      "tripped": out.tripped, "forensics": out.forensics}))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
