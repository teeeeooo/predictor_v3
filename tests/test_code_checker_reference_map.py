"""Focused tests for code_checker reference map calibration (272).

Uses synthetic FileInfo objects and small temp files to avoid brittle
full-repo fixtures.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

# Allow importing code_checker from tools/
REPO_ROOT = Path(__file__).resolve().parents[1]
_TOOLS_DIR = str(REPO_ROOT / "tools")
if _TOOLS_DIR not in sys.path:
    sys.path.insert(0, _TOOLS_DIR)

from code_checker.scanner import Symbol, FileInfo, scan_file
from code_checker.analyzer import (
    find_duplicate_symbols,
    find_hotspots,
    group_by_keyword,
    compute_import_edges,
)
from code_checker.renderer import render_compact_map, AnalysisResult


# ---------------------------------------------------------------------------
# Task 2: scanner distinguishes top-level functions from methods
# ---------------------------------------------------------------------------

def test_scanner_symbol_kinds() -> None:
    code = """
class Foo:
    def method_a(self):
        def nested_b():
            pass

def top_level_c():
    pass

TOP = 1
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code)
        f.flush()
        info = scan_file(Path(f.name))

    assert len(info.classes) == 1
    assert info.classes[0].kind == "class"
    assert info.classes[0].name == "Foo"

    assert len(info.top_level_functions) == 1
    assert info.top_level_functions[0].kind == "top_level_function"
    assert info.top_level_functions[0].name == "top_level_c"

    assert len(info.methods) == 1
    assert info.methods[0].kind == "method"
    assert info.methods[0].name == "method_a"

    assert len(info.nested_functions) == 1
    assert info.nested_functions[0].kind == "nested_function"
    assert info.nested_functions[0].name == "nested_b"

    assert len(info.constants) == 1
    assert info.constants[0].kind == "constant"
    assert info.constants[0].name == "TOP"


# ---------------------------------------------------------------------------
# Task 3: duplicate candidates exclude class methods / framework noise
# ---------------------------------------------------------------------------

def test_duplicate_excludes_methods_and_framework_noise() -> None:
    root = Path("/tmp")
    fi1 = FileInfo(
        path=Path("/tmp/a.py"),
        loc=10,
        classes=[],
        top_level_functions=[Symbol("grid", 1, 2, "top_level_function")],
        methods=[Symbol("grid", 3, 4, "method")],
        constants=[],
    )
    fi2 = FileInfo(
        path=Path("/tmp/b.py"),
        loc=10,
        classes=[],
        top_level_functions=[Symbol("grid", 1, 2, "top_level_function")],
        methods=[Symbol("grid", 3, 4, "method")],
        constants=[],
    )
    dups = find_duplicate_symbols([fi1, fi2], root)
    # "grid" is in _FRAMEWORK_METHOD_NOISE, so it should be excluded even as top-level.
    names = {d.name for d in dups}
    assert "grid" not in names


def test_duplicate_includes_repeated_top_level_helpers() -> None:
    root = Path("/tmp")
    fi1 = FileInfo(
        path=Path("/tmp/a.py"),
        loc=10,
        classes=[],
        top_level_functions=[Symbol("normalize_input", 1, 2, "top_level_function")],
        methods=[],
        constants=[],
    )
    fi2 = FileInfo(
        path=Path("/tmp/b.py"),
        loc=10,
        classes=[],
        top_level_functions=[Symbol("normalize_input", 1, 2, "top_level_function")],
        methods=[],
        constants=[],
    )
    dups = find_duplicate_symbols([fi1, fi2], root)
    names = {d.name for d in dups}
    assert "normalize_input" in names


# ---------------------------------------------------------------------------
# Task 4: hotspots split active vs legacy/deferred
# ---------------------------------------------------------------------------

def test_hotspot_active_vs_legacy_split() -> None:
    root = Path("/repo")
    active_fi = FileInfo(
        path=Path("/repo/ui_tk/big_file.py"),
        loc=500,
        classes=[Symbol("A", 1, 2, "class")],
        top_level_functions=[],
        methods=[],
        constants=[],
    )
    legacy_fi = FileInfo(
        path=Path("/repo/core/_legacy/old.py"),
        loc=500,
        classes=[Symbol("B", 1, 2, "class")],
        top_level_functions=[],
        methods=[],
        constants=[],
    )
    deferred_fi = FileInfo(
        path=Path("/repo/ui/qt_old.py"),
        loc=500,
        classes=[Symbol("C", 1, 2, "class")],
        top_level_functions=[],
        methods=[],
        constants=[],
    )
    active, legacy = find_hotspots([active_fi, legacy_fi, deferred_fi], root)
    assert len(active) == 1
    assert active[0].path == "ui_tk/big_file.py"
    assert active[0].category == "active"
    assert len(legacy) == 2
    legacy_paths = {h.path for h in legacy}
    assert "core/_legacy/old.py" in legacy_paths
    assert "ui/qt_old.py" in legacy_paths


# ---------------------------------------------------------------------------
# Task 5: keyword hit group evidence label
# ---------------------------------------------------------------------------

def test_keyword_hit_group_not_ownership() -> None:
    root = Path("/tmp")
    fi = FileInfo(
        path=Path("/tmp/ui_tk/table_widget.py"),
        loc=10,
        classes=[Symbol("TableWidget", 1, 2, "class")],
        top_level_functions=[],
        methods=[],
        constants=[],
    )
    groups = group_by_keyword([fi], root)
    keywords = {g.keyword for g in groups}
    # "table" should match because class name contains "Table"
    assert "table" in keywords
    # "calculator" should NOT match just because the file exists
    assert "calculator" not in keywords


# ---------------------------------------------------------------------------
# Task 6: import edge granularity beyond top-level
# ---------------------------------------------------------------------------

def test_import_edge_shows_module_prefix() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        # Simulate a repo with a core/ package
        (root / "core").mkdir(parents=True, exist_ok=True)
        fi = FileInfo(
            path=root / "app.py",
            loc=10,
            classes=[],
            top_level_functions=[],
            methods=[],
            constants=[],
            imports=["core.calculator_profiles.resolve_calculator_profile"],
        )
        edges = compute_import_edges([fi], root)
        assert any(
            e.source == "app.py" and e.target == "core.calculator_profiles.resolve_calculator_profile"
            for e in edges
        )


# ---------------------------------------------------------------------------
# Task 7: renderer output includes both hotspot sections
# ---------------------------------------------------------------------------

def test_renderer_has_active_and_legacy_hotspot_sections() -> None:
    result = AnalysisResult(
        layer_overviews=[],
        keyword_hit_groups=[],
        active_hotspots=[],
        legacy_hotspots=[],
        duplicates=[],
        import_edges=[],
    )
    md = render_compact_map(result, task_number="272")
    assert "## Active Hotspots" in md
    assert "## Legacy / Deferred Hotspots" in md


def test_renderer_has_duplicate_framework_filter_note() -> None:
    result = AnalysisResult(
        layer_overviews=[],
        keyword_hit_groups=[],
        active_hotspots=[],
        legacy_hotspots=[],
        duplicates=[],
        import_edges=[],
    )
    md = render_compact_map(result, task_number="272")
    assert "Framework methods" in md
    assert "filtered out" in md


def test_renderer_long_function_not_self_hotspot() -> None:
    # render_compact_map itself was a long function in 271.
    # After split into helpers, renderer.py should not show up as a hotspot.
    root = Path(__file__).resolve().parents[1]
    renderer_path = root / "tools" / "code_checker" / "renderer.py"
    info = scan_file(renderer_path)
    active, legacy = find_hotspots([info], root)
    assert len(active) == 0
    assert len(legacy) == 0
