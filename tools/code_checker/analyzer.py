"""Analysis layer: hotspots, duplicates, keyword hits, import edges."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Set

from .scanner import FileInfo, Symbol

OWNER_KEYWORDS: Dict[str, List[str]] = {
    "table": ["table", "spreadsheet", "clipboard"],
    "window": ["window", "dialog", "viewport", "geometry", "fit", "resize", "content"],
    "calculator": [
        "calculator",
        "calc",
        "hspf",
        "iseer",
        "cop",
        "eerp",
        "plf",
        "ahri",
        "saso",
    ],
    "detail": ["detail", "bin", "graph", "trace", "chart"],
    "export": ["export", "clipboard", "csv", "tsv", "copy", "save"],
    "batch": ["batch", "matrix", "bulk"],
    "predictor": ["predictor", "model", "train", "ml", "regression", "optuna"],
    "controller": ["controller", "adapter", "resolver", "dispatcher", "orchestrator"],
    "config": ["config", "constant", "token", "registry", "setting"],
}

LOC_SOFT_LIMIT = 250
LOC_NEAR_HARD = 350
CLASS_SOFT_LIMIT = 3
FUNCTION_SOFT_LIMIT = 60

_IGNORED_DUPLICATE_NAMES: Set[str] = {
    "__init__",
    "main",
    "run",
    "setup",
    "load",
    "save",
    "get",
    "set",
    "parse",
    "render",
    "format",
    "validate",
    "convert",
    "calculate",
    "compute",
    "update",
    "reset",
    "init",
    "start",
    "stop",
    "process",
    "handle",
    "create",
    "build",
    "generate",
    "write",
    "read",
    "open",
    "close",
    "delete",
    "remove",
    "add",
    "insert",
    "append",
    "clear",
    "copy",
    "sort",
    "filter",
    "find",
    "index",
    "count",
    "join",
    "split",
    "strip",
    "replace",
    "configure",
}

_FRAMEWORK_METHOD_NOISE: Set[str] = {
    "grid",
    "pack",
    "place",
    "rowCount",
    "columnCount",
    "row_count",
    "column_count",
    "data",
    "headerData",
    "setData",
    "set_data",
    "flags",
    "keyPressEvent",
    "paintEvent",
    "mousePressEvent",
    "mouseMoveEvent",
    "mouseReleaseEvent",
    "wheelEvent",
    "focusInEvent",
    "focusOutEvent",
    "showEvent",
    "hideEvent",
    "resizeEvent",
    "moveEvent",
    "closeEvent",
    "contextMenuEvent",
    "dragEnterEvent",
    "dragMoveEvent",
    "dropEvent",
    "enterEvent",
    "leaveEvent",
    "timerEvent",
    "changeEvent",
    "event",
    "eventFilter",
}


@dataclass
class DuplicateGroup:
    name: str
    locations: List[tuple[str, int]]  # (relative_path, line)


@dataclass
class HotspotFile:
    path: str
    loc: int
    class_count: int
    long_functions: List[tuple[str, int]]  # (name, approx_loc)
    category: str = "active"


@dataclass
class KeywordHitGroup:
    keyword: str
    files: List[str]


@dataclass
class LayerOverview:
    name: str
    file_count: int
    total_loc: int


@dataclass
class ImportEdge:
    source: str
    target: str


@dataclass
class AnalysisResult:
    layer_overviews: List[LayerOverview]
    keyword_hit_groups: List[KeywordHitGroup]
    active_hotspots: List[HotspotFile]
    legacy_hotspots: List[HotspotFile]
    duplicates: List[DuplicateGroup]
    import_edges: List[ImportEdge]


def _rel(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def _hotspot_category(rel_path: str) -> str:
    if rel_path.startswith("core/_legacy/"):
        return "legacy"
    if rel_path.startswith("ui/"):
        return "legacy"
    if rel_path.startswith("scripts/"):
        return "deferred"
    return "active"


def compute_layer_overview(file_infos: List[FileInfo], root: Path) -> List[LayerOverview]:
    layers: Dict[str, List[FileInfo]] = defaultdict(list)
    for fi in file_infos:
        rel = Path(_rel(fi.path, root))
        top = rel.parts[0] if rel.parts else "root"
        layers[top].append(fi)
    overviews: List[LayerOverview] = []
    for name in sorted(layers):
        files = layers[name]
        overviews.append(
            LayerOverview(
                name=name,
                file_count=len(files),
                total_loc=sum(f.loc for f in files),
            )
        )
    return overviews


def group_by_keyword(file_infos: List[FileInfo], root: Path) -> List[KeywordHitGroup]:
    keyword_to_files: Dict[str, Set[str]] = defaultdict(set)
    for fi in file_infos:
        rel = _rel(fi.path, root).lower()
        all_names = {s.name.lower() for s in fi.classes + fi.top_level_functions + fi.constants}
        for keyword, substrings in OWNER_KEYWORDS.items():
            for sub in substrings:
                if sub in rel or any(sub in n for n in all_names):
                    keyword_to_files[keyword].add(_rel(fi.path, root))
                    break
    groups: List[KeywordHitGroup] = []
    for keyword in sorted(keyword_to_files):
        groups.append(
            KeywordHitGroup(
                keyword=keyword,
                files=sorted(keyword_to_files[keyword]),
            )
        )
    return groups


def find_hotspots(file_infos: List[FileInfo], root: Path) -> tuple[List[HotspotFile], List[HotspotFile]]:
    active: List[HotspotFile] = []
    legacy: List[HotspotFile] = []
    for fi in file_infos:
        rel = _rel(fi.path, root)
        class_count = len(fi.classes)
        long_functions = []
        for sym in fi.functions:
            func_loc = sym.end_line - sym.line + 1
            if func_loc > FUNCTION_SOFT_LIMIT:
                long_functions.append((sym.name, func_loc))
        is_hot = (
            fi.loc > LOC_SOFT_LIMIT
            or class_count > CLASS_SOFT_LIMIT
            or long_functions
            or fi.loc >= LOC_NEAR_HARD
        )
        if is_hot:
            hotspot = HotspotFile(
                path=rel,
                loc=fi.loc,
                class_count=class_count,
                long_functions=long_functions,
                category=_hotspot_category(rel),
            )
            if hotspot.category == "active":
                active.append(hotspot)
            else:
                legacy.append(hotspot)
    active = sorted(active, key=lambda h: h.loc, reverse=True)
    legacy = sorted(legacy, key=lambda h: h.loc, reverse=True)
    return active, legacy


def find_duplicate_symbols(file_infos: List[FileInfo], root: Path) -> List[DuplicateGroup]:
    symbol_map: Dict[str, List[tuple[str, int]]] = defaultdict(list)
    for fi in file_infos:
        rel = _rel(fi.path, root)
        # Only top-level functions, classes, and constants are eligible for extraction candidates.
        for sym in fi.classes + fi.top_level_functions + fi.constants:
            symbol_map[sym.name].append((rel, sym.line))
    duplicates: List[DuplicateGroup] = []
    for name, locs in symbol_map.items():
        if name in _IGNORED_DUPLICATE_NAMES:
            continue
        if name in _FRAMEWORK_METHOD_NOISE:
            continue
        if len(locs) > 1:
            duplicates.append(DuplicateGroup(name=name, locations=sorted(locs)))
    return sorted(duplicates, key=lambda d: len(d.locations), reverse=True)


def _internal_top_levels(root: Path) -> Set[str]:
    """Return top-level directory/package names inside the repo."""
    tops: Set[str] = set()
    for p in root.iterdir():
        if p.is_dir() and not p.name.startswith("."):
            tops.add(p.name)
        elif p.suffix == ".py":
            tops.add(p.stem)
    return tops


def compute_import_edges(file_infos: List[FileInfo], root: Path) -> List[ImportEdge]:
    internal = _internal_top_levels(root)
    edges: Set[tuple[str, str]] = set()
    for fi in file_infos:
        rel = _rel(fi.path, root)
        for imp in fi.imports:
            parts = imp.split(".")
            top = parts[0]
            if top in internal:
                # Show up to 3 parts of the imported module for better granularity.
                target = ".".join(parts[:3])
                edges.add((rel, target))
    return [ImportEdge(source=s, target=t) for s, t in sorted(edges)]
