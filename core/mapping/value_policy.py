"""Canonical Qt-free value policy for definition-backed mapping attributes."""

from __future__ import annotations

import math
from typing import Any

from core.mapping.editor_model import MappingEditorGroup

_TRUE_VALUES = frozenset({"true", "1", "yes"})
_FALSE_VALUES = frozenset({"false", "0", "no"})
_BUILTIN_NUMERIC_COLUMNS = {
    "idu": frozenset({"ID Volume"}),
    "evap_index": frozenset({"Evap Area", "Evap Volume"}),
    "odu": frozenset({"OD Volume"}),
    "compressor": frozenset({"Comp EER", "Comp cc"}),
    "odu_cond_specs": frozenset({"Cond Area", "Cond Volume"}),
}


def coerce_mapping_number(value: Any) -> int | float:
    """Return one finite JSON number or raise ``ValueError``."""
    if isinstance(value, bool):
        raise ValueError("boolean is not a mapping number")
    try:
        number = float(str(value).strip())
    except (TypeError, ValueError) as exc:
        raise ValueError("mapping number is invalid") from exc
    if not math.isfinite(number):
        raise ValueError("mapping number must be finite")
    return int(number) if number.is_integer() else number


def coerce_mapping_boolean(value: Any) -> bool:
    """Return one canonical boolean or raise ``ValueError``."""
    if isinstance(value, bool):
        return value
    normalized = "" if value is None else str(value).strip().lower()
    if normalized in _TRUE_VALUES:
        return True
    if normalized in _FALSE_VALUES:
        return False
    raise ValueError("mapping boolean is invalid")


def coerce_mapping_value(value: Any, data_type: str) -> Any:
    """Coerce a supported definition-backed value for runtime persistence."""
    if value is None or (isinstance(value, str) and not value.strip()):
        return ""
    if data_type == "number":
        return coerce_mapping_number(value)
    if data_type == "boolean":
        return coerce_mapping_boolean(value)
    return value


def mapping_column_data_type(group: MappingEditorGroup, column: str) -> str:
    """Return one canonical visible-column type for mutation and validation."""
    declared = group.column_data_types.get(column)
    if declared in {"string", "number", "boolean"}:
        return declared
    if column in _BUILTIN_NUMERIC_COLUMNS.get(group.group_key, ()):
        return "number"
    return "string"


def canonicalize_mapping_cell_input(
    group: MappingEditorGroup,
    column: str,
    value: Any,
) -> Any:
    """Canonicalize valid input while preserving invalid text for validation."""
    try:
        return coerce_mapping_value(value, mapping_column_data_type(group, column))
    except ValueError:
        return value


def is_valid_mapping_number(value: Any) -> bool:
    """Return whether ``value`` satisfies the finite mapping-number contract."""
    try:
        coerce_mapping_number(value)
    except ValueError:
        return False
    return True


def is_valid_mapping_boolean(value: Any) -> bool:
    """Return whether ``value`` is one approved canonical boolean input."""
    try:
        coerce_mapping_boolean(value)
    except ValueError:
        return False
    return True
