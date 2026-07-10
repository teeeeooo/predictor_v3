"""Staged result-record validation for the agent change gate."""

from __future__ import annotations

import re
from typing import Sequence

from tools.agent_change_gate_git import GitIndex, StagedChange
from tools.agent_change_gate_models import (
    ChangeGate,
    Finding,
    TaskManifest,
    parse_change_gate,
    parse_record_metadata,
)

RECORD_ROOT = "result_reports/records/"
REPORT_INDEX_PATH = "result_reports/REPORT_INDEX.md"
MEMORY_SEED_PATH = "result_reports/memory/project_memory_seed.md"
_RECORD_PATH_PATTERN = re.compile(
    r"^result_reports/records/(\d{4}-\d{2})/"
    r"(\d{4}-\d{2}-\d{2})-[a-z0-9][a-z0-9-]*\.md$"
)


def validate_records(
    index: GitIndex,
    changes: Sequence[StagedChange],
    records: Sequence[StagedChange],
    manifest: TaskManifest | None,
    findings: list[Finding],
) -> ChangeGate | None:
    if not records:
        if manifest is not None and manifest.report_path:
            findings.append(
                Finding(
                    "error",
                    manifest.report_path,
                    "manifest report_path is not a staged result record",
                )
            )
        return None

    staged_paths = {change.path for change in changes if change.status != "D"}
    index_source = ""
    if REPORT_INDEX_PATH in staged_paths:
        index_source = index.index_text(REPORT_INDEX_PATH)
    else:
        findings.append(
            Finding(
                "error",
                REPORT_INDEX_PATH,
                "new result records require a staged REPORT_INDEX.md update",
            )
        )

    gates: dict[str, ChangeGate] = {}
    for record in records:
        if record.status != "A":
            findings.append(
                Finding(
                    "error",
                    record.path,
                    "result records are append-only; create a correction record",
                )
            )
            continue
        match = _RECORD_PATH_PATTERN.fullmatch(record.path)
        if match is None or match.group(1) != match.group(2)[:7]:
            findings.append(
                Finding(
                    "error",
                    record.path,
                    "record path must use records/YYYY-MM/YYYY-MM-DD-<slug>.md",
                )
            )
            continue
        source = index.index_text(record.path)
        try:
            metadata = parse_record_metadata(source)
        except ValueError as exc:
            findings.append(Finding("error", record.path, str(exc)))
            continue
        if metadata.date != match.group(2):
            findings.append(
                Finding("error", record.path, "record date must match its filename")
            )
        if f"`{record.path}`" not in index_source:
            findings.append(
                Finding("error", REPORT_INDEX_PATH, f"missing index row for {record.path}")
            )
        if (
            metadata.memory_review == "updated"
            and MEMORY_SEED_PATH not in staged_paths
        ):
            findings.append(
                Finding(
                    "error",
                    MEMORY_SEED_PATH,
                    "memory_review: updated requires the staged memory seed",
                )
            )
        if _has_block(source, "change_gate"):
            try:
                gates[record.path] = parse_change_gate(source)
            except ValueError as exc:
                findings.append(Finding("error", record.path, str(exc)))

    selected = manifest.report_path if manifest is not None else None
    if selected:
        if selected not in {record.path for record in records}:
            findings.append(
                Finding(
                    "error",
                    selected,
                    "manifest report_path is not a staged result record",
                )
            )
            return None
        return gates.get(selected)
    if len(gates) == 1:
        return next(iter(gates.values()))
    if len(gates) > 1:
        findings.append(
            Finding(
                "warning",
                RECORD_ROOT,
                "multiple change_gate records require manifest selection for exemptions",
            )
        )
    return None


def _has_block(source: str, heading: str) -> bool:
    return any(line.strip() == f"{heading}:" for line in source.splitlines())
