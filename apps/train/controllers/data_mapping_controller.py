"""Controller boundary for the Train Data Mapping panel."""

from __future__ import annotations

from dataclasses import dataclass

from apps.train.services.data_mapping_service import (
    DataMappingAction,
    DataMappingService,
)
from core.mapping.editor_model import MappingEditorGroup, MappingEditorRow
from core.mapping.entity_model import MappingValidationError


@dataclass(frozen=True)
class DataMappingEntitySummary:
    """Group row shown in the Data Mapping group list."""

    entity_key: str
    label: str
    row_count: int
    active: bool
    notes: str


@dataclass(frozen=True)
class DataMappingAttributeRow:
    """Field row shown for the selected group."""

    attribute_key: str
    label: str
    data_type: str
    required: bool
    notes: str


@dataclass(frozen=True)
class DataMappingValueRow:
    """Row value shown for the selected group."""

    row_key: str
    values: tuple[str, ...]
    notes: str


@dataclass(frozen=True)
class DataMappingControllerState:
    """UI-facing Data Mapping state."""

    source_label: str
    status: str
    message: str
    selected_group_key: str
    entities: tuple[DataMappingEntitySummary, ...]
    attributes: tuple[DataMappingAttributeRow, ...]
    value_headers: tuple[str, ...]
    values: tuple[DataMappingValueRow, ...]
    validation_rows: tuple[MappingValidationError, ...]
    actions: tuple[DataMappingAction, ...]


class DataMappingController:
    """Coordinate Data Mapping service calls for the UI."""

    def __init__(self, service: DataMappingService | None = None) -> None:
        self._service = service or DataMappingService()

    def refresh(self, selected_entity_key: str = "") -> DataMappingControllerState:
        """Load the latest Data Mapping state."""
        try:
            snapshot = self._service.load_snapshot()
        except Exception as exc:
            detail = f"Data load failed: {exc}"
            return _error_state(
                "Unable to load data.",
                source_label=_display_source_label(self._service.source_label),
                detail_message=detail,
            )

        draft = snapshot.draft
        entities = tuple(_entity_summary(group) for group in draft.groups)
        selected = _selected_group(draft.groups, selected_entity_key)
        attributes = _attribute_rows(selected)
        value_headers = selected.columns
        values = _value_rows(selected.rows, value_headers)
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
            selected_group_key=selected.group_key,
            entities=entities,
            attributes=attributes,
            value_headers=value_headers,
            values=values,
            validation_rows=validation_rows,
            actions=snapshot.actions,
        )


def _entity_summary(
    group: MappingEditorGroup,
) -> DataMappingEntitySummary:
    return DataMappingEntitySummary(
        entity_key=group.group_key,
        label=group.label,
        row_count=len(group.rows),
        active=True,
        notes=group.notes,
    )


def _selected_group(
    groups: tuple[MappingEditorGroup, ...],
    selected_group_key: str,
) -> MappingEditorGroup:
    selected = next((group for group in groups if group.group_key == selected_group_key), None)
    if selected is not None:
        return selected
    return groups[0] if groups else _empty_group()


def _attribute_rows(
    group: MappingEditorGroup,
) -> tuple[DataMappingAttributeRow, ...]:
    return tuple(
        DataMappingAttributeRow(
            column,
            column,
            "string",
            column == group.columns[0],
            "",
        )
        for column in group.columns
    )


def _value_rows(
    rows: tuple[MappingEditorRow, ...],
    value_headers: tuple[str, ...],
) -> tuple[DataMappingValueRow, ...]:
    return tuple(
        DataMappingValueRow(
            row.source_key,
            tuple(_display_value(row.value_for(header, "")) for header in value_headers),
            row.notes,
        )
        for row in rows
    )


def _display_value(value: object) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    return "" if value is None else str(value)


def _empty_group() -> MappingEditorGroup:
    return MappingEditorGroup("", "", ())


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
        selected_group_key="",
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
