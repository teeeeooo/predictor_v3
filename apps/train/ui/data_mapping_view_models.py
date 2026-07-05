"""Presentation helpers for the read-only Data Mapping UI foundation."""

from __future__ import annotations

from apps.train.controllers.data_mapping_controller import DataMappingControllerState

ENTITY_HEADERS = ("Group", "Label", "Rows", "Active", "Notes")
ATTRIBUTE_HEADERS = ("Field", "Label", "Type", "Required", "Active", "Notes")
VALIDATION_HEADERS = ("Level", "Code", "Group", "Row", "Field", "Message")


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


def attribute_rows(state: DataMappingControllerState) -> tuple[tuple[str, ...], ...]:
    """Return rows for the selected entity attribute table."""
    return tuple(
        (
            attribute.attribute_key,
            attribute.label,
            attribute.data_type,
            _bool_text(attribute.required),
            _bool_text(attribute.active),
            attribute.notes,
        )
        for attribute in state.attributes
    )


def value_headers(state: DataMappingControllerState) -> tuple[str, ...]:
    """Return table headers for row data values."""
    return ("Row Key", *state.value_headers, "Active", "Notes")


def value_rows(state: DataMappingControllerState) -> tuple[tuple[str, ...], ...]:
    """Return rows for selected entity row data."""
    return tuple(
        (row.row_key, *row.values, _bool_text(row.active), row.notes)
        for row in state.values
    )


def validation_rows(state: DataMappingControllerState) -> tuple[tuple[str, ...], ...]:
    """Return rows for validation summary."""
    if not state.validation_rows:
        return (("info", "ok", "", "", "", "Mapping entity validation OK."),)
    return tuple(
        (
            row.severity,
            row.code,
            row.entity_key,
            row.row_key,
            row.attribute_key,
            row.message,
        )
        for row in state.validation_rows
    )


def _bool_text(value: bool) -> str:
    return "true" if value else "false"
