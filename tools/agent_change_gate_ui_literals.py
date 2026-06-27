"""Staged-addition policy for UI sizing and style magic literals."""

from __future__ import annotations

import ast
from pathlib import PurePosixPath
import re
from typing import Sequence

from tools.agent_change_gate_git import GitIndex, StagedChange
from tools.agent_change_gate_models import ChangeGate, Finding

UI_SOURCE_ROOTS = ("apps/calculator/ui/", "ui/", "ui_tk/")
LAYOUT_TOKEN_OWNER = "apps/calculator/ui/layout_constants.py"
_COLOR_PATTERN = re.compile(r"#[0-9A-Fa-f]{6}\b")
_GEOMETRY_PATTERN = re.compile(r"^\d+x\d+(?:[+-]\d+[+-]\d+)?$")
_TABLE_SIZE_KEYWORDS = {"row_header_chars", "data_column_chars"}
_PHASE2_SIZE_KEYWORDS = {"width", "height", "padx", "pady"}
_NAMED_COLORS = {
    "black",
    "blue",
    "cyan",
    "gray",
    "green",
    "grey",
    "orange",
    "purple",
    "red",
    "white",
    "yellow",
}


def check_ui_magic_literals(
    index: GitIndex,
    changes: Sequence[StagedChange],
    gate: ChangeGate | None,
) -> list[Finding]:
    """Reject Phase 1 UI literals and warn on Phase 2 presentation candidates."""
    if gate is not None and gate.ui_literal_exemption == "approved-for-slice":
        return []
    findings: list[Finding] = []
    for change in changes:
        if change.status == "D" or not _is_checked_ui_source(change.path):
            continue
        source = index.index_text(change.path)
        added = index.added_line_numbers(change.path)
        try:
            tree = ast.parse(source)
        except SyntaxError:
            continue
        for severity, line, kind in _literal_findings(tree):
            if line in added:
                message = (
                    f"new UI {kind} literal must use a token owner or "
                    "ui_literal_exemption: approved-for-slice"
                    if severity == "error"
                    else f"new UI {kind} literal should use an existing token, "
                    "owner helper, or report-local no-reuse reason"
                )
                findings.append(Finding(severity, f"{change.path}:{line}", message))
    return findings


def _is_checked_ui_source(path: str) -> bool:
    if not path.endswith(".py") or not path.startswith(UI_SOURCE_ROOTS):
        return False
    if path == LAYOUT_TOKEN_OWNER:
        return False
    return "token" not in PurePosixPath(path).name.lower()


def _literal_findings(tree: ast.AST) -> list[tuple[str, int, str]]:
    found: set[tuple[str, int, str]] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.keyword) and node.arg in _TABLE_SIZE_KEYWORDS:
            if _is_number(node.value):
                found.add(("error", node.value.lineno, node.arg))
        elif isinstance(node, ast.keyword) and node.arg == "min_size":
            if _is_numeric_pair(node.value):
                found.add(("error", node.value.lineno, "window min_size"))
        elif isinstance(node, ast.keyword) and node.arg in _PHASE2_SIZE_KEYWORDS:
            if _is_number(node.value) and node.value not in {0, 1}:
                found.add(("warning", node.value.lineno, node.arg))
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            value = node.value
            targets = node.targets if isinstance(node, ast.Assign) else (node.target,)
            if any(_target_name(target) == "min_size" for target in targets):
                if _is_numeric_pair(value):
                    found.add(("error", value.lineno, "window min_size"))
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name == "min_size":
                for child in ast.walk(node):
                    if isinstance(child, ast.Return) and _is_numeric_pair(child.value):
                        found.add(("error", child.value.lineno, "window min_size"))
        elif isinstance(node, ast.Call) and _call_name(node.func) == "geometry":
            if node.args and _is_geometry_string(node.args[0]):
                found.add(("error", node.args[0].lineno, "window geometry"))
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            if _COLOR_PATTERN.search(node.value):
                found.add(("error", node.lineno, "color"))
            elif node.value.lower() in _NAMED_COLORS:
                found.add(("warning", node.lineno, "named color"))
    return sorted(found)


def _is_number(node: ast.AST) -> bool:
    return isinstance(node, ast.Constant) and isinstance(node.value, (int, float))


def _is_numeric_pair(node: ast.AST) -> bool:
    return (
        isinstance(node, ast.Tuple)
        and len(node.elts) == 2
        and all(_is_number(item) for item in node.elts)
    )


def _target_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return None


def _call_name(node: ast.AST) -> str | None:
    return _target_name(node)


def _is_geometry_string(node: ast.AST) -> bool:
    return (
        isinstance(node, ast.Constant)
        and isinstance(node.value, str)
        and _GEOMETRY_PATTERN.fullmatch(node.value) is not None
    )
