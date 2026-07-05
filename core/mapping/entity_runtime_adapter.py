"""Adapt runtime mapping repository data into mapping entity catalogs."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

from core.mapping.entity_model import (
    MappingAttributeDefinition,
    MappingEntityCatalog,
    MappingEntityDefinition,
    MappingEntityRow,
)
from core.mapping.paths import MAPPING_JSON_FILE
from core.mapping.repository import load_mapping_data


def load_runtime_mapping_catalog(mapping_file: str | None = None) -> MappingEntityCatalog:
    """Load runtime mapping data and adapt it to a read-only entity catalog."""
    source_path = mapping_file or MAPPING_JSON_FILE
    mapping_data = load_mapping_data(source_path)
    if not mapping_data:
        raise ValueError(f"runtime mapping data is empty or unavailable: {source_path}")
    if not isinstance(mapping_data, Mapping):
        raise ValueError("runtime mapping data must be a JSON object")
    return adapt_runtime_mapping_data(mapping_data, source_label=source_path)


def adapt_runtime_mapping_data(
    mapping_data: Mapping[str, Any],
    *,
    source_label: str = "runtime mapping repository",
) -> MappingEntityCatalog:
    """Return a deterministic read-only catalog for runtime mapping data."""
    entities: list[MappingEntityDefinition] = []
    rows: list[MappingEntityRow] = []

    for section_key in sorted(str(key) for key in mapping_data):
        section = mapping_data.get(section_key)
        if not isinstance(section, Mapping):
            continue
        entity_rows = _rows_for_section(section_key, section)
        entities.append(_entity_definition(section_key, entity_rows))
        rows.extend(entity_rows)

    if not entities:
        raise ValueError("runtime mapping data contains no table-shaped sections")
    return MappingEntityCatalog(
        entities=tuple(entities),
        rows=tuple(rows),
        notes=f"Read-only runtime mapping repository snapshot: {source_label}",
    )


def runtime_mapping_source_label(mapping_file: str | None = None) -> str:
    """Return a compact display label for the runtime mapping source."""
    source_path = Path(mapping_file or MAPPING_JSON_FILE)
    return f"Runtime mapping repository: {source_path}"


def _entity_definition(
    section_key: str,
    rows: tuple[MappingEntityRow, ...],
) -> MappingEntityDefinition:
    key_attribute = _key_attribute(section_key)
    attributes = [MappingAttributeDefinition(key_attribute, _label(key_attribute))]
    attribute_keys = _attribute_keys(rows)
    attributes.extend(
        MappingAttributeDefinition(
            attribute_key,
            _label(attribute_key),
            data_type=_infer_data_type(rows, attribute_key),
        )
        for attribute_key in attribute_keys
        if attribute_key != key_attribute
    )
    nested_count = sum(1 for row in rows if row.notes)
    notes = "Read-only runtime mapping section."
    if nested_count:
        notes = f"{notes} {nested_count} row(s) contain nested values not flattened."
    return MappingEntityDefinition(
        entity_key=section_key,
        label=_label(section_key),
        key_attribute=key_attribute,
        attributes=tuple(attributes),
        notes=notes,
    )


def _rows_for_section(
    section_key: str,
    section: Mapping[Any, Any],
) -> tuple[MappingEntityRow, ...]:
    rows: list[MappingEntityRow] = []
    for row_key in sorted(str(key) for key in section):
        row_value = section.get(row_key)
        values: dict[str, Any] = {}
        nested_keys: list[str] = []
        if isinstance(row_value, Mapping):
            for attribute_key in sorted(str(key) for key in row_value):
                value = row_value.get(attribute_key)
                if isinstance(value, Mapping):
                    nested_keys.append(attribute_key)
                    continue
                values[attribute_key] = value
        elif row_value is not None:
            values["value"] = row_value
        rows.append(
            MappingEntityRow(
                entity_key=section_key,
                row_key=row_key,
                values=values,
                notes=_nested_note(nested_keys),
            )
        )
    return tuple(rows)


def _attribute_keys(rows: tuple[MappingEntityRow, ...]) -> tuple[str, ...]:
    keys: set[str] = set()
    for row in rows:
        keys.update(str(key) for key in row.values)
    return tuple(sorted(keys))


def _infer_data_type(rows: tuple[MappingEntityRow, ...], attribute_key: str) -> str:
    values = [
        row.value_for(attribute_key)
        for row in rows
        if row.value_for(attribute_key) not in (None, "")
    ]
    if values and all(isinstance(value, bool) for value in values):
        return "boolean"
    if values and all(_is_number(value) for value in values):
        return "number"
    return "string"


def _is_number(value: Any) -> bool:
    if isinstance(value, bool):
        return False
    if isinstance(value, (int, float)):
        return True
    try:
        float(str(value).strip())
    except (TypeError, ValueError):
        return False
    return True


def _key_attribute(section_key: str) -> str:
    return f"{section_key}_key"


def _label(key: str) -> str:
    return str(key).replace("_", " ").strip().title()


def _nested_note(nested_keys: list[str]) -> str:
    if not nested_keys:
        return ""
    return "Nested values not flattened: " + ", ".join(sorted(nested_keys))
