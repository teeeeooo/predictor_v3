"""Pure UI-facing state composition for the Train Data Definition controller."""

from __future__ import annotations

from dataclasses import dataclass

from core.data_definition import (
    DataDefinitionDraft,
    DataDefinitionDraftRow,
    DataDefinitionIssue,
    DataDefinitionReport,
    DataDefinitionSaveBlocker,
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
class DataDefinitionBlockerItem:
    """Structured UI-facing blocker evidence before selection relevance."""

    severity: str
    code: str
    target: str
    message: str
    related_row_identity: tuple[str, str] | None
    related_field: str
    source: str


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
    save_action_enabled: bool
    save_plan_rows: tuple[tuple[str, ...], ...]
    save_blocker_rows: tuple[tuple[str, ...], ...]
    save_result_rows: tuple[tuple[str, str], ...]
    save_result_issue_rows: tuple[tuple[str, ...], ...]
    blocker_items: tuple[DataDefinitionBlockerItem, ...]
    draft_change_rows: tuple[tuple[str, ...], ...]
    projected_feature_rows: tuple[tuple[str, ...], ...]
    mapping_requirement_rows: tuple[tuple[str, ...], ...]
    one_hot_rows: tuple[tuple[str, ...], ...]
    readiness_rows: tuple[tuple[str, ...], ...]
    issue_rows: tuple[tuple[str, ...], ...]
    requires_restart: bool
    requires_retrain: bool
    impact_summary: str
    last_action_ok: bool = True


def state_from_report(
    report: DataDefinitionReport,
    draft: DataDefinitionDraft,
    save_plan: DataDefinitionSavePlan,
    *,
    message: str | None = None,
    status: str | None = None,
    save_result: DataDefinitionSchemaSaveResult | None = None,
    last_action_ok: bool = True,
) -> DataDefinitionControllerState:
    """Compose immutable UI-facing state from report, draft, and save plan data."""
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
        save_action_enabled=(
            draft.is_changed
            and save_plan.can_save_schema
            and (save_result is None or save_result.status != "blocked")
        ),
        save_plan_rows=tuple(
            (target.target, target.status, target.reason)
            for target in save_plan.planned_targets
        ),
        save_blocker_rows=_save_blocker_rows(save_plan),
        save_result_rows=_save_result_rows(save_result),
        save_result_issue_rows=_save_result_issue_rows(save_result),
        blocker_items=_blocker_items(save_plan, save_result),
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
        requires_restart=save_plan.requires_restart,
        requires_retrain=save_plan.requires_retrain,
        impact_summary=save_plan.restart_impact.message,
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


def _save_result_issue_rows(
    result: DataDefinitionSchemaSaveResult | None,
) -> tuple[tuple[str, ...], ...]:
    if result is None:
        return ()
    return tuple(
        (issue.severity, issue.code, issue.target, issue.message)
        for issue in result.issues
    )


def _blocker_items(
    save_plan: DataDefinitionSavePlan,
    result: DataDefinitionSchemaSaveResult | None,
) -> tuple[DataDefinitionBlockerItem, ...]:
    items = [
        _blocker_item(blocker, "save_plan")
        for blocker in save_plan.blocked_reasons
    ]
    if result is not None:
        items.extend(
            _blocker_item(blocker, "last_save_result")
            for blocker in result.issues
        )
    return tuple(items)


def _blocker_item(
    blocker: DataDefinitionSaveBlocker,
    source: str,
) -> DataDefinitionBlockerItem:
    return DataDefinitionBlockerItem(
        severity=blocker.severity,
        code=blocker.code,
        target=blocker.target,
        message=blocker.message,
        related_row_identity=blocker.row_identity,
        related_field=blocker.field_name,
        source=source,
    )


def save_status(result: DataDefinitionSchemaSaveResult) -> str:
    """Map a schema-save result to the existing controller status string."""
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


def error_state(exc: Exception) -> DataDefinitionControllerState:
    """Return the existing controller error-state projection."""
    return DataDefinitionControllerState(
        status="error",
        message=f"Data Definition report failed: {exc}",
        summary_rows=(("Status", "Error"),),
        draft_headers=DRAFT_HEADERS,
        draft_rows=(),
        draft_row_identities=(),
        draft_changed=False,
        can_save_schema=False,
        save_action_enabled=False,
        save_plan_rows=(),
        save_blocker_rows=(("error", "load_failed", "Data Definition", str(exc)),),
        save_result_rows=(("Status", "Error"), ("Message", str(exc))),
        save_result_issue_rows=(),
        blocker_items=(DataDefinitionBlockerItem(
            "error", "load_failed", "Data Definition", str(exc), None, "", "save_plan",
        ),),
        draft_change_rows=(),
        projected_feature_rows=(),
        mapping_requirement_rows=(),
        one_hot_rows=(),
        readiness_rows=(),
        issue_rows=(("error", "load_failed", "Data Definition", str(exc)),),
        requires_restart=False,
        requires_retrain=False,
        impact_summary="Impact unavailable because Data Definition failed to load.",
        last_action_ok=False,
    )
