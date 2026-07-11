"""Save contract and in-memory save plan for Data Definition drafts."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from core.data_definition.draft import DataDefinitionDraft, DataDefinitionDraftChange
from core.data_definition.edit_policy import restricted_draft_field_changes
from core.data_definition.projection import (
    project_feature_catalog_from_draft,
    projected_feature_catalog_fingerprint,
)
from core.data_definition.report_model import DataDefinitionReport
from core.data_definition.validation import build_data_definition_report

BlockerSeverity = Literal["error", "warning", "info"]
WriteTargetStatus = Literal["planned", "blocked", "deferred", "no_op"]

SCHEMA_CHANGE_FIELDS = frozenset(
    {
        "label", "editor", "data_type", "visible", "required", "readonly",
        "value_source", "mapping_entity", "mapping_attribute", "trigger_column",
        "rule_id", "model_input_enabled", "ml_name", "one_hot_group", "active",
        "notes",
    }
)
RETRAIN_FIELDS = frozenset({"model_input_enabled", "ml_name", "value_source"})
MAPPING_REQUIREMENT_FIELDS = frozenset(
    {"mapping_entity", "mapping_attribute", "trigger_column", "rule_id"}
)
ONE_HOT_FIELDS = frozenset({"one_hot_group", "value_source"})


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
    changes = draft.changes()
    blockers = [
        *_report_blockers(report),
        *_candidate_projection_blockers(draft, report),
        *_change_blockers(draft, changes),
        *_requested_target_blockers(requested_targets),
    ]
    requires_restart = _requires_restart(changes)
    requires_retrain = _requires_retrain(changes)
    can_save_schema = any(_is_schema_change(change) for change in changes) and not any(
        blocker.severity == "error" and blocker.target in {"schema_csv", ""}
        for blocker in blockers
    )
    targets = _write_targets(changes, blockers, requested_targets)
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
    return (_blocker(
        "ml_compatibility_projection_write_required",
        "error",
        (
            "Schema save is blocked because the draft changes the ML compatibility "
            "projection and no features.csv projection writer is available."
        ),
        "schema_csv",
    ),)


def _change_blockers(
    draft: DataDefinitionDraft,
    changes: tuple[DataDefinitionDraftChange, ...],
) -> tuple[DataDefinitionSaveBlocker, ...]:
    blockers = [
        *_raw_row_change_blockers(changes),
        *_field_policy_blockers(draft),
    ]
    checks = (
        (
            any(change.row_identity[0] == "derived_policy" for change in changes),
            ("derived_policy_persistence_required", "error",
             "Derived policy edits require a persistence owner before save.", "derived_policy"),
        ),
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
    changes: tuple[DataDefinitionDraftChange, ...],
) -> tuple[DataDefinitionSaveBlocker, ...]:
    if not any(change.field_name == "__row__" for change in changes):
        return ()
    return (_blocker(
        "raw_row_add_delete_not_allowed", "error",
        "Raw draft row add/delete requires a controlled Add/Remove Feature command.",
        "schema_csv",
    ),)


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
        )
        for change in restricted_draft_field_changes(draft)
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
    changes: tuple[DataDefinitionDraftChange, ...],
    blockers: list[DataDefinitionSaveBlocker],
    requested_targets: tuple[str, ...],
) -> tuple[DataDefinitionWriteTarget, ...]:
    has_schema_change = any(_is_schema_change(change) for change in changes)
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


def _blocker(code: str, severity: BlockerSeverity, message: str, target: str) -> DataDefinitionSaveBlocker:
    return DataDefinitionSaveBlocker(code, severity, message, target)


def _target(target: str, status: WriteTargetStatus, reason: str) -> DataDefinitionWriteTarget:
    return DataDefinitionWriteTarget(target, status, reason)


def _requires_restart(changes: tuple[DataDefinitionDraftChange, ...]) -> bool:
    return any(_is_schema_change(change) for change in changes)


def _requires_retrain(changes: tuple[DataDefinitionDraftChange, ...]) -> bool:
    return any(change.field_name in RETRAIN_FIELDS for change in changes)


def _is_schema_change(change: DataDefinitionDraftChange) -> bool:
    return change.row_identity[0] == "schema_row" and change.field_name in SCHEMA_CHANGE_FIELDS


def _impact_message(requires_restart: bool, requires_retrain: bool) -> str:
    if requires_restart and requires_retrain:
        return "Schema restart and model retrain are required before activation."
    if requires_restart:
        return "Schema change is restart-required."
    if requires_retrain:
        return "Model input change is retrain-required."
    return "No restart or retrain impact for unchanged draft."
