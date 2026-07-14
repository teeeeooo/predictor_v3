"""Presentation helpers for Data Mapping Manager tables."""

from __future__ import annotations

from apps.train.controllers.data_mapping_controller import DataMappingControllerState

ENTITY_HEADERS = ("Group", "Label", "Rows", "Active", "Notes")
GROUP_HEADERS = ("Group", "Rows")
ATTRIBUTE_HEADERS = ("Field", "Label", "Type", "Required", "Notes")
VALIDATION_HEADERS = ("Level", "Group", "Row", "Field", "Message")


def entity_rows(state: DataMappingControllerState) -> tuple[tuple[str, ...], ...]:
    """Return rows for the entity list table."""
    return tuple(
        (
            entity.entity_key,
            entity.label,
            str(entity.row_count),
            _bool_text(entity.active),
            entity.notes,
        )
        for entity in state.entities
    )


def group_rows(state: DataMappingControllerState) -> tuple[tuple[str, ...], ...]:
    """Return concise user-facing rows for group navigation."""
    return tuple((entity.label, str(entity.row_count)) for entity in state.entities)


def attribute_rows(state: DataMappingControllerState) -> tuple[tuple[str, ...], ...]:
    """Return rows for the selected entity attribute table."""
    return tuple(
        (
            attribute.attribute_key,
            attribute.label,
            attribute.data_type,
            _bool_text(attribute.required),
            attribute.notes,
        )
        for attribute in state.attributes
    )


def value_headers(state: DataMappingControllerState) -> tuple[str, ...]:
    """Return table headers for row data values."""
    return state.value_headers


def value_rows(state: DataMappingControllerState) -> tuple[tuple[str, ...], ...]:
    """Return rows for selected entity row data."""
    return tuple(row.values for row in state.values)


def validation_rows(state: DataMappingControllerState) -> tuple[tuple[str, ...], ...]:
    """Return rows for validation summary."""
    if not state.validation_rows:
        return (("info", "", "", "", "Mapping draft projection OK."),)
    return tuple(
        (
            row.severity,
            row.entity_key,
            row.row_key,
            row.attribute_key,
            row.message,
        )
        for row in state.validation_rows
    )


def _bool_text(value: bool) -> str:
    return "true" if value else "false"
