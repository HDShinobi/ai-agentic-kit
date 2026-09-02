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

def _run_dispatch_worker(repo: Path, role: str, prompt_text: str, path_env: str):
    prompt = repo / "prompt.txt"
    prompt.write_text(prompt_text, encoding="utf-8")
    script = PLUGIN_ROOT / "scripts" / "dispatch_worker.py"
    return subprocess.run(
        [sys.executable, str(script), "--role", role, "--repo", str(repo),
         "--prompt-file", str(prompt), "--cwd", str(repo)],
        capture_output=True, text=True, timeout=30,
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
