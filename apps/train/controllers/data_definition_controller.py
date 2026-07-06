"""Controller boundary for the Train Data Definition panel."""

from __future__ import annotations

from dataclasses import dataclass

from apps.train.services.data_definition_service import DataDefinitionService
from core.data_definition import (
    DataDefinitionDraft,
    DataDefinitionDraftRow,
    DataDefinitionIssue,
    DataDefinitionReport,
    DataDefinitionSchemaSaveResult,
    DataDefinitionSavePlan,
    field_editability,
)

DRAFT_FIELDS = (
    "source_kind",
    "display_order",
    "column_key",
    "label",
    "role",
    "editor",
    "data_type",
    "visible",
    "required",
    "readonly",
    "value_source",
    "mapping_entity",
    "mapping_attribute",
    "trigger_column",
    "rule_id",
    "model_input_enabled",
    "ml_name",
    "one_hot_group",
    "active",
    "notes",
)
DRAFT_HEADERS = (
    "Source",
    "Order",
    "Column Key",
    "Label",
    "Role",
    "Editor",
    "Data Type",
    "Visible",
    "Required",
    "Readonly",
    "Value Source",
    "Mapping Entity",
    "Mapping Attribute",
    "Trigger Column",
    "Rule ID",
    "Model Input",
    "ML Name",
    "One-hot Group",
    "Active",
    "Notes",
)


@dataclass(frozen=True)
class DataDefinitionDraftCellState:
    """UI-facing editability and change state for one draft cell."""

    field_name: str
    value: str
    editable: bool
    reason: str
    changed: bool


@dataclass(frozen=True)
class DataDefinitionControllerState:
    """UI-facing Data Definition state."""

    status: str
    message: str
    summary_rows: tuple[tuple[str, str], ...]
    draft_headers: tuple[str, ...]
    draft_rows: tuple[tuple[DataDefinitionDraftCellState, ...], ...]
    draft_row_identities: tuple[tuple[str, str], ...]
    draft_changed: bool
    can_save_schema: bool
    save_plan_rows: tuple[tuple[str, ...], ...]
    save_blocker_rows: tuple[tuple[str, ...], ...]
    save_result_rows: tuple[tuple[str, str], ...]
    draft_change_rows: tuple[tuple[str, ...], ...]
    projected_feature_rows: tuple[tuple[str, ...], ...]
    mapping_requirement_rows: tuple[tuple[str, ...], ...]
    one_hot_rows: tuple[tuple[str, ...], ...]
    readiness_rows: tuple[tuple[str, ...], ...]
    issue_rows: tuple[tuple[str, ...], ...]
    last_action_ok: bool = True


class DataDefinitionController:
    """Coordinate Data Definition report and draft refresh for the UI."""

    def __init__(self, service: DataDefinitionService | None = None) -> None:
        self._service = service or DataDefinitionService()
        self._draft: DataDefinitionDraft | None = None

    def refresh(self) -> DataDefinitionControllerState:
        """Return current Data Definition view state and reload the draft."""
        try:
            report = self._service.refresh_report()
            self._draft = self._service.refresh_draft()
        except Exception as exc:
            return _error_state(exc)
        return _state_from_report(
            report,
            self._draft,
            self._service.preview_save_plan(self._draft, current_report=report),
        )

    def edit_cell(
        self,
        row_identity: tuple[str, str],
        field_name: str,
        value: object,
    ) -> DataDefinitionControllerState:
        """Apply one draft edit and return refreshed preview state."""
        try:
            draft = self._draft or self._service.load_draft()
            result = self._service.edit_draft_cell(draft, row_identity, field_name, value)
            self._draft = result.draft
            report = self._service.refresh_report()
            state = _state_from_report(
                report,
                self._draft,
                self._service.preview_save_plan(self._draft, current_report=report),
                message=result.message,
                status="draft_changed" if result.accepted and self._draft.is_changed else None,
                last_action_ok=result.accepted,
            )
        except Exception as exc:
            return _error_state(exc)
        return state

    def reset_draft(self) -> DataDefinitionControllerState:
        """Discard in-memory edits and reload draft state from the service."""
        try:
            report = self._service.refresh_report()
            self._draft = self._service.refresh_draft()
        except Exception as exc:
            return _error_state(exc)
        return _state_from_report(
            report,
            self._draft,
            self._service.preview_save_plan(self._draft, current_report=report),
            message="Draft reset from schema.",
        )

    def save_schema(self) -> DataDefinitionControllerState:
        """Run the guarded schema save workflow and return updated UI state."""
        try:
            draft = self._draft or self._service.load_draft()
            report_before = self._service.refresh_report()
            result = self._service.save_schema_draft(draft, current_report=report_before)
            if result.status == "written":
                self._draft = self._service.refresh_draft()
            else:
                self._draft = draft
            report_after = self._service.refresh_report()
            plan = self._service.preview_save_plan(self._draft, current_report=report_after)
        except Exception as exc:
            return _error_state(exc)
        return _state_from_report(
            report_after,
            self._draft,
            plan,
            message=result.message,
            status=_save_status(result),
            save_result=result,
            last_action_ok=result.status in {"written", "noop"},
        )


def _state_from_report(
    report: DataDefinitionReport,
    draft: DataDefinitionDraft,
    save_plan: DataDefinitionSavePlan,
    *,
    message: str | None = None,
    status: str | None = None,
    save_result: DataDefinitionSchemaSaveResult | None = None,
    last_action_ok: bool = True,
) -> DataDefinitionControllerState:
    parity_count = len(report.parity_issues)
    issue_count = len([issue for issue in report.issues if issue.severity == "error"])
    resolved_status = status or ("ready" if report.ok else "error")
    resolved_message = message or (
        "Data Definition report ready." if report.ok else "Data Definition issues found."
    )
    summary_rows = (
        ("Status", "OK" if report.ok else "Issues"),
        ("Projected features", str(len(report.projected_features))),
        ("Current catalog features", str(len(report.catalog_features))),
        ("Parity issues", str(parity_count)),
        ("Mapping requirements", str(len(report.mapping_requirements))),
        ("One-hot relationships", str(len(report.one_hot_relationships))),
        ("Readiness", _readiness_summary(report)),
        ("Draft changes", str(len(save_plan.changed_fields))),
        ("Schema save preview", "Allowed" if save_plan.can_save_schema else "Not allowed"),
        ("Impact", save_plan.restart_impact.message),
        ("Error issues", str(issue_count)),
    )
    return DataDefinitionControllerState(
        status=resolved_status,
        message=resolved_message,
        summary_rows=summary_rows,
        draft_headers=DRAFT_HEADERS,
        draft_rows=_draft_rows(draft),
        draft_row_identities=tuple(row.identity for row in draft.rows),
        draft_changed=draft.is_changed,
        can_save_schema=save_plan.can_save_schema,
        save_plan_rows=tuple(
            (target.target, target.status, target.reason)
            for target in save_plan.planned_targets
        ),
        save_blocker_rows=_save_blocker_rows(save_plan),
        save_result_rows=_save_result_rows(save_result),
        draft_change_rows=_draft_change_rows(save_plan),
        projected_feature_rows=tuple(
            (
                str(row.order),
                row.role,
                row.ml_name,
                row.ui_key,
                row.label,
                row.source,
                row.mapping_key,
                row.one_hot_group,
                row.zero_fill_policy,
                str(row.active).lower(),
            )
            for row in report.projected_features
        ),
        mapping_requirement_rows=tuple(
            (
                row.column_key,
                row.ml_name,
                row.mapping_entity,
                row.mapping_attribute,
                row.trigger_column,
                row.rule_id,
            )
            for row in report.mapping_requirements
        ),
        one_hot_rows=tuple(
            (
                row.selector_column,
                row.one_hot_group,
                ", ".join(row.emitted_ml_names),
                ", ".join(row.catalog_ml_names),
                "OK" if row.emitted_ml_names == row.catalog_ml_names else "Mismatch",
            )
            for row in report.one_hot_relationships
        ),
        readiness_rows=tuple(
            (row.name, row.status, row.message)
            for row in report.readiness
        ),
        issue_rows=_issue_rows(report.issues),
        last_action_ok=last_action_ok,
    )


def _draft_rows(
    draft: DataDefinitionDraft,
) -> tuple[tuple[DataDefinitionDraftCellState, ...], ...]:
    changed_by_identity: dict[tuple[str, str], set[str]] = {}
    for change in draft.changes():
        changed_by_identity.setdefault(change.row_identity, set()).add(change.field_name)
    return tuple(
        _draft_row(row, changed_by_identity.get(row.identity, set()))
        for row in draft.rows
    )


def _draft_row(
    row: DataDefinitionDraftRow,
    changed_fields: set[str],
) -> tuple[DataDefinitionDraftCellState, ...]:
    cells: list[DataDefinitionDraftCellState] = []
    for field_name in DRAFT_FIELDS:
        editability = field_editability(row, field_name)
        cells.append(
            DataDefinitionDraftCellState(
                field_name=field_name,
                value=_display_value(getattr(row, field_name)),
                editable=editability.editable,
                reason=editability.reason,
                changed=field_name in changed_fields,
            )
        )
    return tuple(cells)


def _display_value(value: object) -> str:
    if isinstance(value, bool):
        return str(value).lower()
    return "" if value is None else str(value)


def _save_blocker_rows(
    save_plan: DataDefinitionSavePlan,
) -> tuple[tuple[str, ...], ...]:
    if not save_plan.blocked_reasons:
        return (("info", "no_blockers", "", "No save blockers."),)
    return tuple(
        (blocker.severity, blocker.code, blocker.target, blocker.message)
        for blocker in save_plan.blocked_reasons
    )


def _draft_change_rows(
    save_plan: DataDefinitionSavePlan,
) -> tuple[tuple[str, ...], ...]:
    if not save_plan.changed_fields:
        return (("info", "", "", "", "No draft changes."),)
    return tuple(
        (
            change.row_identity[0],
            change.row_identity[1],
            change.field_name,
            _display_value(change.before),
            _display_value(change.after),
        )
        for change in save_plan.changed_fields
    )


def _save_result_rows(
    result: DataDefinitionSchemaSaveResult | None,
) -> tuple[tuple[str, str], ...]:
    if result is None:
        return (("Status", "No save attempted."),)
    return (
        ("Status", result.status),
        ("Success", str(result.success).lower()),
        ("Message", result.message),
        ("Rows written", str(result.rows_written)),
        ("Path", str(result.path or "")),
        ("Backup", str(result.backup_path or "")),
        ("Issues", ", ".join(issue.code for issue in result.issues) or "none"),
    )


def _save_status(result: DataDefinitionSchemaSaveResult) -> str:
    if result.status == "written":
        return "saved"
    if result.status == "noop":
        return "ready"
    return result.status


def _issue_rows(
    issues: tuple[DataDefinitionIssue, ...],
) -> tuple[tuple[str, ...], ...]:
    if not issues:
        return (("info", "no_issues", "", "No Data Definition issues."),)
    return tuple(
        (issue.severity, issue.code, issue.subject, issue.message)
        for issue in issues
    )


def _readiness_summary(report: DataDefinitionReport) -> str:
    counts: dict[str, int] = {}
    for check in report.readiness:
        counts[check.status] = counts.get(check.status, 0) + 1
    return ", ".join(f"{status}: {count}" for status, count in sorted(counts.items()))


def _error_state(exc: Exception) -> DataDefinitionControllerState:
    return DataDefinitionControllerState(
        status="error",
        message=f"Data Definition report failed: {exc}",
        summary_rows=(("Status", "Error"),),
        draft_headers=DRAFT_HEADERS,
        draft_rows=(),
        draft_row_identities=(),
        draft_changed=False,
        can_save_schema=False,
        save_plan_rows=(),
        save_blocker_rows=(("error", "load_failed", "Data Definition", str(exc)),),
        save_result_rows=(("Status", "Error"), ("Message", str(exc))),
        draft_change_rows=(),
        projected_feature_rows=(),
        mapping_requirement_rows=(),
        one_hot_rows=(),
        readiness_rows=(),
        issue_rows=(("error", "load_failed", "Data Definition", str(exc)),),
        last_action_ok=False,
    )
