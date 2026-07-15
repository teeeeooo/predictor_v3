"""Canonical CSV records and serialization for mapping_bundle_v1."""

from __future__ import annotations

import csv
import io
from typing import Any

from core.mapping.condenser_identity import condenser_requires_pi
from core.mapping.editor_model import MappingEditorDraft, MappingEditorGroup, MappingEditorRow
from core.mapping.editor_projection import (
    COMPRESSOR_GROUP,
    EVAP_INDEX_GROUP,
    EXPANSION_GROUP,
    IDU_GROUP,
    ODU_COND_SPECS_GROUP,
    ODU_GROUP,
    REFRIGERANT_GROUP,
)
from core.mapping.value_policy import (
    coerce_mapping_boolean,
    coerce_mapping_number,
    mapping_column_data_type,
)

BUNDLE_FORMAT_MARKER = "__FORMAT__"
BUNDLE_SECTION_MARKER = "__SECTION__"
BUNDLE_FORMAT = "mapping_bundle_v1"
CANONICAL_GROUP_KEYS = (
    IDU_GROUP,
    EVAP_INDEX_GROUP,
    ODU_GROUP,
    COMPRESSOR_GROUP,
    REFRIGERANT_GROUP,
    EXPANSION_GROUP,
    ODU_COND_SPECS_GROUP,
)
CANONICAL_GROUP_FILENAMES = tuple(f"{group_key}.csv" for group_key in CANONICAL_GROUP_KEYS)


def exchange_group_records(group: MappingEditorGroup) -> tuple[tuple[str, ...], ...]:
    """Return one group's header and visible rows as canonical CSV records."""
    return (
        tuple(group.columns),
        *tuple(
            tuple(_exchange_value_text(group, row, column) for column in group.columns)
            for row in group.rows
        ),
    )


def serialize_group_csv(group: MappingEditorGroup) -> bytes:
    """Serialize one group using the official UTF-8, LF-delimited CSV policy."""
    return _serialize_records(exchange_group_records(group))


def serialize_bundle_csv(draft: MappingEditorDraft) -> bytes:
    """Serialize all seven groups in canonical section order."""
    groups = {group.group_key: group for group in draft.groups}
    output = io.StringIO(newline="")
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow((BUNDLE_FORMAT_MARKER, BUNDLE_FORMAT))
    for group_key in CANONICAL_GROUP_KEYS:
        writer.writerow(())
        writer.writerow((BUNDLE_SECTION_MARKER, group_key))
        for record in exchange_group_records(groups[group_key]):
            writer.writerow(record)
    return output.getvalue().encode("utf-8")


def _serialize_records(records: tuple[tuple[str, ...], ...]) -> bytes:
    output = io.StringIO(newline="")
    writer = csv.writer(output, lineterminator="\n")
    writer.writerows(records)
    return output.getvalue().encode("utf-8")


def _exchange_value_text(
    group: MappingEditorGroup,
    row: MappingEditorRow,
    column: str,
) -> str:
    """Return a stable user-facing text value without exposing hidden payload."""
    value: Any = row.value_for(column, "")
    if group.group_key == ODU_COND_SPECS_GROUP and column == "Pi":
        if not condenser_requires_pi(row.value_for("Fin Type", "")):
            return ""
    if value is None or (isinstance(value, str) and not value.strip()):
        return ""
    data_type = mapping_column_data_type(group, column)
    if data_type == "number":
        return str(coerce_mapping_number(value))
    if data_type == "boolean":
        return "true" if coerce_mapping_boolean(value) else "false"
    return str(value)
