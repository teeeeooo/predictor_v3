"""Strict bootstrap adapter for the validation-only legacy wide mapping CSV."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from apps.train.adapters.mapping._legacy_layout import (
    EXPECTED_HEADERS,
    LEGACY_BLOCKS,
    LegacyBlock,
)
from apps.train.adapters.mapping._legacy_validation import (
    LegacyMappingBootstrapError,
    parse_number,
    reject_duplicate,
)
from core.mapping.condenser_identity import (
    condenser_identity,
    condenser_requires_pi,
    condenser_spec_key,
)
from core.mapping.editor_model import MappingEditorDraft, MappingEditorGroup, MappingEditorRow
from core.mapping.editor_projection import (
    ODU_COND_SPECS_GROUP,
)
from core.mapping.editor_validation import validate_mapping_editor_draft

def parse_legacy_mapping_csv(source: str | Path) -> MappingEditorDraft:
    """Parse the fixed legacy-wide layout into a validated editor-owned draft."""
    rows = _read_rows(Path(source))
    parsed: dict[str, list[MappingEditorRow]] = {
        block.group_key: [] for block in LEGACY_BLOCKS
    }
    parsed[ODU_COND_SPECS_GROUP] = []
    seen: dict[str, dict[Any, int]] = {group_key: {} for group_key in parsed}
    contexts: dict[tuple[str, str], int] = {}

    for legacy_row, row in enumerate(rows[1:], start=2):
        if len(row) != len(EXPECTED_HEADERS):
            raise LegacyMappingBootstrapError(
                f"legacy layout row has {len(row)} columns; expected {len(EXPECTED_HEADERS)}",
                legacy_row=legacy_row,
                block="layout",
            )
        for block in LEGACY_BLOCKS:
            parsed_row = _parse_block(row, legacy_row, block, seen[block.group_key])
            if parsed_row is not None:
                parsed[block.group_key].append(parsed_row)
                contexts[(block.group_key, parsed_row.source_key)] = legacy_row
        condenser_row = _parse_condenser(row, legacy_row, seen[ODU_COND_SPECS_GROUP])
        if condenser_row is not None:
            parsed[ODU_COND_SPECS_GROUP].append(condenser_row)
            contexts[(ODU_COND_SPECS_GROUP, condenser_row.source_key)] = legacy_row

    draft = MappingEditorDraft(
        groups=tuple(
            _editor_group(block, parsed[block.group_key]) for block in LEGACY_BLOCKS
        )
        + (_condenser_group(parsed[ODU_COND_SPECS_GROUP]),),
        source_label="Legacy mapping bootstrap",
    )
    _require_valid_draft(draft, contexts)
    return draft


def _read_rows(source: Path) -> list[list[str]]:
    try:
        with source.open(newline="", encoding="utf-8-sig") as csv_file:
            rows = list(csv.reader(csv_file))
    except (OSError, UnicodeError, csv.Error) as exc:
        raise LegacyMappingBootstrapError(str(exc), block="layout") from exc
    if not rows:
        raise LegacyMappingBootstrapError("legacy layout is empty", block="layout")
    headers = tuple(cell.strip() for cell in rows[0])
    if headers != EXPECTED_HEADERS:
        mismatch = next(
            (index for index, pair in enumerate(zip(headers, EXPECTED_HEADERS)) if pair[0] != pair[1]),
            min(len(headers), len(EXPECTED_HEADERS)),
        )
        raise LegacyMappingBootstrapError(
            "legacy header/layout does not match the required wide-table contract",
            legacy_row=1,
            block="layout",
            field=f"column {mismatch + 1}",
        )
    return rows


def _parse_block(
    row: list[str],
    legacy_row: int,
    block: LegacyBlock,
    seen: dict[Any, int],
) -> MappingEditorRow | None:
    key = row[block.indexes[0]].strip()
    if not key:
        return None
    reject_duplicate(seen, key, legacy_row, block.group_key, "duplicate primary key")
    values: dict[str, Any] = {}
    for column, index in zip(block.columns, block.indexes):
        raw_value = row[index].strip()
        values[column] = (
            parse_number(raw_value, legacy_row, block.group_key, column, key)
            if column in block.numeric_columns
            else raw_value
        )
    return MappingEditorRow(values=values, source_key=key)


def _parse_condenser(
    row: list[str],
    legacy_row: int,
    seen: dict[Any, int],
) -> MappingEditorRow | None:
    odu = row[16].strip()
    if not odu:
        return None
    fin = row[17].strip()
    pi = row[18].strip()
    row_value = row[19].strip()
    for field, value in (("Fin Type", fin), ("Row", row_value)):
        if not value:
            raise LegacyMappingBootstrapError(
                "required condenser field is missing",
                legacy_row=legacy_row,
                block=ODU_COND_SPECS_GROUP,
                field=field,
                key=odu,
            )
    if condenser_requires_pi(fin) and not pi:
        raise LegacyMappingBootstrapError(
            "required condenser field is missing",
            legacy_row=legacy_row,
            block=ODU_COND_SPECS_GROUP,
            field="Pi",
            key=odu,
        )
    normalized_pi = pi if condenser_requires_pi(fin) else ""
    identity = condenser_identity(odu, fin, normalized_pi, row_value)
    key = condenser_spec_key(odu, fin, normalized_pi, row_value)
    reject_duplicate(
        seen,
        identity,
        legacy_row,
        ODU_COND_SPECS_GROUP,
        "duplicate condenser identity",
        key,
    )
    values = {
        "ODU": odu,
        "Fin Type": fin,
        "Pi": normalized_pi,
        "Row": row_value,
        "Cond Area": parse_number(
            row[21].strip(), legacy_row, ODU_COND_SPECS_GROUP, "Cond Area", key
        ),
        "Cond Volume": parse_number(
            row[22].strip(), legacy_row, ODU_COND_SPECS_GROUP, "Cond Volume", key
        ),
    }
    return MappingEditorRow(values=values, source_key=key)


def _editor_group(
    block: LegacyBlock,
    rows: list[MappingEditorRow],
) -> MappingEditorGroup:
    return MappingEditorGroup(
        group_key=block.group_key,
        label=block.label,
        columns=block.columns,
        rows=tuple(sorted(rows, key=lambda item: item.source_key)),
        runtime_sections=block.runtime_sections,
    )


def _condenser_group(rows: list[MappingEditorRow]) -> MappingEditorGroup:
    return MappingEditorGroup(
        group_key=ODU_COND_SPECS_GROUP,
        label="ODU Cond Specs",
        columns=("ODU", "Fin Type", "Pi", "Row", "Cond Area", "Cond Volume"),
        rows=tuple(
            sorted(
                rows,
                key=lambda item: condenser_identity(
                    item.value_for("ODU"),
                    item.value_for("Fin Type"),
                    item.value_for("Pi"),
                    item.value_for("Row"),
                ),
            )
        ),
        runtime_sections=("odu_cascade", "cond_specs", "fin_type", "pi", "row"),
    )


def _require_valid_draft(
    draft: MappingEditorDraft,
    contexts: dict[tuple[str, str], int],
) -> None:
    validation = validate_mapping_editor_draft(draft)
    if validation.save_enabled:
        return
    issue = next(item for item in validation.issues if item.severity == "error")
    group = next((item for item in draft.groups if item.label == issue.entity_key), None)
    group_key = group.group_key if group is not None else issue.entity_key
    legacy_row = contexts.get((group_key, issue.row_key))
    raise LegacyMappingBootstrapError(
        issue.message,
        legacy_row=legacy_row,
        block=group_key,
        field=issue.attribute_key or issue.field,
        key=issue.row_key,
    )
