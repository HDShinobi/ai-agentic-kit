#!/usr/bin/env python3
"""Thin CLI over mcd_core.workspace. Wires the run-start branch/overlap gates
and worktree-lifecycle prepare step (spec §4.8, §4.9, §5.1 step 1) so Control
invokes real git through mcd_core instead of hand-rolling git subprocess calls.
Mirrors dispatch_worker.py/preflight_clis.py's contract: any mcd_core failure
(ContainmentError from a git failure or detached HEAD, or any other McdError)
becomes structured JSON on stdout with a non-zero exit -- never a raw
traceback -- so Control can always parse stdout. Usage:
    python3 "${CLAUDE_PLUGIN_ROOT}/scripts/workspace_ctl.py" branch-gate \
        --repo <path>
    python3 "${CLAUDE_PLUGIN_ROOT}/scripts/workspace_ctl.py" overlap-gate \
        --repo <path> --owned <comma,separated,paths>
    python3 "${CLAUDE_PLUGIN_ROOT}/scripts/workspace_ctl.py" prepare \
        --repo <path> --branch <name> [--mode worktree|shared] \
        [--workspaces-dir <path>]
"""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from mcd_core.workspace import prepare_workspace, overlap_gate, branch_gate
from mcd_core.errors import McdError

def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="action", required=True)

    p_branch = sub.add_parser("branch-gate")
    p_branch.add_argument("--repo", required=True, type=Path)

    p_overlap = sub.add_parser("overlap-gate")
    p_overlap.add_argument("--repo", required=True, type=Path)
    p_overlap.add_argument("--owned", required=True,
                           help="comma-separated repo-relative paths the caller owns")

    p_prepare = sub.add_parser("prepare")
    p_prepare.add_argument("--repo", required=True, type=Path)
    p_prepare.add_argument("--branch", required=True)
    p_prepare.add_argument("--mode", choices=("worktree", "shared"), default="worktree")
    p_prepare.add_argument("--workspaces-dir", default=None, type=Path)

    args = ap.parse_args()
    try:
        if args.action == "branch-gate":
            print(json.dumps({"branch": branch_gate(args.repo)}))
        elif args.action == "overlap-gate":
            owned = [p.strip() for p in args.owned.split(",") if p.strip()]
            print(json.dumps({"overlap": overlap_gate(args.repo, owned)}))
        elif args.action == "prepare":
            ws = prepare_workspace(args.repo, args.branch, workspace_mode=args.mode,
                                   workspaces_dir=args.workspaces_dir)
            print(json.dumps({"workspace": str(ws.resolve())}))
    except McdError as exc:
        # ContainmentError (detached HEAD, any git failure) or any other typed
        # mcd_core failure -- structured JSON, never a traceback, matching
        # dispatch_worker.py's contract for actions.
        print(json.dumps({"error": str(exc)}))
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
