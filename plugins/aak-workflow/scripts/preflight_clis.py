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

def main(argv: list[str]) -> int:
    repo = Path(argv[1]) if len(argv) > 1 else Path.cwd()
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
    return 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
