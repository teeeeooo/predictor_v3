"""Validation for generic mapping entity and master data catalogs."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from core.mapping.entity_model import (
    MappingAttributeDefinition,
    MappingEntityCatalog,
    MappingEntityDefinition,
    MappingEntityRow,
    MappingValidationError,
)

ALLOWED_DATA_TYPES = frozenset({"string", "number", "boolean"})
_TRUE_VALUES = frozenset({"true", "1", "yes"})
_FALSE_VALUES = frozenset({"false", "0", "no"})


def validate_mapping_entity_catalog(
    catalog: MappingEntityCatalog,
) -> tuple[MappingValidationError, ...]:
    """Return validation errors for generic mapping entity definitions and rows."""
    errors: list[MappingValidationError] = []
    definitions_by_key = _validate_entity_definitions(catalog.entities, errors)
    _validate_rows(catalog.rows, definitions_by_key, errors)
    return tuple(errors)


def _validate_entity_definitions(
    entities: tuple[MappingEntityDefinition, ...],
    errors: list[MappingValidationError],
) -> dict[str, MappingEntityDefinition]:
    definitions_by_key: dict[str, MappingEntityDefinition] = {}
    seen_entity_keys: dict[str, MappingEntityDefinition] = {}

    for entity in entities:
        entity_key = _clean(entity.entity_key)
        if not entity_key:
            errors.append(
                _error(
                    "blank_entity_key",
                    "entity key must not be blank",
                    entity_key=entity.entity_key,
                    field="entity_key",
                )
            )
            continue
        if entity_key in seen_entity_keys:
            errors.append(
                _error(
                    "duplicate_entity_key",
                    f"duplicate entity key '{entity_key}'",
                    entity_key=entity.entity_key,
                    field="entity_key",
                )
            )
        else:
            seen_entity_keys[entity_key] = entity
            definitions_by_key[entity_key] = entity

        _validate_attributes(entity, errors)

    return definitions_by_key


def _validate_attributes(
    entity: MappingEntityDefinition,
    errors: list[MappingValidationError],
) -> None:
    seen_attribute_keys: set[str] = set()
    attribute_keys: set[str] = set()

    for attribute in entity.attributes:
        attribute_key = _clean(attribute.attribute_key)
        if attribute_key in seen_attribute_keys:
            errors.append(
                _error(
                    "duplicate_attribute_key",
                    f"duplicate attribute key '{attribute_key}'",
                    entity_key=entity.entity_key,
                    attribute_key=attribute.attribute_key,
                    field="attribute_key",
                )
            )
        else:
            seen_attribute_keys.add(attribute_key)
            attribute_keys.add(attribute_key)
        if attribute.data_type not in ALLOWED_DATA_TYPES:
            errors.append(
                _error(
                    "invalid_attribute_data_type",
                    f"unsupported data_type '{attribute.data_type}'",
                    entity_key=entity.entity_key,
                    attribute_key=attribute.attribute_key,
                    field="data_type",
                )
            )

    if _clean(entity.key_attribute) not in attribute_keys:
        errors.append(
            _error(
                "missing_key_attribute",
                f"key_attribute '{entity.key_attribute}' is not defined",
                entity_key=entity.entity_key,
                attribute_key=entity.key_attribute,
                field="key_attribute",
            )
        )


def _validate_rows(
    rows: tuple[MappingEntityRow, ...],
    definitions_by_key: dict[str, MappingEntityDefinition],
    errors: list[MappingValidationError],
) -> None:
    row_keys_by_entity: dict[str, set[str]] = defaultdict(set)

    for row in rows:
        entity_key = _clean(row.entity_key)
        row_key = _clean(row.row_key)
        entity = definitions_by_key.get(entity_key)

        if entity is None:
            errors.append(
                _error(
                    "unknown_row_entity",
                    f"row references unknown entity '{row.entity_key}'",
                    entity_key=row.entity_key,
                    row_key=row.row_key,
                    field="entity_key",
                )
            )
            continue
        if not row_key:
            errors.append(
                _error(
                    "blank_row_key",
                    "row key must not be blank",
                    entity_key=row.entity_key,
                    row_key=row.row_key,
                    field="row_key",
                )
            )
        elif row_key in row_keys_by_entity[entity_key]:
            errors.append(
                _error(
                    "duplicate_row_key",
                    f"duplicate row key '{row_key}'",
                    entity_key=row.entity_key,
                    row_key=row.row_key,
                    field="row_key",
                )
            )
        else:
            row_keys_by_entity[entity_key].add(row_key)

        _validate_row_values(row, entity, errors)


def _validate_row_values(
    row: MappingEntityRow,
    entity: MappingEntityDefinition,
    errors: list[MappingValidationError],
) -> None:
    attributes_by_key = {
        attribute.attribute_key: attribute for attribute in entity.attributes
    }
    key_attribute = _clean(entity.key_attribute)

    for attribute_key in row.values:
        if attribute_key not in attributes_by_key:
            errors.append(
                _error(
                    "unknown_attribute_value",
                    f"unknown attribute '{attribute_key}'",
                    entity_key=row.entity_key,
                    row_key=row.row_key,
                    attribute_key=attribute_key,
                    field="values",
                )
            )

    for attribute in entity.attributes:
        if not attribute.active or attribute.attribute_key == key_attribute:
            continue
        value = row.values.get(attribute.attribute_key)
        if attribute.required and _is_blank(value):
            errors.append(
                _error(
                    "missing_required_value",
                    f"required attribute '{attribute.attribute_key}' is missing",
                    entity_key=row.entity_key,
                    row_key=row.row_key,
                    attribute_key=attribute.attribute_key,
                    field="values",
                )
            )
            continue
        if not _is_blank(value) and not _value_matches_type(value, attribute):
            errors.append(
                _error(
                    "invalid_value_type",
                    f"attribute '{attribute.attribute_key}' must be {attribute.data_type}",
                    entity_key=row.entity_key,
                    row_key=row.row_key,
                    attribute_key=attribute.attribute_key,
                    field="values",
                )
            )


def _value_matches_type(
    value: Any,
    attribute: MappingAttributeDefinition,
) -> bool:
    if attribute.data_type == "string":
        return True
    if attribute.data_type == "number":
        if isinstance(value, (int, float)):
            return not isinstance(value, bool)
        try:
            float(str(value).strip())
        except (TypeError, ValueError):
            return False
        return True
    if attribute.data_type == "boolean":
        if isinstance(value, bool):
            return True
        return _clean(value).lower() in _TRUE_VALUES | _FALSE_VALUES
    return False


def _is_blank(value: Any) -> bool:
    return value is None or (isinstance(value, str) and not value.strip())


def _clean(value: Any) -> str:
    return "" if value is None else str(value).strip()

def _error(
    code: str, message: str, *, entity_key: str = "", attribute_key: str = "",
    row_key: str = "", field: str = "",
) -> MappingValidationError:
    return MappingValidationError(
        code=code, message=message, entity_key=entity_key,
        attribute_key=attribute_key, row_key=row_key, field=field,
    )
