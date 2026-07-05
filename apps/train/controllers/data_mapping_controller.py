"""Controller boundary for the Train Data Mapping panel."""

from __future__ import annotations

from dataclasses import dataclass

from apps.train.services.data_mapping_service import (
    DataMappingAction,
    DataMappingService,
)
from core.mapping.entity_model import (
    MappingAttributeDefinition,
    MappingEntityCatalog,
    MappingEntityDefinition,
    MappingEntityRow,
    MappingValidationError,
)


@dataclass(frozen=True)
class DataMappingEntitySummary:
    """Entity row shown in the Data Mapping entity list."""

    entity_key: str
    label: str
    row_count: int
    active: bool
    notes: str


@dataclass(frozen=True)
class DataMappingAttributeRow:
    """Attribute row shown for the selected entity."""

    attribute_key: str
    label: str
    data_type: str
    required: bool
    active: bool
    notes: str


@dataclass(frozen=True)
class DataMappingValueRow:
    """Row value shown for the selected entity."""

    row_key: str
    values: tuple[str, ...]
    active: bool
    notes: str


@dataclass(frozen=True)
class DataMappingControllerState:
    """UI-facing Data Mapping state."""

    source_label: str
    status: str
    message: str
    selected_entity_key: str
    entities: tuple[DataMappingEntitySummary, ...]
    attributes: tuple[DataMappingAttributeRow, ...]
    value_headers: tuple[str, ...]
    values: tuple[DataMappingValueRow, ...]
    validation_rows: tuple[MappingValidationError, ...]
    actions: tuple[DataMappingAction, ...]


class DataMappingController:
    """Coordinate Data Mapping service calls for the read-only UI."""

    def __init__(self, service: DataMappingService | None = None) -> None:
        self._service = service or DataMappingService()

    def refresh(self, selected_entity_key: str = "") -> DataMappingControllerState:
        """Load the latest read-only Data Mapping state."""
        try:
            snapshot = self._service.load_snapshot()
        except Exception as exc:
            detail = f"Data load failed: {exc}"
            return _error_state(
                "Unable to load data.",
                source_label=_display_source_label(self._service.source_label),
                detail_message=detail,
            )

        catalog = snapshot.catalog
        entities = tuple(_entity_summary(catalog, entity) for entity in catalog.entities)
        selected = _selected_entity(catalog, selected_entity_key)
        attributes = _attribute_rows(selected)
        value_headers = _value_headers(selected)
        values = _value_rows(catalog.rows_for_entity(selected.entity_key), value_headers)
        validation_rows = snapshot.validation_errors
        status = "ready" if snapshot.is_valid else "error"
        message = (
            "Ready."
            if snapshot.is_valid
            else "Issues found."
        )
        return DataMappingControllerState(
            source_label=_display_source_label(snapshot.source_label),
            status=status,
            message=message,
            selected_entity_key=selected.entity_key,
            entities=entities,
            attributes=attributes,
            value_headers=value_headers,
            values=values,
            validation_rows=validation_rows,
            actions=snapshot.actions,
        )


def _entity_summary(
    catalog: MappingEntityCatalog,
    entity: MappingEntityDefinition,
) -> DataMappingEntitySummary:
    return DataMappingEntitySummary(
        entity_key=entity.entity_key,
        label=entity.label,
        row_count=len(catalog.rows_for_entity(entity.entity_key)),
        active=entity.active,
        notes=entity.notes,
    )


def _selected_entity(
    catalog: MappingEntityCatalog,
    selected_entity_key: str,
) -> MappingEntityDefinition:
    selected = catalog.entity_definition(selected_entity_key)
    if selected is not None:
        return selected
    return catalog.entities[0] if catalog.entities else _empty_entity()


def _attribute_rows(
    entity: MappingEntityDefinition,
) -> tuple[DataMappingAttributeRow, ...]:
    return tuple(
        DataMappingAttributeRow(
            attribute.attribute_key,
            attribute.label,
            attribute.data_type,
            attribute.required,
            attribute.active,
            attribute.notes,
        )
        for attribute in entity.attributes
    )


def _value_headers(entity: MappingEntityDefinition) -> tuple[str, ...]:
    key_attribute = entity.key_attribute
    return tuple(
        attribute.attribute_key
        for attribute in entity.attributes
        if attribute.attribute_key != key_attribute
    )


def _value_rows(
    rows: tuple[MappingEntityRow, ...],
    value_headers: tuple[str, ...],
) -> tuple[DataMappingValueRow, ...]:
    return tuple(
        DataMappingValueRow(
            row.row_key,
            tuple(_display_value(row.value_for(header, "")) for header in value_headers),
            row.active,
            row.notes,
        )
        for row in rows
    )


def _display_value(value: object) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    return "" if value is None else str(value)


def _empty_entity() -> MappingEntityDefinition:
    return MappingEntityDefinition("", "", "", ())


def _display_source_label(source_label: str) -> str:
    if not source_label:
        return ""
    known_prefix = "Runtime mapping repository:"
    if source_label.startswith(known_prefix):
        return f"File: {source_label.removeprefix(known_prefix).strip()}"
    return f"File: {source_label}"


def _error_state(
    message: str,
    *,
    source_label: str = "",
    detail_message: str = "",
) -> DataMappingControllerState:
    issue_message = detail_message or message
    return DataMappingControllerState(
        source_label=source_label,
        status="error",
        message=message,
        selected_entity_key="",
        entities=(),
        attributes=(),
        value_headers=(),
        values=(),
        validation_rows=(
            MappingValidationError(
                code="load_failed",
                message=issue_message,
                field="source",
            ),
        ),
        actions=(),
    )
