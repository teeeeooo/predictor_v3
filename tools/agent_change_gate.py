"""Policy evaluation for staged agent changes."""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Sequence

from tools.agent_change_gate_git import GitIndex, StagedChange
from tools.agent_change_gate_ui_literals import check_ui_magic_literals
from tools.agent_change_gate_models import (
    ChangeGate,
    Finding,
    TaskManifest,
    parse_change_gate,
    parse_manifest,
)

ACTIVE_REPORT_ROOT = "result_reports/active/"
CODE_MAP_PATH = "docs/code_map/CODEBASE_REFERENCE_MAP.md"
PRODUCTION_ROOTS = ("core/", "ui/", "apps/", "scripts/")
RELEVANT_ROOTS = (*PRODUCTION_ROOTS, "tests/", "tools/", "data/region_configs/")

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
            findings.append(Finding("error", "manifest", f"staged paths not allowed: {outside!r}"))

    relevant = tuple(change for change in changes if _is_relevant(change.path))
    report_changes = tuple(
        change for change in changes if change.path.startswith(ACTIVE_REPORT_ROOT)
    )
    gate = _associated_gate(index, relevant, report_changes, manifest, findings)
    findings.extend(check_ui_magic_literals(index, changes, gate))

    structural = False
    for change in changes:
        if _is_python_source(change.path):
            structural = _check_source(index, change, gate, findings) or structural
    if structural and (gate is None or gate.code_map_check == "not_required"):
        findings.append(Finding("error", CODE_MAP_PATH, "structural source change requires code_map_check judgment"))
    if structural and (
        gate is None or gate.reuse_commonization == "not_required"
    ):
        findings.append(
            Finding(
                "error",
                "change_gate",
                "structural source change requires reuse_commonization decision",
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


def _associated_gate(
    index: GitIndex,
    relevant: Sequence[StagedChange],
    reports: Sequence[StagedChange],
    manifest: TaskManifest | None,
    findings: list[Finding],
) -> ChangeGate | None:
    if not relevant:
        return None
    selected = manifest.report_path if manifest is not None else None
    report_paths = {item.path for item in reports}
    if selected is not None and selected not in report_paths:
        findings.append(Finding("error", selected, "manifest report_path is not a staged active report"))
        return None
    if selected is None:
        if len(reports) == 1:
            selected = reports[0].path
        elif len(reports) > 1:
            findings.append(Finding("error", ACTIVE_REPORT_ROOT, "multiple staged reports require manifest report_path"))
            return None
        elif manifest is not None and _valid_exemption(index, relevant, manifest, findings):
            return None
        else:
            findings.append(Finding("error", ACTIVE_REPORT_ROOT, "relevant staged change requires one active report"))
            return None
    try:
        return parse_change_gate(index.index_text(selected))
    except ValueError as exc:
        findings.append(Finding("error", selected, str(exc)))
        return None


def _check_source(
    index: GitIndex,
    change: StagedChange,
    gate: ChangeGate | None,
    findings: list[Finding],
) -> bool:
    new_source = change.status == "A" and _is_production(change.path)
    staged = "" if change.status == "D" else index.index_text(change.path)
    base = index.head_text(change.old_path or change.path)
    loc = _loc(staged)
    classes = _class_count(staged, change.path, findings)
    if new_source:
        if loc > 350:
            findings.append(Finding("error", change.path, f"new production source exceeds 350 LOC ({loc})"))
        elif loc > 250 and (gate is None or gate.new_source not in {"split", "justified"}):
            findings.append(Finding("error", change.path, f"new production source {loc} LOC requires split/justified"))
        if classes > 5:
            findings.append(Finding("warning", change.path, f"new source defines {classes} top-level classes"))
        if classes > 5 and loc > 250 and (gate is None or gate.new_source != "justified"):
            findings.append(Finding("error", change.path, "class-heavy source over 250 LOC requires new_source: justified"))
    if base is not None and max(_loc(base), loc) > 400 and loc - _loc(base) >= 40:
        accepted = {"wiring-only", "accepted-for-slice", "split-audit-required", "split-required"}
        if gate is None or gate.hotspot_delta not in accepted:
            findings.append(Finding("error", change.path, "hotspot net +40 LOC requires hotspot_delta decision"))
    return _is_structural(change, base, staged)


def _valid_exemption(
    index: GitIndex,
    relevant: Sequence[StagedChange],
    manifest: TaskManifest,
    findings: list[Finding],
) -> bool:
    if manifest.reason in {"commit-push-only", "status-only"}:
        findings.append(Finding("error", "manifest", f"{manifest.reason} cannot authorize staged content"))
        return False
    if manifest.reason == "user-approved-docs-only":
        valid = all(item.path.startswith(("docs/", "result_reports/")) for item in relevant)
    else:
        valid = all(_formatting_only(index, item) for item in relevant)
    if not valid:
        findings.append(Finding("error", "manifest", "staged change is not eligible for report exemption"))
    return valid


def _formatting_only(index: GitIndex, change: StagedChange) -> bool:
    if change.status != "M":
        return False
    before = index.head_text(change.path)
    after = index.index_text(change.path)
    if before is None:
        return False
    if change.path.endswith(".py"):
        try:
            return ast.dump(ast.parse(before)) == ast.dump(ast.parse(after))
        except SyntaxError:
            return False
    return "".join(before.split()) == "".join(after.split())


def _load_manifest(index: GitIndex, findings: list[Finding]) -> TaskManifest | None:
    path = index.manifest_path()
    if not path.exists():
        return None
    try:
        return parse_manifest(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        findings.append(Finding("error", str(path), f"invalid manifest: {exc}"))
        return None


def _is_relevant(path: str) -> bool:
    return path == CODE_MAP_PATH or path.startswith(RELEVANT_ROOTS)


def _is_production(path: str) -> bool:
    return path.endswith(".py") and path.startswith(PRODUCTION_ROOTS)


def _is_python_source(path: str) -> bool:
    return path.endswith(".py") and path.startswith((*PRODUCTION_ROOTS, "tools/"))


def _loc(source: str) -> int:
    return 0 if not source else source.count("\n") + (0 if source.endswith("\n") else 1)


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
    before_names = {(type(node).__name__, node.name) for node in before.body if isinstance(node, symbol_types)}
    after_names = {(type(node).__name__, node.name) for node in after.body if isinstance(node, symbol_types)}
    return before_names != after_names
