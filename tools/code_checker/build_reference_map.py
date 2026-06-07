"""Thin orchestrator: build the codebase reference map."""

from __future__ import annotations

import sys
from pathlib import Path

# Allow imports from tools/ when run as a script
_TOOLS_DIR = Path(__file__).resolve().parent.parent
_tools_str = str(_TOOLS_DIR)
if _tools_str not in sys.path:
    sys.path.insert(0, _tools_str)

from code_checker.scanner import discover_python_files, scan_file
from code_checker.analyzer import (
    AnalysisResult,
    compute_import_edges,
    compute_layer_overview,
    find_duplicate_symbols,
    find_hotspots,
    group_by_keyword,
)
from code_checker.renderer import render_compact_map

OUTPUT_PATH = Path(__file__).resolve().parents[2] / "docs" / "code_map" / "CODEBASE_REFERENCE_MAP.md"


def build_map(repo_root: Path | None = None) -> str:
    root = repo_root or Path(__file__).resolve().parents[2]
    py_files = discover_python_files(root)
    file_infos = [scan_file(p) for p in py_files]
    active_hotspots, legacy_hotspots = find_hotspots(file_infos, root)
    result = AnalysisResult(
        layer_overviews=compute_layer_overview(file_infos, root),
        keyword_hit_groups=group_by_keyword(file_infos, root),
        active_hotspots=active_hotspots,
        legacy_hotspots=legacy_hotspots,
        duplicates=find_duplicate_symbols(file_infos, root),
        import_edges=compute_import_edges(file_infos, root),
    )
    return render_compact_map(result, task_number="272")


def main() -> int:
    markdown = build_map()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(markdown, encoding="utf-8")
    print(f"Reference map written to {OUTPUT_PATH}")
    print(f"Total length: {len(markdown.splitlines())} lines")
    return 0


if __name__ == "__main__":
    sys.exit(main())
