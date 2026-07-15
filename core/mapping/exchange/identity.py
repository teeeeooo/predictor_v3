"""Canonical visible-row identity for mapping exchange import and diffing."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from core.mapping.condenser_identity import (
    canonical_condenser_pi,
    condenser_identity,
)
from core.mapping.editor_model import MappingEditorGroup, MappingEditorRow
from core.mapping.editor_projection import ODU_COND_SPECS_GROUP


def exchange_row_identity(
    group: MappingEditorGroup,
    row: MappingEditorRow,
) -> tuple[str, ...] | None:
    """Return one row's canonical visible identity, or ``None`` when blank."""
    return exchange_values_identity(group, row.values)


def exchange_values_identity(
    group: MappingEditorGroup,
    values: Mapping[str, Any],
) -> tuple[str, ...] | None:
    """Return canonical identity components from visible values."""
    if group.group_key == ODU_COND_SPECS_GROUP:
        odu = _clean(values.get("ODU", ""))
        fin_type = _clean(values.get("Fin Type", ""))
        pi = canonical_condenser_pi(fin_type, values.get("Pi", ""))
        row = _clean(values.get("Row", ""))
        identity = condenser_identity(odu, fin_type, pi, row)
        return identity if all(identity) else None
    if not group.columns:
        return None
    key = _clean(values.get(group.columns[0], ""))
    return (key,) if key else None


def normalize_exchange_identity_values(
    group: MappingEditorGroup,
    values: dict[str, Any],
) -> tuple[str, ...] | None:
    """Normalize identity text in-place and return its canonical identity."""
    if group.group_key == ODU_COND_SPECS_GROUP:
        for column in ("ODU", "Fin Type", "Row"):
            values[column] = _clean(values.get(column, ""))
        values["Pi"] = canonical_condenser_pi(
            values.get("Fin Type", ""),
            values.get("Pi", ""),
        )
    elif group.columns:
        key_column = group.columns[0]
        values[key_column] = _clean(values.get(key_column, ""))
    return exchange_values_identity(group, values)


def _clean(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()
