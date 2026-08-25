#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Replay trussary's eval corpus against the vendored per-skill validators.

Non-vendored acceptance tool (authored for aak-vietnamese). Stdlib only.

    python3 plugins/aak-vietnamese/.acceptance/replay_evals.py plugins/aak-vietnamese/evals

For each evals/<skill>/pairs.jsonl row:
  * run skills/<skill>/scripts/validate_copy.py on the row's string with
    --json --strict (+ --register/--doctype when present), writing the string
    to a temp file named by the row's `filename` when present;
  * BAD row: assert every expected_rules id is emitted AND exit != 0
    (skip both when expected_rules is empty — documented not-machine-detectable);
  * GOOD row: assert no findings AND exit == 0.
Exit non-zero if any row misbehaves.
"""
from __future__ import annotations
import json, subprocess, sys, tempfile, pathlib

def run_validator(validator: pathlib.Path, text: str, filename, register, doctype):
    with tempfile.TemporaryDirectory() as d:
        # Sanitize: use only the final path component so a corpus `filename`
        # like "../x" or "/etc/x" cannot write outside the temp dir.
        name = pathlib.Path(filename).name if filename else "sample.md"
        if not name or name in (".", ".."):
            name = "sample.md"
        f = pathlib.Path(d) / name
        f.write_text(text, encoding="utf-8")
        cmd = [sys.executable, str(validator), str(f), "--json", "--strict"]
        if register: cmd += ["--register", register]
        if doctype:  cmd += ["--doctype", doctype]
        p = subprocess.run(cmd, capture_output=True, text=True)
        try:
            rules = {x["rule"] for x in json.loads(p.stdout).get("findings", [])}
        except Exception:
            rules = set()
        return p.returncode, rules, p.stdout + p.stderr

def main() -> int:
    evals_dir = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "plugins/aak-vietnamese/evals")
    skills_dir = evals_dir.parent / "skills"
    failures = []
    checked = 0
    for corpus in sorted(evals_dir.glob("*/pairs.jsonl")):
        skill = corpus.parent.name
        validator = skills_dir / skill / "scripts" / "validate_copy.py"
        if not validator.exists():
            failures.append(f"{skill}: MISSING validator {validator}")
            continue
        for line in corpus.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            rid = row.get("id", "?")
            fn, reg, dt = row.get("filename"), row.get("register"), row.get("doctype")
            expected = set(row.get("expected_rules", []))
            # BAD
            if "bad" in row:
                code, rules, out = run_validator(validator, row["bad"], fn, reg, dt)
                if expected:
                    checked += 1
                    missing = expected - rules
                    if missing:
                        failures.append(f"{skill}/{rid} BAD: missing {sorted(missing)} (got {sorted(rules)})")
                    if code == 0:
                        failures.append(f"{skill}/{rid} BAD: expected non-zero exit under --strict")
            # GOOD
            if "good" in row:
                code, rules, out = run_validator(validator, row["good"], fn, reg, dt)
                checked += 1
                if rules:
                    failures.append(f"{skill}/{rid} GOOD: unexpected findings {sorted(rules)}")
                if code != 0:
                    failures.append(f"{skill}/{rid} GOOD: expected exit 0, got {code}")
    print(f"checked {checked} assertions across {len(list(evals_dir.glob('*/pairs.jsonl')))} corpora")
    if failures:
        print(f"FAIL ({len(failures)}):")
        for f in failures:
            print("  -", f)
        return 1
    print("REPLAY_OK")
    return 0

if __name__ == "__main__":
    sys.exit(main())
