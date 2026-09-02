from __future__ import annotations
from pathlib import Path
import mcd_core
from mcd_core import errors

PLUGIN_ROOT = Path(__file__).resolve().parent.parent

def test_package_exposes_version_and_error_hierarchy():
    assert isinstance(mcd_core.__version__, str) and mcd_core.__version__
    for name in ("ConfigError", "HandoffError", "ContainmentError",
                 "DispatchError", "PreflightError"):
        exc = getattr(errors, name)
        assert issubclass(exc, errors.McdError)

def test_plugin_manifest_present():
    assert (PLUGIN_ROOT / ".claude-plugin" / "plugin.json").is_file()

# --- Task 10: thin CLI entrypoints over mcd_core (preflight_clis.py, dispatch_worker.py) ---

import json, subprocess, sys, textwrap

def test_preflight_cli_emits_json(tmp_path):
    (tmp_path / ".aak").mkdir()
    (tmp_path / ".aak" / "delivery.yml").write_text(textwrap.dedent("""
        roles:
          review: {cli: claude, model: opus}
    """), encoding="utf-8")
    script = PLUGIN_ROOT / "scripts" / "preflight_clis.py"
    out = subprocess.run([sys.executable, str(script), str(tmp_path)],
                         capture_output=True, text=True,
                         env={"PATH": "/usr/bin:/bin", "PYTHONPATH": str(PLUGIN_ROOT)})
    assert out.returncode == 0, out.stderr
    data = json.loads(out.stdout)
    assert "roles" in data and "review" in data["roles"]

def test_preflight_cli_is_inert_without_config(tmp_path):
    # CLI contract: absent .aak/delivery.yml -> {"roles": {}, "inert": true, ...}, exit 0.
    script = PLUGIN_ROOT / "scripts" / "preflight_clis.py"
    out = subprocess.run([sys.executable, str(script), str(tmp_path)],
                         capture_output=True, text=True,
                         env={"PATH": "/usr/bin:/bin", "PYTHONPATH": str(PLUGIN_ROOT)})
    assert out.returncode == 0, out.stderr
    data = json.loads(out.stdout)
    assert data["roles"] == {} and data.get("inert") is True

def test_preflight_cli_malformed_config_emits_json_error(tmp_path):
    # Fix round 1: a malformed .aak/delivery.yml (roles as a list/scalar,
    # unknown keys, bad types) raises mcd_core.errors.ConfigError inside
    # load_delivery_config. preflight_clis.py must still honor its contract
    # -- exit 0, error IN the JSON on stdout -- not an uncaught traceback.
    (tmp_path / ".aak").mkdir()
    (tmp_path / ".aak" / "delivery.yml").write_text("roles: oops\n", encoding="utf-8")
    script = PLUGIN_ROOT / "scripts" / "preflight_clis.py"
    out = subprocess.run([sys.executable, str(script), str(tmp_path)],
                         capture_output=True, text=True,
                         env={"PATH": "/usr/bin:/bin", "PYTHONPATH": str(PLUGIN_ROOT)})
    assert out.returncode == 0, out.stderr
    data = json.loads(out.stdout)
    assert data["roles"] == {} and "error" in data

def _write_delivery_yml(repo: Path, role: str, cli: str, model: str) -> None:
    (repo / ".aak").mkdir(exist_ok=True)
    (repo / ".aak" / "delivery.yml").write_text(textwrap.dedent(f"""
        roles:
          {role}: {{cli: {cli}, model: {model}}}
    """), encoding="utf-8")

def _make_fake_bin(bin_dir: Path, name: str, body: str) -> None:
    """A minimal fake CLI on PATH, run by the SAME interpreter as the test process
    (absolute-path shebang -- no dependency on a system python3 being on PATH)."""
    bin_dir.mkdir(exist_ok=True)
    script = bin_dir / name
    script.write_text(f"#!{sys.executable}\n{body}", encoding="utf-8")
    script.chmod(0o755)

def _run_dispatch_worker(repo: Path, role: str, prompt_text: str, path_env: str,
                         cli: str | None = None, model: str | None = None):
    prompt = repo / "prompt.txt"
    prompt.write_text(prompt_text, encoding="utf-8")
    script = PLUGIN_ROOT / "scripts" / "dispatch_worker.py"
    argv = [sys.executable, str(script), "--role", role, "--repo", str(repo),
           "--prompt-file", str(prompt), "--cwd", str(repo)]
    if cli is not None:
        argv += ["--cli", cli]
    if model is not None:
        argv += ["--model", model]
    return subprocess.run(
        argv, capture_output=True, text=True, timeout=30,
        env={"PATH": path_env, "PYTHONPATH": str(PLUGIN_ROOT)},
    )

def test_dispatch_worker_cli_missing_config_emits_error_json(tmp_path):
    out = _run_dispatch_worker(tmp_path, "code", "hello\n", "/usr/bin:/bin")
    assert out.returncode != 0
    data = json.loads(out.stdout)
    assert "error" in data

def test_dispatch_worker_cli_spawn_failure_emits_error_json(tmp_path):
    # Config/role are well-formed, but no "claude" binary exists on this PATH.
    # Task 7 follow-up: run_worker must raise DispatchError (not a raw
    # FileNotFoundError), and the CLI must turn that into structured JSON
    # instead of crashing with a traceback.
    _write_delivery_yml(tmp_path, "code", "claude", "opus")
    out = _run_dispatch_worker(tmp_path, "code", "hello\n", "/usr/bin:/bin")
    assert out.returncode != 0, out.stdout
    data = json.loads(out.stdout)
    assert "error" in data and "claude" in data["error"]

def test_dispatch_worker_cli_unknown_cli_emits_error_json(tmp_path):
    # Fix round 1 (minor): a role bound to a cli id that isn't a registered
    # adapter makes get_adapter() raise ConfigError. dispatch_worker.py's
    # try/except McdError must turn that into structured JSON too, not just
    # spawn failures -- this was claimed in the Task 10 report but untested.
    _write_delivery_yml(tmp_path, "code", "not-a-real-cli", "some-model")
    out = _run_dispatch_worker(tmp_path, "code", "hello\n", "/usr/bin:/bin")
    assert out.returncode != 0, out.stdout
    data = json.loads(out.stdout)
    assert "error" in data

def test_dispatch_worker_cli_wires_prompt_via_arg_for_claude(tmp_path):
    # Ruling B: claude's adapter takes the prompt file path as a trailing CLI arg.
    _write_delivery_yml(tmp_path, "code", "claude", "opus")
    _make_fake_bin(tmp_path / "bin", "claude", textwrap.dedent("""\
        import sys
        with open(sys.argv[-1], encoding="utf-8") as f:
            data = f.read()
        sys.stdout.write(f"argfile={data}")
        sys.exit(0)
        """))
    out = _run_dispatch_worker(tmp_path, "code", "hello-via-arg\n",
                               f"{tmp_path / 'bin'}:/usr/bin:/bin")
    assert out.returncode == 0, out.stderr
    data = json.loads(out.stdout)
    assert data["exit_code"] == 0 and data["tripped"] is None
    assert "hello-via-arg" in data["stdout"]

def test_dispatch_worker_cli_wires_prompt_via_stdin_for_codex(tmp_path):
    # Ruling B: codex reads its prompt from stdin, not argv -- dispatch_worker.py
    # must pass stdin_file=<prompt file> to run_worker for this adapter only.
    # (If this wiring regresses to always stdin_file=None, codex sees EOF and
    # this test fails -- it does not merely check the "arg" path works.)
    _write_delivery_yml(tmp_path, "code", "codex", "gpt-5.6-terra")
    _make_fake_bin(tmp_path / "bin", "codex", textwrap.dedent("""\
        import sys
        data = sys.stdin.read()
        sys.stdout.write(f"stdin={data}")
        sys.exit(0)
        """))
    out = _run_dispatch_worker(tmp_path, "code", "hello-via-stdin\n",
                               f"{tmp_path / 'bin'}:/usr/bin:/bin")
    assert out.returncode == 0, out.stderr
    data = json.loads(out.stdout)
    assert data["exit_code"] == 0 and data["tripped"] is None
    assert "hello-via-stdin" in data["stdout"]

# --- Task 16: dispatch_worker returns the parsed handoff + honors --cli/--model overrides ---

def test_dispatch_worker_parses_handoff(tmp_path):
    # The tested exit0+sentinel+last-match gate (mcd_core.handoff.parse_handoff)
    # must actually run at the CLI boundary, not just in test_handoff.py.
    _write_delivery_yml(tmp_path, "code", "claude", "opus")
    _make_fake_bin(tmp_path / "bin", "claude", textwrap.dedent("""\
        import sys
        sys.stdout.write("doing work\\nStatus: DONE\\nRole: code\\nModel: fake\\n"
                         "Changed paths: src/a.py\\nVerification: pytest -> pass\\n"
                         "Disposition: ACCEPT\\nEND OF HANDOFF\\n")
        sys.exit(0)
        """))
    out = _run_dispatch_worker(tmp_path, "code", "hello\n",
                               f"{tmp_path / 'bin'}:/usr/bin:/bin")
    assert out.returncode == 0, out.stderr
    data = json.loads(out.stdout)
    assert data["success"] is True
    assert data["handoff"]["status"] == "DONE"
    assert data["handoff"]["disposition"] == "ACCEPT"
    assert data["handoff"]["changed_paths"] == ["src/a.py"]

def test_dispatch_worker_flags_truncated_handoff(tmp_path):
    # No END OF HANDOFF sentinel -> parse_handoff raises HandoffError -> the
    # CLI must report success: false with the reason, not crash and not
    # silently claim success on truncated/untrusted worker output.
    _write_delivery_yml(tmp_path, "code", "claude", "opus")
    _make_fake_bin(tmp_path / "bin", "claude", textwrap.dedent("""\
        import sys
        sys.stdout.write("doing work\\nStatus: DONE\\nno sentinel here\\n")
        sys.exit(0)
        """))
    out = _run_dispatch_worker(tmp_path, "code", "hello\n",
                               f"{tmp_path / 'bin'}:/usr/bin:/bin")
    assert out.returncode == 0, out.stderr
    data = json.loads(out.stdout)
    assert data["success"] is False
    assert "handoff_error" in data

def test_dispatch_worker_cli_model_override(tmp_path):
    # role "code" is bound to a *nonexistent* adapter id in config -- without
    # the override applying before get_adapter(), this would fail with a
    # ConfigError ("unknown adapter/cli id"), like
    # test_dispatch_worker_cli_unknown_cli_emits_error_json. Passing
    # --cli claude --model OVERRIDE-MODEL must both dodge that error AND put
    # OVERRIDE-MODEL (not the config's "base-model") on the worker's argv --
    # proving the override supersedes the config binding for this dispatch.
    _write_delivery_yml(tmp_path, "code", "not-a-real-cli", "base-model")
    _make_fake_bin(tmp_path / "bin", "claude", textwrap.dedent("""\
        import sys
        model = sys.argv[sys.argv.index("--model") + 1]
        sys.stdout.write(f"Status: DONE\\nRole: code\\nModel: {model}\\n"
                         "Changed paths:\\nVerification: none\\n"
                         "Disposition: ACCEPT\\nEND OF HANDOFF\\n")
        sys.exit(0)
        """))
    out = _run_dispatch_worker(tmp_path, "code", "hello\n",
                               f"{tmp_path / 'bin'}:/usr/bin:/bin",
                               cli="claude", model="OVERRIDE-MODEL")
    assert out.returncode == 0, out.stdout + out.stderr
    data = json.loads(out.stdout)
    assert data["success"] is True
    assert data["handoff"]["model"] == "OVERRIDE-MODEL"

# --- Task 11: the protocol playbook (SKILL.md + references/handoff.md + references/adapters.md) ---

def test_skill_frontmatter_and_no_hardcoded_models():
    skill = PLUGIN_ROOT / "skills" / "multi-cli-delivery" / "SKILL.md"
    text = skill.read_text(encoding="utf-8")
    assert text.startswith("---")
    assert "name: multi-cli-delivery" in text
    assert "Triggers on" in text or "Triggers on…" in text
    # Golden Rule #1: the SKILL must not hardcode a project's model/plan choice.
    for banned in ("gpt-5.6-terra", "glm-5.2", "minimax-m3"):
        assert banned not in text, f"SKILL.md must not hardcode model {banned!r}"
    assert "END OF HANDOFF" in text

# --- Task 12: vendor the dely acceptance-table (references/acceptance.md) + attribution ---

def test_acceptance_vendored_with_killer_rules_and_credit():
    acc = PLUGIN_ROOT / "skills" / "multi-cli-delivery" / "references" / "acceptance.md"
    text = acc.read_text(encoding="utf-8").lower()
    assert "counterexample" in text and "instrument" in text
    assert "before and after" in text          # the killer rule survived verbatim
    assert "dely" in text                       # credit present in the file
    root = PLUGIN_ROOT.parent.parent
    assert "dely" in (root / "NOTICE").read_text(encoding="utf-8").lower()

# --- Task 14: command entrypoint (commands/delegate.md) ---

def test_delegate_command_frontmatter_and_distinction():
    cmd = PLUGIN_ROOT / "commands" / "delegate.md"
    text = cmd.read_text(encoding="utf-8")
    assert text.startswith("---") and "name: delegate" in text
    assert "multi-cli-delivery" in text
    assert "orchestrate" in text.lower()        # states the distinction
    assert "--code" in text and "--review" in text   # per-run override documented

# --- Task 15: README workflow section + version bump + validation gate ---

import json as _json

def test_version_bumped_and_delegate_documented():
    manifest = _json.loads((PLUGIN_ROOT / ".claude-plugin" / "plugin.json").read_text())
    assert manifest["version"] != "0.1.0", "bump aak-workflow version with this feature"
    readme = (PLUGIN_ROOT.parent.parent / "README.md").read_text(encoding="utf-8")
    assert "delegate" in readme and "multi-cli" in readme.lower()

# --- Task 17: preflight emits independence (REVIEW!=CODE) resolution ---

def _write_delivery_yml_code_review(repo: Path, code: tuple[str, str], review: tuple[str, str],
                                    review_must_differ_from_code: bool = True) -> None:
    (repo / ".aak").mkdir(exist_ok=True)
    (repo / ".aak" / "delivery.yml").write_text(textwrap.dedent(f"""
        roles:
          code: {{cli: {code[0]}, model: {code[1]}}}
          review: {{cli: {review[0]}, model: {review[1]}}}
        defaults:
          review_must_differ_from_code: {str(review_must_differ_from_code).lower()}
    """), encoding="utf-8")

def _run_preflight(repo: Path):
    script = PLUGIN_ROOT / "scripts" / "preflight_clis.py"
    return subprocess.run([sys.executable, str(script), str(repo)],
                          capture_output=True, text=True,
                          env={"PATH": "/usr/bin:/bin", "PYTHONPATH": str(PLUGIN_ROOT)})

def test_preflight_independence_differs(tmp_path):
    # Different providers (codex/openai vs claude/anthropic) -> independent review.
    _write_delivery_yml_code_review(tmp_path, ("codex", "gpt-5.6-terra"), ("claude", "opus"),
                                    review_must_differ_from_code=True)
    out = _run_preflight(tmp_path)
    assert out.returncode == 0, out.stderr
    data = json.loads(out.stdout)
    assert data["independence"]["differ"] is True
    assert "reduced_assurance" not in data["independence"]
    assert "requires_human_approval" not in data["independence"]

def test_preflight_independence_same_model_flagged(tmp_path):
    # "opus" and "anthropic/opus" are aliases that collapse to the same canonical
    # identity (mcd_core.identity) -- must NOT falsely satisfy REVIEW!=CODE.
    _write_delivery_yml_code_review(tmp_path, ("claude", "opus"), ("claude", "anthropic/opus"),
                                    review_must_differ_from_code=True)
    out = _run_preflight(tmp_path)
    assert out.returncode == 0, out.stderr
    data = json.loads(out.stdout)
    indep = data["independence"]
    assert indep["differ"] is False
    assert indep["reduced_assurance"] == "review_independence: same-model"
    assert indep["requires_human_approval"] is True

def test_preflight_independence_absent_without_review_role(tmp_path):
    # Only a "code" role configured -- no "review" role to resolve independence
    # against, so the block must be omitted entirely (not present-but-empty).
    (tmp_path / ".aak").mkdir()
    (tmp_path / ".aak" / "delivery.yml").write_text(textwrap.dedent("""
        roles:
          code: {cli: claude, model: opus}
    """), encoding="utf-8")
    out = _run_preflight(tmp_path)
    assert out.returncode == 0, out.stderr
    data = json.loads(out.stdout)
    assert "independence" not in data
