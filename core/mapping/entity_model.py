"""Qt-free mapping entity and master data model."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True)
class MappingAttributeDefinition:
    """One attribute that belongs to a generic mapping entity."""

    attribute_key: str
    label: str
    data_type: str = "string"
    required: bool = False
    active: bool = True
    notes: str = ""


@dataclass(frozen=True)
class MappingEntityDefinition:
    """Definition for one generic mapping entity."""

    entity_key: str
    label: str
    key_attribute: str
    attributes: tuple[MappingAttributeDefinition, ...] = ()
    active: bool = True
    notes: str = ""

    def attribute(self, attribute_key: str) -> MappingAttributeDefinition | None:
        """Return the first attribute definition with the requested key."""
        return next(
            (
                attribute
                for attribute in self.attributes
                if attribute.attribute_key == attribute_key
            ),
            None,
        )


@dataclass(frozen=True)
class MappingEntityRow:
    """One row of values for a generic mapping entity."""

    entity_key: str
    row_key: str
    values: Mapping[str, Any] = field(default_factory=dict)
    active: bool = True
    notes: str = ""

    def value_for(self, attribute_key: str, default: Any = None) -> Any:
        """Return the value for an attribute key."""
        return self.values.get(attribute_key, default)


@dataclass(frozen=True)
class MappingValidationError:
    """Validation issue reported by mapping entity validators."""

    code: str
    message: str
    entity_key: str = ""
    attribute_key: str = ""
    row_key: str = ""
    field: str = ""
    severity: str = "error"


@dataclass(frozen=True)
class MappingEntityCatalog:
    """Aggregate of generic mapping entity definitions and row data."""

    entities: tuple[MappingEntityDefinition, ...] = ()
    rows: tuple[MappingEntityRow, ...] = ()
    notes: str = ""

    def entity_definition(self, entity_key: str) -> MappingEntityDefinition | None:
        """Return the first entity definition with the requested key."""
        return next(
            (entity for entity in self.entities if entity.entity_key == entity_key),
            None,
        )

    def attribute_definition(
        self,
        entity_key: str,
        attribute_key: str,
    ) -> MappingAttributeDefinition | None:
        """Return the first matching attribute definition."""
        entity = self.entity_definition(entity_key)
        if entity is None:
            return None
        return entity.attribute(attribute_key)

    def rows_for_entity(self, entity_key: str) -> tuple[MappingEntityRow, ...]:
        """Return rows for one entity in stored order."""
        return tuple(row for row in self.rows if row.entity_key == entity_key)

    def row(self, entity_key: str, row_key: str) -> MappingEntityRow | None:
        """Return the first row matching entity and row key."""
        return next(
            (
                row
                for row in self.rows
                if row.entity_key == entity_key and row.row_key == row_key
            ),
            None,
        )

    def value_for(
        self,
        entity_key: str,
        row_key: str,
        attribute_key: str,
        default: Any = None,
    ) -> Any:
        """Return one row value by entity, row key, and attribute key."""
        row = self.row(entity_key, row_key)
        if row is None:
            return default
        return row.value_for(attribute_key, default)
