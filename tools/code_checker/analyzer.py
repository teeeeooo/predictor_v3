"""Analysis layer: hotspots, duplicates, owner groups, import edges."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Set

from .scanner import FileInfo, Symbol

OWNER_KEYWORDS: Dict[str, List[str]] = {
    "table": ["table", "cell", "row", "column", "spreadsheet", "clipboard"],
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


@dataclass
class OwnerGroup:
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
    owner_groups: List[OwnerGroup]
    hotspots: List[HotspotFile]
    duplicates: List[DuplicateGroup]
    import_edges: List[ImportEdge]


def _rel(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


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


def group_by_owner(file_infos: List[FileInfo], root: Path) -> List[OwnerGroup]:
    keyword_to_files: Dict[str, Set[str]] = defaultdict(set)
    for fi in file_infos:
        rel = _rel(fi.path, root).lower()
        all_names = {s.name.lower() for s in fi.classes + fi.functions + fi.constants}
        for keyword, substrings in OWNER_KEYWORDS.items():
            for sub in substrings:
                if sub in rel or any(sub in n for n in all_names):
                    keyword_to_files[keyword].add(_rel(fi.path, root))
                    break
    groups: List[OwnerGroup] = []
    for keyword in sorted(keyword_to_files):
        groups.append(
            OwnerGroup(
                keyword=keyword,
                files=sorted(keyword_to_files[keyword]),
            )
        )
    return groups


def find_hotspots(file_infos: List[FileInfo], root: Path) -> List[HotspotFile]:
    hotspots: List[HotspotFile] = []
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
            hotspots.append(
                HotspotFile(
                    path=rel,
                    loc=fi.loc,
                    class_count=class_count,
                    long_functions=long_functions,
                )
            )
    return sorted(hotspots, key=lambda h: h.loc, reverse=True)


def find_duplicate_symbols(file_infos: List[FileInfo], root: Path) -> List[DuplicateGroup]:
    symbol_map: Dict[str, List[tuple[str, int]]] = defaultdict(list)
    for fi in file_infos:
        rel = _rel(fi.path, root)
        for sym in fi.classes + fi.functions + fi.constants:
            symbol_map[sym.name].append((rel, sym.line))
    duplicates: List[DuplicateGroup] = []
    for name, locs in symbol_map.items():
        if name in _IGNORED_DUPLICATE_NAMES:
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
            top = imp.split(".")[0]
            if top in internal:
                edges.add((rel, top))
    return [ImportEdge(source=s, target=t) for s, t in sorted(edges)]
