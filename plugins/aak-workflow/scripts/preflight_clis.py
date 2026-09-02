#!/usr/bin/env python3
"""Thin CLI over mcd_core.preflight. Emits JSON; the OUTCOME is in the JSON,
not the exit code (Control parses structured data). Usage:
    python3 "${CLAUDE_PLUGIN_ROOT}/scripts/preflight_clis.py" <repo_root>
"""
from __future__ import annotations
import json, os, shutil, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # import mcd_core
from mcd_core.config import load_delivery_config
from mcd_core.preflight import probe
from mcd_core.adapters import effort_warnings
from mcd_core.errors import McdError

def main(argv: list[str]) -> int:
    repo = Path(argv[1]) if len(argv) > 1 else Path.cwd()
    try:
        cfg = load_delivery_config(repo)
        if cfg is None:
            print(json.dumps({"roles": {}, "inert": True,
                              "reason": ".aak/delivery.yml absent — skill inert"}))
            return 0
        roles = {}
        for name, binding in cfg.roles.items():
            r = probe(binding, cfg.secrets, which=shutil.which, env=os.environ,
                      on_missing_auth=cfg.defaults.on_missing_auth)
            roles[name] = {"outcome": r.outcome, "reason": r.reason}
        print(json.dumps({"roles": roles, "effort_warnings": effort_warnings(cfg)}))
    except McdError as exc:
        # Malformed/invalid .aak/delivery.yml (bad types, unknown keys, etc.):
        # preflight's contract is that Control always parses JSON off stdout
        # -- the outcome/error lives IN the JSON, never the exit code. Return
        # 0 here on purpose (unlike dispatch_worker.py's non-zero-on-error
        # contract, which is a different script with a different contract).
        print(json.dumps({"roles": {}, "error": str(exc)}))
    return 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
