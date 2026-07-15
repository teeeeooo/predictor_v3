"""Pure snapshot-to-presentation projection for Data Mapping."""

from __future__ import annotations

from dataclasses import dataclass

from apps.train.application.data_mapping import (
    DataMappingCoverageItem,
    DataMappingIssueTarget,
)
from apps.train.application.data_mapping.coverage import project_mapping_coverage
from apps.train.services.data_mapping_types import DataMappingAction, DataMappingSnapshot
from core.mapping.condenser_identity import condenser_requires_pi
from core.mapping.editor_model import MappingEditorGroup, MappingEditorRow
from core.mapping.entity_model import MappingValidationError
from core.mapping.value_policy import mapping_column_data_type


@dataclass(frozen=True)
class DataMappingEntitySummary:
    entity_key: str
    label: str
    row_count: int
    active: bool
    notes: str


@dataclass(frozen=True)
class DataMappingAttributeRow:
    attribute_key: str
    label: str
    data_type: str
    required: bool
    notes: str


@dataclass(frozen=True)
class DataMappingValueRow:
    row_key: str
    values: tuple[str, ...]
    notes: str


@dataclass(frozen=True)
class DataMappingControllerState:
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
    resource_status: str = "available"
    read_only_cells: frozenset[tuple[int, int]] = frozenset()
    operation_applied: int = 0
    operation_blocked: int = 0
    issue_targets: tuple[DataMappingIssueTarget | None, ...] = ()
    invalid_cells: frozenset[tuple[int, int]] = frozenset()
    coverage_items: tuple[DataMappingCoverageItem, ...] = ()


def project_snapshot(
    snapshot: DataMappingSnapshot,
    selected_group_key: str,
    *,
    resource_status: str,
    status: str | None = None,
    message: str | None = None,
    extra_issues: tuple[MappingValidationError, ...] = (),
    operation_applied: int = 0,
    operation_blocked: int = 0,
) -> DataMappingControllerState:
    """Project one application snapshot into stable UI-facing rows."""
    draft = snapshot.draft
    entities = tuple(_entity_summary(group) for group in draft.groups)
    selected = _selected_group(draft.groups, selected_group_key)
    resource_issues = (_resource_missing_issue(),) if resource_status == "missing" else ()
    issues = (*snapshot.validation_errors, *resource_issues, *extra_issues)
    targets = tuple(_issue_target(draft.groups, issue) for issue in issues)
    coverage = project_mapping_coverage(
        snapshot.mapping_requirements,
        draft,
        issues,
        targets,
    )
    return DataMappingControllerState(
        source_label=display_source_label(snapshot.source_label),
        status=status or _snapshot_status(snapshot.is_valid, resource_status),
        message=message or _status_message(snapshot.is_valid, snapshot.dirty, resource_status),
        selected_group_key=selected.group_key,
        entities=entities,
        attributes=_attribute_rows(selected),
        value_headers=selected.columns,
        values=_value_rows(selected.rows, selected.columns),
        validation_rows=issues,
        actions=snapshot.actions,
        dirty=snapshot.dirty,
        resource_status=resource_status,
        read_only_cells=_read_only_cells(selected),
        operation_applied=operation_applied,
        operation_blocked=operation_blocked,
        issue_targets=targets,
        invalid_cells=frozenset(
            (target.row_index, target.column_index)
            for issue, target in zip(issues, targets)
            if issue.severity == "error"
            and target is not None
            and target.group_key == selected.group_key
            and target.row_index is not None
            and target.column_index is not None
        ),
        coverage_items=coverage,
    )


def operation_issue(code: str, group: str, field: str, message: str) -> MappingValidationError:
    return MappingValidationError(
        code=code,
        message=message or f"{group} failed.",
        entity_key=group,
        attribute_key=field,
        field=field,
    )


def exception_summary(exc: Exception) -> str:
    for line in str(exc).splitlines():
        summary = line.strip()
        if summary:
            return summary
    return type(exc).__name__ or "Unknown error"


def display_source_label(source_label: str) -> str:
    if not source_label:
        return ""
    known_prefix = "Runtime mapping repository:"
    if source_label.startswith(known_prefix):
        return f"File: {source_label.removeprefix(known_prefix).strip()}"
    return f"File: {source_label}"


def error_state(
    message: str,
    *,
    source_label: str = "",
    detail_message: str = "",
) -> DataMappingControllerState:
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
                message=detail_message or message,
                field="source",
            ),
        ),
        actions=(
            DataMappingAction(
                "reload_runtime",
                "Reload",
                True,
                "Read the mapping source again.",
            ),
        ),
        resource_status="load-error",
    )


def missing_state(*, source_label: str) -> DataMappingControllerState:
    return DataMappingControllerState(
        source_label=source_label,
        status="missing",
        message="Mapping resource not found.",
        selected_group_key="",
        entities=(),
        attributes=(),
        value_headers=(),
        values=(),
        validation_rows=(
            MappingValidationError(
                code="resource_missing",
                message="The configured mapping file does not exist.",
                field="source",
            ),
        ),
        actions=(
            DataMappingAction(
                "reload_runtime",
                "Reload",
                True,
                "Read the mapping source again.",
            ),
        ),
        resource_status="missing",
    )


def _entity_summary(group: MappingEditorGroup) -> DataMappingEntitySummary:
    return DataMappingEntitySummary(group.group_key, group.label, len(group.rows), True, group.notes)


def _selected_group(
    groups: tuple[MappingEditorGroup, ...],
    selected_group_key: str,
) -> MappingEditorGroup:
    selected = next((group for group in groups if group.group_key == selected_group_key), None)
    return selected or (groups[0] if groups else MappingEditorGroup("", "", ()))


def _attribute_rows(group: MappingEditorGroup) -> tuple[DataMappingAttributeRow, ...]:
    required_columns = set(group.required_columns)
    return tuple(
        DataMappingAttributeRow(
            column,
            column,
            mapping_column_data_type(group, column),
            column == group.columns[0] or column in required_columns,
            "Required by Data Definition." if column in required_columns else "",
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


def _read_only_cells(group: MappingEditorGroup) -> frozenset[tuple[int, int]]:
    if group.group_key != "odu_cond_specs" or "Pi" not in group.columns:
        return frozenset()
    pi_column = group.columns.index("Pi")
    return frozenset(
        (row_index, pi_column)
        for row_index, row in enumerate(group.rows)
        if not condenser_requires_pi(row.value_for("Fin Type"))
    )


def _issue_target(
    groups: tuple[MappingEditorGroup, ...],
    issue: MappingValidationError,
) -> DataMappingIssueTarget | None:
    if issue.field in {"source", "file"} or issue.code in {
        "load_failed",
        "reload_failed",
        "save_failed",
        "resource_missing",
    }:
        return None
    group = next(
        (
            candidate
            for candidate in groups
            if issue.entity_key in {candidate.group_key, candidate.label}
        ),
        None,
    )
    if group is None:
        return None
    field = issue.field or issue.attribute_key
    column_index = group.columns.index(field) if field in group.columns else None
    row_index = issue.row_index
    if row_index is None and issue.row_key:
        row_index = next(
            (
                index
                for index, row in enumerate(group.rows)
                if row.source_key == issue.row_key
            ),
            None,
        )
    if row_index is not None and not 0 <= row_index < len(group.rows):
        row_index = None
    if row_index is None and column_index is not None and group.rows:
        row_index = 0
    row_key = ""
    if row_index is not None and 0 <= row_index < len(group.rows):
        row_key = group.rows[row_index].source_key
    return DataMappingIssueTarget(
        group.group_key,
        row_key,
        field,
        row_index,
        column_index,
    )


def _status_message(is_valid: bool, dirty: bool, resource_status: str) -> str:
    message = "Issues found." if not is_valid else ("Unsaved changes." if dirty else "Ready.")
    return f"{message} Source missing." if resource_status == "missing" else message


def _snapshot_status(is_valid: bool, resource_status: str) -> str:
    if not is_valid:
        return "error"
    return "warning" if resource_status == "missing" else "ready"


def _resource_missing_issue() -> MappingValidationError:
    return MappingValidationError(
        code="resource_missing",
        message="The mapping source is missing; the current in-memory draft is preserved.",
        field="source",
        severity="warning",
    )
