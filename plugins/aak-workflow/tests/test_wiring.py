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
