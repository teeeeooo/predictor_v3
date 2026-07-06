"""Controller boundary for the Train Data Mapping panel."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from apps.train.services.data_mapping_service import DataMappingService
from apps.train.services.data_mapping_types import DataMappingAction, DataMappingSnapshot
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
    dirty: bool = False


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
        message = _status_message(snapshot.is_valid, snapshot.dirty)
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
            dirty=snapshot.dirty,
        )

    def edit_cell(
        self,
        group_key: str,
        row_index: int,
        column: str,
        value: object,
    ) -> DataMappingControllerState:
        """Apply one cell edit and return refreshed state."""
        snapshot = self._service.edit_cell(group_key, row_index, column, value)
        return self._state_from_snapshot(snapshot, group_key)

    def add_row(self, group_key: str) -> DataMappingControllerState:
        """Add one blank row and return refreshed state."""
        return self._state_from_snapshot(self._service.add_row(group_key), group_key)

    def duplicate_row(self, group_key: str, row_index: int) -> DataMappingControllerState:
        """Duplicate one row and return refreshed state."""
        return self._state_from_snapshot(
            self._service.duplicate_row(group_key, row_index),
            group_key,
        )

    def delete_row(self, group_key: str, row_index: int) -> DataMappingControllerState:
        """Delete one row and return refreshed state."""
        return self._state_from_snapshot(self._service.delete_row(group_key, row_index), group_key)

    def reload(self) -> DataMappingControllerState:
        """Discard draft edits and reload from the provider."""
        return self._state_from_snapshot(self._service.reload_snapshot(), "")

    def save(self) -> DataMappingControllerState:
        """Save the current draft and return refreshed state."""
        result, snapshot = self._service.save_mapping()
        if result.success:
            return self._state_from_snapshot(snapshot, "", message="Saved.")
        return self._state_from_snapshot(
            snapshot,
            "",
            status="error",
            message="Save failed.",
            extra_issues=(_operation_issue("save_failed", "Save", "file", result.message),),
        )

    def export_json(self, destination: str | Path) -> DataMappingControllerState:
        """Export the current draft as JSON and return current state."""
        return self.export_snapshot(destination, "json")

    def export_xlsx(self, destination: str | Path) -> DataMappingControllerState:
        """Export the current draft as XLSX and return current state."""
        return self.export_snapshot(destination, "xlsx")

    def export_snapshot(
        self,
        destination: str | Path,
        export_format: str,
    ) -> DataMappingControllerState:
        """Export the current draft in the requested review snapshot format."""
        result, snapshot = self._service.export_snapshot(destination, export_format)
        selected = snapshot.draft.groups[0].group_key if snapshot.draft.groups else ""
        if result.success:
            return self._state_from_snapshot(snapshot, selected, message="Exported.")
        return self._state_from_snapshot(
            snapshot,
            selected,
            status="error",
            message="Export failed.",
            extra_issues=(
                _operation_issue("export_failed", "Export", "file", result.message),
            ),
        )

    def _state_from_snapshot(
        self,
        snapshot: DataMappingSnapshot,
        selected_group_key: str,
        *,
        status: str | None = None,
        message: str | None = None,
        extra_issues: tuple[MappingValidationError, ...] = (),
    ) -> DataMappingControllerState:
        draft = snapshot.draft
        entities = tuple(_entity_summary(group) for group in draft.groups)
        selected = _selected_group(draft.groups, selected_group_key)
        attributes = _attribute_rows(selected)
        value_headers = selected.columns
        values = _value_rows(selected.rows, value_headers)
        resolved_status = status or ("ready" if snapshot.is_valid else "error")
        return DataMappingControllerState(
            source_label=_display_source_label(snapshot.source_label),
            status=resolved_status,
            message=message or _status_message(snapshot.is_valid, snapshot.dirty),
            selected_group_key=selected.group_key,
            entities=entities,
            attributes=attributes,
            value_headers=value_headers,
            values=values,
            validation_rows=(*snapshot.validation_errors, *extra_issues),
            actions=snapshot.actions,
            dirty=snapshot.dirty,
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


def _operation_issue(
    code: str,
    group: str,
    field: str,
    message: str,
) -> MappingValidationError:
    return MappingValidationError(
        code=code,
        message=message or f"{group} failed.",
        entity_key=group,
        attribute_key=field,
        field=field,
    )


def _status_message(is_valid: bool, dirty: bool) -> str:
    if not is_valid:
        return "Issues found."
    if dirty:
        return "Unsaved changes."
    return "Ready."


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
        dirty=False,
    )
