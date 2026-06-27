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
        path=Path("/repo/apps/calculator/ui/big_file.py"),
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
    assert active[0].path == "apps/calculator/ui/big_file.py"
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
        path=Path("/tmp/apps/calculator/ui/table_widget.py"),
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
    # The reference map is a search-cue index, so path keywords also match.
    assert "calculator" in keywords


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
            imports=["core.calculators.profiles.resolve_calculator_profile"],
        )
        edges = compute_import_edges([fi], root)
        assert any(
            e.source == "app.py" and e.target == "core.calculators.profiles.resolve_calculator_profile"
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
    md = render_compact_map(result)
    assert "## Active Hotspots" in md
    assert "## Legacy / Deferred Hotspots" in md
    assert "task" not in md.split("\n")[2] # Verify no task number text in header


def test_renderer_has_duplicate_framework_filter_note() -> None:
    result = AnalysisResult(
        layer_overviews=[],
        keyword_hit_groups=[],
        active_hotspots=[],
        legacy_hotspots=[],
        duplicates=[],
        import_edges=[],
    )
    md = render_compact_map(result)
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


# ---------------------------------------------------------------------------
# Task 8: code_checker metadata and freshness check tests (310)
# ---------------------------------------------------------------------------

from code_checker.metadata import (
    get_git_info,
    generate_metadata,
    render_metadata_comment,
    parse_metadata_from_map,
    evaluate_freshness,
)

def test_metadata_generation_and_rendering() -> None:
    # 1. generate_metadata works safely even in a temp directory (fallback)
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        meta = generate_metadata(tmp_path)
        assert meta["generator"] == "code_checker"
        assert meta["schema_version"] == "1.0.0"
        assert "generated_at_utc" in meta
        # Since it's a new empty dir, commit might fallback to "unknown"
        assert "git_commit_short" in meta
        assert "git_dirty" in meta

    # 2. renderer incorporates metadata as HTML comment at the top
    result = AnalysisResult(
        layer_overviews=[],
        keyword_hit_groups=[],
        active_hotspots=[],
        legacy_hotspots=[],
        duplicates=[],
        import_edges=[],
    )
    fake_meta = {
        "generator": "code_checker",
        "schema_version": "1.0.0",
        "generated_at_utc": "2026-06-10 00:00 UTC",
        "git_commit_short": "abc1234",
        "git_dirty": False,
    }
    md = render_compact_map(result, metadata=fake_meta)
    expected_comment = render_metadata_comment(fake_meta)
    assert md.startswith(expected_comment)
    assert "abc1234" in md


def test_metadata_parsing_and_freshness_evaluation() -> None:
    # 1. parsing comment back to dict
    fake_meta = {
        "generator": "code_checker",
        "schema_version": "1.0.0",
        "generated_at_utc": "2026-06-10 00:00 UTC",
        "git_commit_short": "abc1234",
        "git_dirty": False,
    }
    comment = render_metadata_comment(fake_meta)
    parsed = parse_metadata_from_map(comment)
    assert parsed == fake_meta

    # 2. Evaluate freshness in different scenarios
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        map_file = tmp_path / "CODEBASE_REFERENCE_MAP.md"

        # Scenario A: Map file does not exist
        res_missing = evaluate_freshness(map_file, tmp_path)
        assert res_missing["status"] == "missing"

        # Scenario B: Map file exists but lacks metadata comment
        map_file.write_text("# Reference Map Without Metadata", encoding="utf-8")
        res_no_meta = evaluate_freshness(map_file, tmp_path)
        assert res_no_meta["status"] == "metadata_missing"

        # Scenario C: Map has metadata, evaluate freshness based on commit match
        # Since git_commit_short of tmpdir will likely be "unknown"
        # We write a map matching the current commit
        current_git = get_git_info(tmp_path)
        current_commit = current_git["commit"]

        matching_meta = {
            "generator": "code_checker",
            "schema_version": "1.0.0",
            "generated_at_utc": "2026-06-10 00:00 UTC",
            "git_commit_short": current_commit,
            "git_dirty": False,
        }
        comment_match = render_metadata_comment(matching_meta)
        map_file.write_text(f"{comment_match}\n# Map content", encoding="utf-8")

        res_fresh = evaluate_freshness(map_file, tmp_path)
        if current_commit == "unknown":
            assert res_fresh["status"] == "unknown"
        else:
            assert res_fresh["status"] == "fresh"

        # Scenario D: Stale commit
        stale_meta = {
            "generator": "code_checker",
            "schema_version": "1.0.0",
            "generated_at_utc": "2026-06-10 00:00 UTC",
            "git_commit_short": "stale123",
            "git_dirty": False,
        }
        comment_stale = render_metadata_comment(stale_meta)
        map_file.write_text(f"{comment_stale}\n# Map content", encoding="utf-8")

        res_stale = evaluate_freshness(map_file, tmp_path)
        if current_commit == "unknown":
            assert res_stale["status"] == "unknown"
        else:
            assert res_stale["status"] == "stale"
