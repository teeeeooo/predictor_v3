"""Tests for ``tools/check_code_structure.py``.

The guard is pure-Python (stdlib only). We import its helpers and
drive them against in-memory source snippets so the tests do not
depend on PyQt5, Tkinter, or the rest of the repository tree. One
CLI smoke runs the script against the live repo via ``subprocess``
to confirm the current tree passes.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from tools import check_code_structure as guard


REPO_ROOT = Path(__file__).resolve().parents[1]


# ---------------------------------------------------------------------------
# Banned-import boundary checks
# ---------------------------------------------------------------------------


def test_core_layer_rejects_ui_tk_import():
    findings = guard.check_banned_imports(
        "from ui_tk.profile_resolver import resolve_profile_id\n",
        "core/something.py",
        "core",
        guard.BANNED_IMPORTS["core"],
    )
    assert any("ui_tk" in f.message for f in findings)
    assert all(f.severity == "error" for f in findings)


def test_core_layer_rejects_pyqt5_import():
    findings = guard.check_banned_imports(
        "import PyQt5\n",
        "core/something.py",
        "core",
        guard.BANNED_IMPORTS["core"],
    )
    assert any("PyQt5" in f.message for f in findings)


def test_core_layer_rejects_tkinter_import():
    findings = guard.check_banned_imports(
        "import tkinter\n",
        "core/something.py",
        "core",
        guard.BANNED_IMPORTS["core"],
    )
    assert any("tkinter" in f.message for f in findings)


def test_core_layer_allows_pure_python_import():
    findings = guard.check_banned_imports(
        "from typing import Optional\nimport math\n",
        "core/something.py",
        "core",
        guard.BANNED_IMPORTS["core"],
    )
    assert findings == []


def test_ui_tk_layer_rejects_pyqt5_import():
    findings = guard.check_banned_imports(
        "from PyQt5.QtWidgets import QWidget\n",
        "ui_tk/something.py",
        "ui_tk",
        guard.BANNED_IMPORTS["ui_tk"],
    )
    assert any("PyQt5" in f.message for f in findings)


def test_ui_tk_layer_rejects_ui_import():
    findings = guard.check_banned_imports(
        "from ui.calc_window import CalculatorWindow\n",
        "ui_tk/something.py",
        "ui_tk",
        guard.BANNED_IMPORTS["ui_tk"],
    )
    assert any("'ui'" in f.message for f in findings)


def test_ui_tk_layer_allows_tkinter_and_core_dispatcher():
    findings = guard.check_banned_imports(
        "import tkinter as tk\nfrom core.calculator_dispatcher import "
        "create_calculator_for_profile\n",
        "ui_tk/something.py",
        "ui_tk",
        guard.BANNED_IMPORTS["ui_tk"],
    )
    assert findings == []


# ---------------------------------------------------------------------------
# App entrypoint thin guard
# ---------------------------------------------------------------------------


def test_app_entrypoint_rejects_class_definition():
    source = "class MyApp:\n    pass\n\ndef main():\n    pass\n"
    findings = guard.check_app_entrypoint_thin(source, "app_x.py")
    assert any("must not define classes" in f.message for f in findings)


def test_app_entrypoint_rejects_too_many_functions():
    source = "".join(
        f"def fn_{i}():\n    pass\n" for i in range(guard.APP_ENTRYPOINT_MAX_FUNCS + 2)
    )
    findings = guard.check_app_entrypoint_thin(source, "app_x.py")
    assert any("module-level functions" in f.message for f in findings)


def test_app_entrypoint_rejects_loc_overflow():
    source = "import os\n" * (guard.APP_ENTRYPOINT_MAX_LOC + 5) + "def main():\n    pass\n"
    findings = guard.check_app_entrypoint_thin(source, "app_x.py")
    assert any("LOC" in f.message for f in findings)


def test_app_entrypoint_accepts_thin_file():
    source = (
        "from ui_tk.calculator_app import main\n\n"
        "if __name__ == '__main__':\n    main()\n"
    )
    findings = guard.check_app_entrypoint_thin(source, "app_x.py")
    assert findings == []


# ---------------------------------------------------------------------------
# ui_tk lightweight shell anti-pattern
# ---------------------------------------------------------------------------


def test_ui_tk_anti_pattern_trips_on_multi_responsibility_file():
    """A file that defines shell + tab + section + resolver +
    result-panel responsibilities all in one place must fail."""
    source = (
        "REGION_BY_LABEL = {'Hong Kong': 'hong_kong'}\n"
        "\n"
        "class CalculatorTkApp:\n    pass\n\n"
        "class Iso16358Tab:\n    pass\n\n"
        "class IsoCspfSection:\n    pass\n\n"
        "class ResultPanel:\n    pass\n\n"
        "def resolve_profile_id(region, metric):\n    return ''\n"
    )
    findings = guard.check_ui_tk_shell_anti_pattern(source, "ui_tk/calculator_app.py")
    assert findings, "anti-pattern check should fire on multi-responsibility file"
    assert "mixes too many responsibilities" in findings[0].message


def test_ui_tk_anti_pattern_ignores_dedicated_module():
    """A single-responsibility module (e.g. only ``Iso16358Tab``) must
    not trip the anti-pattern even if it imports the resolver/etc."""
    source = (
        "from ui_tk.profile_resolver import resolve_profile_id, REGION_BY_LABEL\n"
        "from ui_tk.result_panel import ResultPanel\n"
        "from ui_tk.sections.iso_cspf_section import IsoCspfSection\n\n"
        "class Iso16358Tab:\n    pass\n"
    )
    findings = guard.check_ui_tk_shell_anti_pattern(source, "ui_tk/tabs/iso16358_tab.py")
    assert findings == []


def test_ui_tk_anti_pattern_ignores_non_ui_tk_path():
    source = (
        "class CalculatorTkApp:\n    pass\n\n"
        "class Iso16358Tab:\n    pass\n\n"
        "class IsoCspfSection:\n    pass\n"
    )
    findings = guard.check_ui_tk_shell_anti_pattern(source, "ui/other.py")
    assert findings == []


# ---------------------------------------------------------------------------
# Soft limit + allowlist
# ---------------------------------------------------------------------------


def test_soft_limit_warns_when_loc_exceeded(tmp_path):
    source = "x = 1\n" * (guard.LOC_SOFT_LIMIT + 5)
    findings = guard.check_soft_limits(
        source,
        "core/new_big_thing.py",
        loc_allowlist=set(),
        class_allowlist=set(),
    )
    assert any(
        f.severity == "warning" and "LOC soft limit" in f.message for f in findings
    )


def test_soft_limit_skipped_when_file_in_allowlist():
    source = "x = 1\n" * (guard.LOC_SOFT_LIMIT + 5)
    findings = guard.check_soft_limits(
        source,
        "core/_legacy/calculator_iso16358_legacy.py",
        loc_allowlist={"core/_legacy/calculator_iso16358_legacy.py"},
        class_allowlist=set(),
    )
    assert not any("LOC soft limit" in f.message for f in findings)


def test_soft_limit_warns_when_class_count_exceeded():
    source = "".join(
        f"class C{i}:\n    pass\n\n" for i in range(guard.CLASS_SOFT_LIMIT + 2)
    )
    findings = guard.check_soft_limits(
        source,
        "ui_tk/many_classes.py",
        loc_allowlist=set(),
        class_allowlist=set(),
    )
    assert any("top-level classes" in f.message for f in findings)


def test_class_soft_limit_skipped_when_in_allowlist():
    source = "".join(
        f"class C{i}:\n    pass\n\n" for i in range(guard.CLASS_SOFT_LIMIT + 2)
    )
    findings = guard.check_soft_limits(
        source,
        "ui/calc_window.py",
        loc_allowlist=set(),
        class_allowlist={"ui/calc_window.py"},
    )
    assert not any("top-level classes" in f.message for f in findings)


# ---------------------------------------------------------------------------
# Repo-wide pass
# ---------------------------------------------------------------------------


def test_current_repo_passes_guard():
    """The live repo tree must currently pass the guard. Soft-limit
    warnings are allowed; only ``error`` findings cause a failure
    here, matching the script's exit-code contract."""
    findings = guard.run_checks(REPO_ROOT)
    errors = [f for f in findings if f.severity == "error"]
    assert errors == [], "live repo has guard errors:\n" + "\n".join(
        f"  {f.path}: {f.message}" for f in errors
    )


def test_cli_smoke_passes_on_current_repo():
    result = subprocess.run(
        [sys.executable, "-B", "tools/check_code_structure.py"],
        cwd=str(REPO_ROOT),
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"guard exited {result.returncode}; stdout=\n{result.stdout}\n"
        f"stderr=\n{result.stderr}"
    )
    assert "code structure guard" in result.stdout
