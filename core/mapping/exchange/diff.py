"""Visible-value change summaries for mapping exchange previews."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from core.mapping.condenser_identity import condenser_requires_pi
from core.mapping.editor_model import MappingEditorDraft, MappingEditorGroup, MappingEditorRow
from core.mapping.editor_projection import ODU_COND_SPECS_GROUP
from core.mapping.exchange.identity import exchange_row_identity
from core.mapping.value_policy import (
    coerce_mapping_boolean,
    coerce_mapping_number,
    mapping_column_data_type,
)


@dataclass(frozen=True)
class MappingExchangeGroupDiff:
    """Change counts for one full-snapshot replacement group."""

    group_key: str
    label: str
    existing_rows: int
    added_rows: int
    removed_rows: int
    changed_rows: int
    unchanged_rows: int


def diff_mapping_exchange_drafts(
    current: MappingEditorDraft,
    candidate: MappingEditorDraft,
) -> tuple[MappingExchangeGroupDiff, ...]:
    """Compare identities and visible owned values, ignoring row order/hidden data."""
    current_groups = {group.group_key: group for group in current.groups}
    candidate_groups = {group.group_key: group for group in candidate.groups}
    return tuple(
        _group_diff(current_groups[group_key], candidate_groups[group_key])
        for group_key in candidate_groups
        if group_key in current_groups
    )


def _group_diff(
    current: MappingEditorGroup,
    candidate: MappingEditorGroup,
) -> MappingExchangeGroupDiff:
    current_rows = _identity_rows(current)
    candidate_rows = _identity_rows(candidate)
    current_keys = set(current_rows)
    candidate_keys = set(candidate_rows)
    common = current_keys & candidate_keys
    changed = sum(
        not _same_visible_values(current, current_rows[key], candidate_rows[key])
        for key in common
    )
    return MappingExchangeGroupDiff(
        group_key=candidate.group_key,
        label=candidate.label,
        existing_rows=len(current.rows),
        added_rows=len(candidate_keys - current_keys),
        removed_rows=len(current_keys - candidate_keys),
        changed_rows=changed,
        unchanged_rows=len(common) - changed,
    )


def _identity_rows(group: MappingEditorGroup) -> dict[tuple[str, ...], MappingEditorRow]:
    return {
        identity: row
        for row in group.rows
        if (identity := exchange_row_identity(group, row)) is not None
    }


def _same_visible_values(
    group: MappingEditorGroup,
    current: MappingEditorRow,
    candidate: MappingEditorRow,
) -> bool:
    return all(
        _semantic_value(group, current, column) == _semantic_value(group, candidate, column)
        for column in group.columns
    )


def _semantic_value(group: MappingEditorGroup, row: MappingEditorRow, column: str) -> Any:
    value = row.value_for(column, "")
    if group.group_key == ODU_COND_SPECS_GROUP and column == "Pi":
        if not condenser_requires_pi(row.value_for("Fin Type", "")):
            return ""
    if value is None or (isinstance(value, str) and not value.strip()):
        return ""
    data_type = mapping_column_data_type(group, column)
    try:
        if data_type == "number":
            return coerce_mapping_number(value)
        if data_type == "boolean":
            return coerce_mapping_boolean(value)
    except ValueError:
        return str(value)
    return value
