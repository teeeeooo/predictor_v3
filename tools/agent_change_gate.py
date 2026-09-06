"""Policy evaluation for staged agent changes."""

from __future__ import annotations

import ast
from typing import Sequence

from tools.agent_change_gate_git import GitIndex, StagedChange
from tools.agent_change_gate_ui_literals import check_ui_magic_literals
from tools.agent_change_gate_models import Finding, TaskManifest, parse_manifest

PRODUCTION_ROOTS = ("core/", "ui/", "apps/", "scripts/")


def evaluate_cached(index: GitIndex) -> list[Finding]:
    changes = index.staged_changes()
    findings: list[Finding] = []
    whitespace = index.whitespace_errors()
    if whitespace:
        findings.append(Finding("error", "staged diff", whitespace))
    if not changes:
        return findings

    manifest = _load_manifest(index, findings)
    if manifest is not None:
        staged_paths = {change.path for change in changes}
        outside = sorted(staged_paths - set(manifest.allowed_paths))
        if outside:
            findings.append(
                Finding("error", "manifest", f"staged paths not allowed: {outside!r}")
            )

    ui_exempted = (
        manifest is not None
        and manifest.ui_literal_exemption == "approved-for-slice"
    )
    findings.extend(check_ui_magic_literals(index, changes, ui_exempted))

    structural = False
    for change in changes:
        if _is_python_source(change.path):
            structural = _check_source(index, change, findings) or structural
    if structural:
        findings.append(
            Finding(
                "warning",
                "structure",
                "structural source change should review existing ownership and reuse/commonization",
            )
        )
    return findings


def format_findings(findings: Sequence[Finding]) -> str:
    errors = [item for item in findings if item.severity == "error"]
    warnings = [item for item in findings if item.severity == "warning"]
    lines: list[str] = []
    if errors:
        lines.append(f"errors: {len(errors)}")
        lines.extend(f"  [E] {item.path}: {item.message}" for item in errors)
    if warnings:
        lines.append(f"warnings: {len(warnings)}")
        lines.extend(f"  [W] {item.path}: {item.message}" for item in warnings)
    if not findings:
        lines.append("agent change gate: OK")
    return "\n".join(lines) + "\n"


def _check_source(
    index: GitIndex,
    change: StagedChange,
    findings: list[Finding],
) -> bool:
    new_source = change.status == "A" and _is_production(change.path)
    staged = "" if change.status == "D" else index.index_text(change.path)
    base = index.head_text(change.old_path or change.path)
    loc = _loc(staged)
    classes = _class_count(staged, change.path, findings)
    if new_source:
        if loc > 350:
            findings.append(
                Finding(
                    "warning",
                    change.path,
                    f"new production source is {loc} LOC; review responsibility and split if ownership becomes clearer",
                )
            )
        elif loc > 250:
            findings.append(
                Finding(
                    "warning",
                    change.path,
                    f"new production source is {loc} LOC; review whether the responsibility is too broad",
                )
            )
        if classes > 5:
            findings.append(
                Finding(
                    "warning",
                    change.path,
                    f"new source defines {classes} top-level classes",
                )
            )
        if classes > 5 and loc > 250:
            findings.append(
                Finding(
                    "warning",
                    change.path,
                    "class-heavy source over 250 LOC should be reviewed for ownership split",
                )
            )
    if base is not None and max(_loc(base), loc) > 400 and loc - _loc(base) >= 40:
        findings.append(
            Finding(
                "warning",
                change.path,
                "hotspot net +40 LOC should trigger an ownership/responsibility review",
            )
        )
    return _is_structural(change, base, staged)


def _load_manifest(
    index: GitIndex, findings: list[Finding]
) -> TaskManifest | None:
    path = index.manifest_path()
    if not path.exists():
        return None
    try:
        return parse_manifest(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        findings.append(Finding("error", str(path), f"invalid manifest: {exc}"))
        return None


def _is_production(path: str) -> bool:
    return path.endswith(".py") and path.startswith(PRODUCTION_ROOTS)


def _is_python_source(path: str) -> bool:
    return path.endswith(".py") and path.startswith((*PRODUCTION_ROOTS, "tools/"))


def _loc(source: str) -> int:
    return 0 if not source else source.count("\n") + (
        0 if source.endswith("\n") else 1
    )


def _class_count(source: str, path: str, findings: list[Finding]) -> int:
    if not source:
        return 0
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        findings.append(Finding("error", path, f"syntax error: {exc}"))
        return 0
    return sum(isinstance(node, ast.ClassDef) for node in tree.body)


def _is_structural(change: StagedChange, base: str | None, staged: str) -> bool:
    if change.status in {"A", "D", "R", "C"}:
        return True
    try:
        before = ast.parse(base or "")
        after = ast.parse(staged)
    except SyntaxError:
        return True
    symbol_types = (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)
    before_names = {
        (type(node).__name__, node.name)
        for node in before.body
        if isinstance(node, symbol_types)
    }
    after_names = {
        (type(node).__name__, node.name)
        for node in after.body
        if isinstance(node, symbol_types)
    }
    return before_names != after_names
