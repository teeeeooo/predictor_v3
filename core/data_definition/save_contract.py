"""Save contract and in-memory save plan for Data Definition drafts."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from core.data_definition.draft import (
    DataDefinitionDraft,
    DataDefinitionDraftChange,
    replace_draft_row,
)
from core.data_definition.edit_policy import restricted_draft_field_changes
from core.data_definition.projection import (
    project_feature_catalog_from_draft,
    projected_feature_catalog_fingerprint,
)
from core.data_definition.report_model import DataDefinitionReport
from core.data_definition.validation import (
    DataDefinitionCandidateIssue,
    build_data_definition_report,
    validate_data_definition_candidate,
)

BlockerSeverity = Literal["error", "warning", "info"]
WriteTargetStatus = Literal["planned", "blocked", "deferred", "no_op"]

SCHEMA_CHANGE_FIELDS = frozenset(
    {
        "label", "editor", "data_type", "visible", "required", "readonly",
        "value_source", "mapping_entity", "mapping_attribute", "trigger_column",
        "rule_id", "model_input_enabled", "ml_name", "one_hot_group", "active",
        "notes", "column_key", "display_order", "role",
    }
)
RETRAIN_FIELDS = frozenset({"model_input_enabled", "ml_name", "value_source"})
MAPPING_REQUIREMENT_FIELDS = frozenset(
    {"mapping_entity", "mapping_attribute", "trigger_column", "rule_id"}
)
ONE_HOT_FIELDS = frozenset({"one_hot_group", "value_source"})
_BASIC_SCHEMA_ISSUE_CODES = frozenset(
    {"data_type_invalid", "editor_invalid", "value_source_invalid"}
)
_PARITY_ISSUE_CODES = frozenset(
    {"catalog_orphan", "projection_extra", "feature_projection_mismatch"}
)


@dataclass(frozen=True)
class DataDefinitionWriteTarget:
    target: str
    status: WriteTargetStatus
    reason: str


@dataclass(frozen=True)
class DataDefinitionSaveBlocker:
    code: str
    severity: BlockerSeverity
    message: str
    target: str = ""
    row_identity: tuple[str, str] | None = None
    field_name: str = ""


@dataclass(frozen=True)
class DataDefinitionRestartImpact:
    requires_restart: bool
    requires_retrain: bool
    message: str


@dataclass(frozen=True)
class DataDefinitionSavePlan:
    can_save_schema: bool
    can_write_features_projection: bool
    can_write_derived_policy: bool
    requires_restart: bool
    requires_retrain: bool
    changed_fields: tuple[DataDefinitionDraftChange, ...]
    planned_targets: tuple[DataDefinitionWriteTarget, ...]
    blocked_reasons: tuple[DataDefinitionSaveBlocker, ...]
    restart_impact: DataDefinitionRestartImpact


def build_data_definition_save_plan(
    draft: DataDefinitionDraft,
    *,
    current_report: DataDefinitionReport | None = None,
    requested_targets: tuple[str, ...] = (),
) -> DataDefinitionSavePlan:
    """Build an in-memory save plan without writing files."""
    report = current_report or build_data_definition_report()
    changes = draft.attributed_changes()
    projection_blockers = _candidate_projection_blockers(draft, report)
    blockers = [
        *_report_blockers(report),
        *projection_blockers,
        *_candidate_data_definition_blockers(draft, report, projection_blockers),
        *_change_blockers(draft, changes),
        *_requested_target_blockers(requested_targets),
    ]
    requires_restart = _requires_restart(draft, changes)
    requires_retrain = _requires_retrain(changes)
    can_save_schema = any(_is_schema_change(draft, change) for change in changes) and not any(
        blocker.severity == "error" and blocker.target in {"schema_csv", ""}
        for blocker in blockers
    )
    targets = _write_targets(draft, changes, blockers, requested_targets)
    return DataDefinitionSavePlan(
        can_save_schema=can_save_schema,
        can_write_features_projection=False,
        can_write_derived_policy=False,
        requires_restart=requires_restart,
        requires_retrain=requires_retrain,
        changed_fields=changes,
        planned_targets=targets,
        blocked_reasons=tuple(blockers),
        restart_impact=DataDefinitionRestartImpact(
            requires_restart=requires_restart,
            requires_retrain=requires_retrain,
            message=_impact_message(requires_restart, requires_retrain),
        ),
    )


def _report_blockers(report: DataDefinitionReport) -> tuple[DataDefinitionSaveBlocker, ...]:
    blockers: list[DataDefinitionSaveBlocker] = []
    if any(issue.severity == "error" and issue.code == "schema_shape" for issue in report.issues):
        blockers.append(_blocker(
            "schema_validation_error", "error",
            "Current schema validation must pass before save.", "schema_csv",
        ))
    if report.parity_issues:
        blockers.append(_blocker(
            "feature_projection_parity_mismatch", "error",
            "Current projection parity must be resolved before save.", "features_csv",
        ))
    return tuple(blockers)


def _candidate_projection_blockers(
    draft: DataDefinitionDraft,
    report: DataDefinitionReport,
) -> tuple[DataDefinitionSaveBlocker, ...]:
    if not draft.is_changed:
        return ()
    candidate = project_feature_catalog_from_draft(draft)
    if projected_feature_catalog_fingerprint(candidate) == (
        projected_feature_catalog_fingerprint(report.catalog_features)
    ):
        return ()
    message = (
        "Schema save is blocked because the draft changes the ML compatibility "
        "projection and no features.csv projection writer is available."
    )
    contexts = _projection_changing_changes(draft)
    if not contexts:
        return (_blocker(
            "ml_compatibility_projection_write_required",
            "error",
            message,
            "schema_csv",
        ),)
    return tuple(
        _blocker(
            "ml_compatibility_projection_write_required",
            "error",
            message,
            "schema_csv",
            row_identity=change.row_identity,
            field_name=change.field_name,
        )
        for change in contexts
    )


def _projection_changing_changes(
    draft: DataDefinitionDraft,
) -> tuple[DataDefinitionDraftChange, ...]:
    baseline = _projection_attribution_baseline(draft)
    baseline_fingerprint = _draft_projection_fingerprint(baseline)
    baseline_identities = {row.identity for row in baseline.rows}
    changes_by_identity: dict[
        tuple[str, str], list[DataDefinitionDraftChange]
    ] = {}
    for change in draft.attributed_changes():
        if change.field_name == "__row__" or change.row_identity not in baseline_identities:
            continue
        changes_by_identity.setdefault(change.row_identity, []).append(change)

    contexts: list[DataDefinitionDraftChange] = []
    for identity, definition_changes in changes_by_identity.items():
        definition_changes_tuple = tuple(definition_changes)
        definition_candidate = _apply_definition_changes(
            baseline,
            identity,
            definition_changes_tuple,
        )
        definition_fingerprint = _draft_projection_fingerprint(definition_candidate)
        if definition_fingerprint == baseline_fingerprint:
            continue
        contexts.extend(
            _projection_relevant_changes(
                baseline,
                identity,
                definition_changes_tuple,
                baseline_fingerprint,
                definition_fingerprint,
            )
        )
    return tuple(contexts)


def _projection_attribution_baseline(
    draft: DataDefinitionDraft,
) -> DataDefinitionDraft:
    schema_rows = sorted(
        (
            row
            for row in (
                *draft.baseline_rows,
                *draft.controlled_addition_initial_rows,
            )
            if row.source_kind == "schema_row"
        ),
        key=lambda row: row.display_order,
    )
    other_rows = tuple(
        row for row in draft.baseline_rows if row.source_kind != "schema_row"
    )
    rows = (*schema_rows, *other_rows)
    return DataDefinitionDraft(
        rows=rows,
        baseline_rows=rows,
        base_generation_id=draft.base_generation_id,
    )


def _projection_relevant_changes(
    baseline: DataDefinitionDraft,
    identity: tuple[str, str],
    changes: tuple[DataDefinitionDraftChange, ...],
    baseline_fingerprint: str,
    definition_fingerprint: str,
) -> tuple[DataDefinitionDraftChange, ...]:
    """Keep singleton-impactful or full-bundle-necessary field changes."""
    relevant: list[DataDefinitionDraftChange] = []
    for index, change in enumerate(changes):
        singleton = _apply_definition_changes(baseline, identity, (change,))
        if _draft_projection_fingerprint(singleton) != baseline_fingerprint:
            relevant.append(change)
            continue
        without_change = _apply_definition_changes(
            baseline,
            identity,
            changes[:index] + changes[index + 1:],
        )
        if _draft_projection_fingerprint(without_change) != definition_fingerprint:
            relevant.append(change)
    return tuple(relevant)


def _apply_definition_changes(
    baseline: DataDefinitionDraft,
    identity: tuple[str, str],
    changes: tuple[DataDefinitionDraftChange, ...],
) -> DataDefinitionDraft:
    candidate = baseline
    for change in changes:
        candidate = replace_draft_row(
            candidate,
            identity,
            **{change.field_name: change.after},
        )
    return candidate


def _draft_projection_fingerprint(draft: DataDefinitionDraft) -> str:
    return projected_feature_catalog_fingerprint(
        project_feature_catalog_from_draft(draft)
    )


def _candidate_data_definition_blockers(
    draft: DataDefinitionDraft,
    report: DataDefinitionReport,
    projection_blockers: tuple[DataDefinitionSaveBlocker, ...],
) -> tuple[DataDefinitionSaveBlocker, ...]:
    issues = validate_data_definition_candidate(draft, report)
    issues = _issues_without_duplicate_ml_parity(
        draft,
        report,
        issues,
        projection_blockers,
    )
    basic_issue_rows = {
        issue.row_identity
        for issue in issues
        if issue.code in _BASIC_SCHEMA_ISSUE_CODES
    }
    return tuple(
        _blocker(
            f"candidate_{issue.code}",
            "error",
            issue.message,
            "schema_csv",
            row_identity=issue.row_identity,
            field_name=issue.field_name,
        )
        for issue in issues
        if issue.row_identity not in basic_issue_rows
    )


def _issues_without_duplicate_ml_parity(
    draft: DataDefinitionDraft,
    report: DataDefinitionReport,
    issues: tuple[DataDefinitionCandidateIssue, ...],
    projection_blockers: tuple[DataDefinitionSaveBlocker, ...],
) -> tuple[DataDefinitionCandidateIssue, ...]:
    """Keep parity evidence that remains after attributed ML changes are reverted."""
    reference = _draft_without_ml_projection_changes(draft, projection_blockers)
    if reference is draft:
        return issues
    independent_parity = tuple(
        issue
        for issue in validate_data_definition_candidate(reference, report)
        if issue.code in _PARITY_ISSUE_CODES
    )
    result: list[DataDefinitionCandidateIssue] = []
    parity_inserted = False
    for issue in issues:
        if issue.code not in _PARITY_ISSUE_CODES:
            result.append(issue)
            continue
        if not parity_inserted:
            result.extend(independent_parity)
            parity_inserted = True
    return tuple(result)


def _draft_without_ml_projection_changes(
    draft: DataDefinitionDraft,
    projection_blockers: tuple[DataDefinitionSaveBlocker, ...],
) -> DataDefinitionDraft:
    baseline_rows = {
        row.identity: row
        for row in _projection_attribution_baseline(draft).rows
    }
    reference = draft
    reverted = False
    for blocker in projection_blockers:
        baseline_row = baseline_rows.get(blocker.row_identity)
        if baseline_row is None or not blocker.field_name:
            continue
        reference = replace_draft_row(
            reference,
            blocker.row_identity,
            **{blocker.field_name: getattr(baseline_row, blocker.field_name)},
        )
        reverted = True
    return reference if reverted else draft


def _change_blockers(
    draft: DataDefinitionDraft,
    changes: tuple[DataDefinitionDraftChange, ...],
) -> tuple[DataDefinitionSaveBlocker, ...]:
    blockers = [
        *_raw_row_change_blockers(draft, changes),
        *_field_policy_blockers(draft),
        *_derived_policy_blockers(changes),
    ]
    checks = (
        (
            any(change.field_name in RETRAIN_FIELDS for change in changes),
            ("retrain_required_for_new_model_input", "info",
             "Model input changes require retraining before activation.", "model_artifact"),
        ),
        (
            any(change.field_name in ONE_HOT_FIELDS for change in changes),
            ("one_hot_runtime_owner_deferred", "warning",
             "Generic one-hot runtime owner switch is deferred to Arc 15E.", "one_hot_runtime"),
        ),
        (
            any(change.field_name in MAPPING_REQUIREMENT_FIELDS for change in changes),
            ("data_mapping_dynamic_requirement_deferred", "warning",
             "Dynamic Data Mapping requirement injection is deferred to Arc 15D.",
             "data_mapping_requirements"),
        ),
    )
    blockers.extend(_blocker(*args) for present, args in checks if present)
    return tuple(blockers)


def _raw_row_change_blockers(
    draft: DataDefinitionDraft,
    changes: tuple[DataDefinitionDraftChange, ...],
) -> tuple[DataDefinitionSaveBlocker, ...]:
    return tuple(
        _blocker(
            "raw_row_add_delete_not_allowed",
            "error",
            "Raw draft row add/delete requires a controlled Add/Remove Feature command.",
            "schema_csv",
            row_identity=change.row_identity,
            field_name=change.field_name,
        )
        for change in changes
        if change.field_name == "__row__"
        and not (
            change.before is None
            and draft.is_controlled_row_addition(change.row_identity)
        )
        and not (
            change.after is None
            and draft.is_controlled_row_removal(change.row_identity)
        )
    )


def _field_policy_blockers(
    draft: DataDefinitionDraft,
) -> tuple[DataDefinitionSaveBlocker, ...]:
    return tuple(
        _blocker(
            "restricted_field_edit_not_allowed",
            "error",
            (
                f"Direct edit of {change.field_name} on {change.row_identity} "
                f"is blocked: {change.reason}"
            ),
            "schema_csv",
            row_identity=change.row_identity,
            field_name=change.field_name,
        )
        for change in restricted_draft_field_changes(draft)
    )


def _derived_policy_blockers(
    changes: tuple[DataDefinitionDraftChange, ...],
) -> tuple[DataDefinitionSaveBlocker, ...]:
    return tuple(
        _blocker(
            "derived_policy_persistence_required",
            "error",
            "Derived policy edits require a persistence owner before save.",
            "derived_policy",
            row_identity=change.row_identity,
            field_name=change.field_name,
        )
        for change in changes
        if change.row_identity[0] == "derived_policy"
    )


def _requested_target_blockers(
    requested_targets: tuple[str, ...],
) -> tuple[DataDefinitionSaveBlocker, ...]:
    blockers: list[DataDefinitionSaveBlocker] = []
    if "features_csv" in requested_targets:
        blockers.append(_blocker(
            "features_csv_dual_writer_not_resolved", "error",
            "features.csv write is blocked until Data Definition-to-ML catalog persistence is defined.",
            "features_csv",
        ))
    if "derived_policy" in requested_targets:
        blockers.append(_blocker(
            "derived_policy_persistence_required", "error",
            "Derived policy write target is not defined in Arc 15C-1.", "derived_policy",
        ))
    if "mapping_json" in requested_targets:
        blockers.append(_blocker(
            "mapping_value_edit_not_allowed", "error",
            "Data Definition save cannot target mapping.json values.", "mapping_json",
        ))
    return tuple(blockers)


def _write_targets(
    draft: DataDefinitionDraft,
    changes: tuple[DataDefinitionDraftChange, ...],
    blockers: list[DataDefinitionSaveBlocker],
    requested_targets: tuple[str, ...],
) -> tuple[DataDefinitionWriteTarget, ...]:
    has_schema_change = any(_is_schema_change(draft, change) for change in changes)
    schema_blocked = any(
        blocker.severity == "error" and blocker.target in {"schema_csv", ""}
        for blocker in blockers
    )
    schema_status: WriteTargetStatus = (
        "blocked" if has_schema_change and schema_blocked
        else "planned" if has_schema_change
        else "no_op"
    )
    targets = [
        _target(
            "schema_csv",
            schema_status,
            "Future primary Data Definition save target; no writer in Arc 15C-1.",
        ),
        _target(
            "features_csv",
            "blocked",
            "The independent ML catalog remains read-only; no projection writer is defined.",
        ),
        _target("derived_policy", "blocked", "Derived policy persistence owner is not defined."),
    ]
    if "mapping_json" in requested_targets or any(
        blocker.target == "mapping_json" for blocker in blockers
    ):
        targets.append(
            _target(
                "mapping_json",
                "blocked",
                "Mapping values remain owned by Data Mapping Manager.",
            )
        )
    return tuple(targets)


def _blocker(
    code: str,
    severity: BlockerSeverity,
    message: str,
    target: str,
    *,
    row_identity: tuple[str, str] | None = None,
    field_name: str = "",
) -> DataDefinitionSaveBlocker:
    return DataDefinitionSaveBlocker(
        code,
        severity,
        message,
        target,
        row_identity,
        field_name,
    )


def _target(target: str, status: WriteTargetStatus, reason: str) -> DataDefinitionWriteTarget:
    return DataDefinitionWriteTarget(target, status, reason)


def _requires_restart(
    draft: DataDefinitionDraft,
    changes: tuple[DataDefinitionDraftChange, ...],
) -> bool:
    return any(_is_schema_change(draft, change) for change in changes)


def _requires_retrain(changes: tuple[DataDefinitionDraftChange, ...]) -> bool:
    return any(change.field_name in RETRAIN_FIELDS for change in changes)


def _is_schema_change(
    draft: DataDefinitionDraft,
    change: DataDefinitionDraftChange,
) -> bool:
    return change.row_identity[0] == "schema_row" and (
        change.field_name in SCHEMA_CHANGE_FIELDS
        or (
            change.field_name == "__row__"
            and (
                (change.before is None and draft.is_controlled_row_addition(change.row_identity))
                or (change.after is None and draft.is_controlled_row_removal(change.row_identity))
            )
        )
    )


def _impact_message(requires_restart: bool, requires_retrain: bool) -> str:
    if requires_restart and requires_retrain:
        return "Schema restart and model retrain are required before activation."
    if requires_restart:
        return "Schema change is restart-required."
    if requires_retrain:
        return "Model input change is retrain-required."
    return "No restart or retrain impact for unchanged draft."
