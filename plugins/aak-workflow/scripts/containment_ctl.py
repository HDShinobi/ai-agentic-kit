#!/usr/bin/env python3
"""Thin CLI over mcd_core.containment -- the git blast-radius guard (spec
§4.8). Workers have no git authority; Control alone commits, and this is how
Control invokes the deterministic checks at runtime instead of hand-rolling
git subprocess calls: snapshot/restore git-control state around a worker
run, detect the drift a rogue commit or ref/index change would leave behind,
compute the true changed-path set (Ruling-A: tracked + untracked + ignored,
so e.g. a leaked secret in a .gitignore'd file can't slip past scope),
classify what a candidate touched outside its declared ownership, and commit
ONLY owned paths with a commit==reviewed-diff verification. Mirrors
dispatch_worker.py/workspace_ctl.py's contract: any mcd_core failure
(ContainmentError, or any other McdError) becomes structured JSON on stdout
with a non-zero exit -- never a raw traceback -- so Control can always parse
stdout.

`GitState` (head, refs, index_tree -- all JSON-native) round-trips through a
JSON statefile so a snapshot taken before a worker run survives to the
detect-drift/restore call made after it, across separate CLI invocations.

Usage:
    python3 "${CLAUDE_PLUGIN_ROOT}/scripts/containment_ctl.py" snapshot \
        --repo <path> --out <statefile>
    python3 "${CLAUDE_PLUGIN_ROOT}/scripts/containment_ctl.py" detect-drift \
        --repo <path> --state <statefile>
    python3 "${CLAUDE_PLUGIN_ROOT}/scripts/containment_ctl.py" restore \
        --repo <path> --state <statefile>
    python3 "${CLAUDE_PLUGIN_ROOT}/scripts/containment_ctl.py" changed-paths \
        --repo <path> --baseline <ref>
    python3 "${CLAUDE_PLUGIN_ROOT}/scripts/containment_ctl.py" classify-scope \
        --changed <comma,separated,paths> --owned <comma,separated,paths>
    python3 "${CLAUDE_PLUGIN_ROOT}/scripts/containment_ctl.py" commit-owned \
        --repo <path> --owned <comma,separated,paths> --message <str> \
        [--force-add <comma,separated,paths>]
"""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from mcd_core.containment import (
    GitState, snapshot_git_state, detect_git_drift, restore_git_state,
    changed_paths, classify_scope, commit_owned,
)
from mcd_core.errors import McdError

def _parse_list(s: str | None) -> list[str]:
    if not s:
        return []
    return [p.strip() for p in s.split(",") if p.strip()]

def _load_state(path: Path) -> GitState:
    data = json.loads(path.read_text(encoding="utf-8"))
    return GitState(head=data["head"], refs=data["refs"], index_tree=data["index_tree"])

def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="action", required=True)

    p_snap = sub.add_parser("snapshot")
    p_snap.add_argument("--repo", required=True, type=Path)
    p_snap.add_argument("--out", required=True, type=Path)

    p_drift = sub.add_parser("detect-drift")
    p_drift.add_argument("--repo", required=True, type=Path)
    p_drift.add_argument("--state", required=True, type=Path)

    p_restore = sub.add_parser("restore")
    p_restore.add_argument("--repo", required=True, type=Path)
    p_restore.add_argument("--state", required=True, type=Path)

    p_changed = sub.add_parser("changed-paths")
    p_changed.add_argument("--repo", required=True, type=Path)
    p_changed.add_argument("--baseline", required=True)

    p_scope = sub.add_parser("classify-scope")
    p_scope.add_argument("--changed", required=True,
                         help="comma-separated repo-relative paths that changed")
    p_scope.add_argument("--owned", required=True,
                         help="comma-separated repo-relative paths the candidate owns")

    p_commit = sub.add_parser("commit-owned")
    p_commit.add_argument("--repo", required=True, type=Path)
    p_commit.add_argument("--owned", required=True,
                          help="comma-separated repo-relative paths to commit")
    p_commit.add_argument("--message", required=True)
    p_commit.add_argument("--force-add", default=None,
                          help="comma-separated owned paths to force-add despite .gitignore")

    args = ap.parse_args()
    try:
        if args.action == "snapshot":
            state = snapshot_git_state(args.repo)
            args.out.write_text(
                json.dumps({"head": state.head, "refs": state.refs,
                           "index_tree": state.index_tree}),
                encoding="utf-8")
            print(json.dumps({"ok": True, "state": str(args.out)}))
        elif args.action == "detect-drift":
            before = _load_state(args.state)
            print(json.dumps({"drift": detect_git_drift(args.repo, before)}))
        elif args.action == "restore":
            before = _load_state(args.state)
            restore_git_state(args.repo, before)
            print(json.dumps({"restored": True}))
        elif args.action == "changed-paths":
            changed = changed_paths(args.repo, args.baseline)
            print(json.dumps({"changed": sorted(changed)}))
        elif args.action == "classify-scope":
            out_of_scope = classify_scope(set(_parse_list(args.changed)),
                                          set(_parse_list(args.owned)))
            print(json.dumps({"out_of_scope": sorted(out_of_scope)}))
        elif args.action == "commit-owned":
            sha = commit_owned(args.repo, _parse_list(args.owned), args.message,
                               force_add=_parse_list(args.force_add))
            print(json.dumps({"sha": sha}))
    except McdError as exc:
        # ContainmentError (git failure, a .gitignore'd owned path without
        # force_add, commit contents != reviewed diff) or any other typed
        # mcd_core failure -- structured JSON, never a traceback, matching
        # dispatch_worker.py/workspace_ctl.py's contract.
        print(json.dumps({"error": str(exc)}))
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
