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


def test_core_layer_rejects_apps_calculator_ui_import():
    findings = guard.check_banned_imports(
        "from apps.calculator.ui.profile_resolver import resolve_profile_id\n",
        "core/something.py",
        "core",
        guard.BANNED_IMPORTS["core"],
    )
    assert any("apps.calculator.ui" in f.message for f in findings)
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


def test_apps_calculator_ui_layer_rejects_pyqt5_import():
    findings = guard.check_banned_imports(
        "from PyQt5.QtWidgets import QWidget\n",
        "apps/calculator/ui/something.py",
        "apps.calculator.ui",
        guard.BANNED_IMPORTS["apps.calculator.ui"],
    )
    assert any("PyQt5" in f.message for f in findings)


def test_apps_calculator_ui_layer_rejects_ui_import():
    findings = guard.check_banned_imports(
        "from ui.calc_window import CalculatorWindow\n",
        "apps/calculator/ui/something.py",
        "apps.calculator.ui",
        guard.BANNED_IMPORTS["apps.calculator.ui"],
    )
    assert any("'ui'" in f.message for f in findings)


def test_apps_calculator_ui_layer_allows_tkinter_and_core_dispatcher():
    findings = guard.check_banned_imports(
        "import tkinter as tk\nfrom core.calculator_dispatcher import "
        "create_calculator_for_profile\n",
        "apps/calculator/ui/something.py",
        "apps.calculator.ui",
        guard.BANNED_IMPORTS["apps.calculator.ui"],
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
        "from apps.calculator.ui.calculator_app import main\n\n"
        "if __name__ == '__main__':\n    main()\n"
    )
    findings = guard.check_app_entrypoint_thin(source, "app_x.py")
    assert findings == []


# ---------------------------------------------------------------------------
# apps.calculator.ui lightweight shell anti-pattern
# ---------------------------------------------------------------------------


def test_apps_calculator_ui_anti_pattern_trips_on_multi_responsibility_file():
    """A file that defines shell + tab + section + resolver +
    result-panel responsibilities all in one place must fail."""
    source = (
        "REGION_BY_LABEL = {'Hong Kong': 'hong_kong'}\n"
        "\n"
        "class CalculatorTkApp:\n    pass\n\n"
        "class Iso16358Tab:\n    pass\n\n"
        "class HongKongCspfSection:\n    pass\n\n"
        "class ResultPanel:\n    pass\n\n"
        "def resolve_profile_id(region, metric):\n    return ''\n"
    )
    findings = guard.check_apps_calculator_ui_shell_anti_pattern(source, "apps/calculator/ui/calculator_app.py")
    assert findings, "anti-pattern check should fire on multi-responsibility file"
    assert "mixes too many responsibilities" in findings[0].message


def test_apps_calculator_ui_anti_pattern_ignores_dedicated_module():
    """A single-responsibility module (e.g. only ``Iso16358Tab``) must
    not trip the anti-pattern even if it imports the resolver/etc."""
    source = (
        "from apps.calculator.ui.profile_resolver import resolve_profile_id, REGION_BY_LABEL\n"
        "from apps.calculator.ui.result_panel import ResultPanel\n"
        "from apps.calculator.ui.sections.hong_kong_cspf_section import HongKongCspfSection\n\n"
        "class Iso16358Tab:\n    pass\n"
    )
    findings = guard.check_apps_calculator_ui_shell_anti_pattern(source, "apps/calculator/ui/tabs/iso16358_tab.py")
    assert findings == []


def test_apps_calculator_ui_anti_pattern_ignores_non_apps_calculator_ui_path():
    source = (
        "class CalculatorTkApp:\n    pass\n\n"
        "class Iso16358Tab:\n    pass\n\n"
        "class HongKongCspfSection:\n    pass\n"
    )
    findings = guard.check_apps_calculator_ui_shell_anti_pattern(source, "ui/other.py")
    assert findings == []


# ---------------------------------------------------------------------------
# UI visual-value ownership boundary
# ---------------------------------------------------------------------------


def _visual_findings(source: str, relpath: str):
    return guard.check_ui_visual_value_ownership(
        source,
        relpath,
        scan_roots=guard.UI_VISUAL_SCAN_ROOTS,
        owner_paths=guard.UI_VISUAL_OWNER_PATHS,
        allowlist_paths=guard.UI_VISUAL_ALLOWLIST_PATHS,
    )


def test_ui_visual_owner_rejects_raw_hex_in_component():
    findings = _visual_findings(
        'def render_background():\n    return "#e8edf2"\n',
        "apps/calculator/ui/result_panel.py",
    )
    assert any("raw hex color literal" in finding.message for finding in findings)


def test_ui_visual_owner_rejects_local_visual_constant_in_component():
    findings = _visual_findings(
        "RESULT_HEADER_BG = theme_value('result.header')\n",
        "apps/calculator/ui/result_panel.py",
    )
    assert any("local visual constant" in finding.message for finding in findings)


def test_ui_visual_owner_allows_tokens_in_owner_file():
    findings = _visual_findings(
        'RESULT_HEADER_BG = "#e8edf2"\nTABLE_CELL_PADX = 8\n',
        "apps/calculator/ui/layout_constants.py",
    )
    assert findings == []


def test_ui_visual_owner_does_not_scan_core_calculation_constants():
    findings = _visual_findings(
        'HEATING_COLOR = "#e8edf2"\nCAPACITY_WIDTH = 100\n',
        "core/calculator_iso16358.py",
    )
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
        "apps/calculator/ui/many_classes.py",
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
# Source File Owner Boundary Policy checks
# ---------------------------------------------------------------------------


def test_check_ui_root_flat_feature_file():
    # Bad examples
    assert any(
        f.severity == "error" and "Feature-specific flat file" in f.message
        for f in guard.check_ui_root_flat_feature_file("apps/calculator/ui/en14825_seer_adapter.py")
    )
    assert any(
        f.severity == "error" and "Feature-specific flat file" in f.message
        for f in guard.check_ui_root_flat_feature_file("apps/calculator/ui/saso_t3.py")
    )
    # Good examples
    assert guard.check_ui_root_flat_feature_file("apps/calculator/ui/en14825/seer_adapter.py") == []
    assert guard.check_ui_root_flat_feature_file("apps/calculator/ui/result_panel.py") == []


def test_check_sections_flat_model_adapter_table():
    # Bad examples
    assert any(
        f.severity == "error" and "UI glue/routing only" in f.message
        for f in guard.check_sections_flat_model_adapter_table("apps/calculator/ui/sections/en14825_seer_table_model.py")
    )
    assert any(
        f.severity == "error" and "UI glue/routing only" in f.message
        for f in guard.check_sections_flat_model_adapter_table("apps/calculator/ui/sections/saso_adapter.py")
    )
    # Good examples
    assert guard.check_sections_flat_model_adapter_table("apps/calculator/ui/en14825/seer_table_model.py") == []
    assert guard.check_sections_flat_model_adapter_table("apps/calculator/ui/sections/en14825_section.py") == []
    assert guard.check_sections_flat_model_adapter_table("apps/calculator/ui/sections/iso_saso_t3_section.py") == []


def test_check_core_root_flat_helper_misc_utils():
    # Bad examples
    assert any(
        f.severity == "warning" and "Avoid adding new flat helper/misc/utils files" in f.message
        for f in guard.check_core_root_flat_helper_misc_utils("core/new_standard_utils.py")
    )
    assert any(
        f.severity == "warning" and "Avoid adding new flat helper/misc/utils files" in f.message
        for f in guard.check_core_root_flat_helper_misc_utils("core/foo_helper.py")
    )
    # Good examples
    assert guard.check_core_root_flat_helper_misc_utils("core/calculator_en14825.py") == []
    assert guard.check_core_root_flat_helper_misc_utils("core/utils.py") == []  # Not ending in _utils.py


def test_check_tests_mega_test_naming():
    # Bad examples
    assert any(
        f.severity == "warning" and "Avoid using generic mega-test names" in f.message
        for f in guard.check_tests_mega_test_naming("tests/test_newstandard_everything.py")
    )
    assert any(
        f.severity == "warning" and "Avoid using generic mega-test names" in f.message
        for f in guard.check_tests_mega_test_naming("tests/test_foo_all.py")
    )
    # Good examples
    assert guard.check_tests_mega_test_naming("tests/test_apps_calculator_ui_en14825.py") == []
    assert guard.check_tests_mega_test_naming("tests/test_ui_theme_tokens.py") == []


def test_check_ui_package_registry():
    # Bad examples (new unregistered directory)
    assert any(
        f.severity == "warning" and "not in the allowed package registry" in f.message
        for f in guard.check_ui_package_registry("apps/calculator/ui/new_unregistered_package/foo.py")
    )
    # Good examples (registered package)
    assert guard.check_ui_package_registry("apps/calculator/ui/en14825/seer_adapter.py") == []
    assert guard.check_ui_package_registry("apps/calculator/ui/batch/models.py") == []
    # Flat file (registry check is only for packages under ui/, meaning depth >= 5)
    assert guard.check_ui_package_registry("apps/calculator/ui/result_panel.py") == []


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
