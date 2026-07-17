"""Guarded schema.csv writer for Data Definition drafts."""

from __future__ import annotations

import csv
import os
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from core.data_definition.draft import (
    DataDefinitionDraft,
    DataDefinitionDraftRow,
    build_data_definition_draft,
)
from core.data_definition.edit_policy import restricted_draft_field_changes
from core.data_definition.save_contract import (
    DataDefinitionSaveBlocker,
    DataDefinitionSavePlan,
    build_data_definition_save_plan,
)
from core.data_definition.validation import (
    build_data_definition_report,
    validate_data_definition_candidate,
)
from core.predictor_schema.catalog_v2 import (
    REQUIRED_HEADERS,
    load_predict_schema_catalog_v2,
    validate_predict_schema_catalog_v2_issues,
)


@dataclass(frozen=True)
class DataDefinitionSchemaWritePreview:
    path: Path
    rows_to_write: int
    backup_required: bool


@dataclass(frozen=True)
class DataDefinitionSchemaSaveResult:
    success: bool
    path: Path | None
    rows_written: int
    issues: tuple[DataDefinitionSaveBlocker, ...]
    message: str
    backup_path: Path | None = None
    status: str = "blocked"


def save_data_definition_schema_draft(
    draft: DataDefinitionDraft,
    destination_path: str | Path | None,
    *,
    save_plan: DataDefinitionSavePlan | None = None,
    target: str = "schema_csv",
) -> DataDefinitionSchemaSaveResult:
    """Write schema-backed draft rows to an explicit CSV destination."""
    if destination_path is None:
        return _blocked_result(None, (), "destination_path is required")
    destination = Path(destination_path)
    if target != "schema_csv":
        return _blocked_result(
            destination,
            (_blocker("schema_writer_target_not_allowed", f"Unsupported target: {target}"),),
            f"Unsupported writer target: {target}",
        )

    plan = save_plan or build_data_definition_save_plan(
        draft,
        requested_targets=("schema_csv",),
    )
    blockers = _writer_blockers(draft, plan, target)
    if blockers:
        return _blocked_result(destination, blockers, "Schema save guard blocked write")
    if not draft.is_changed:
        return DataDefinitionSchemaSaveResult(
            success=False,
            path=destination,
            rows_written=0,
            issues=(),
            message="Draft is unchanged; schema write skipped.",
            status="noop",
        )

    rows = schema_csv_rows_from_draft(draft)
    preview = DataDefinitionSchemaWritePreview(
        path=destination,
        rows_to_write=len(rows),
        backup_required=destination.exists(),
    )
    return _atomic_write_schema_csv(preview, rows)


def schema_csv_rows_from_draft(
    draft: DataDefinitionDraft,
) -> tuple[dict[str, str], ...]:
    """Return CSV rows for schema-backed draft rows only."""
    schema_rows = sorted(
        (row for row in draft.rows if row.source_kind == "schema_row"),
        key=lambda row: row.display_order,
    )
    return tuple(_csv_row(row) for row in schema_rows)


def _writer_blockers(
    draft: DataDefinitionDraft,
    save_plan: DataDefinitionSavePlan,
    target: str,
) -> tuple[DataDefinitionSaveBlocker, ...]:
    blockers = list(save_plan.blocked_reasons)
    if target != "schema_csv":
        blockers.append(_blocker("schema_writer_target_not_allowed", f"Unsupported target: {target}"))
    if not save_plan.can_save_schema and draft.is_changed:
        blockers.append(_blocker("schema_save_plan_not_allowed", "Save plan did not allow schema write."))
    for change in draft.changes():
        if change.field_name == "__row__" and not (
            change.before is None
            and draft.is_controlled_row_addition(change.row_identity)
        ) and not (
            change.after is None
            and draft.is_controlled_row_removal(change.row_identity)
        ):
            _append_blocker_if_missing(blockers, _blocker(
                "raw_row_add_delete_not_allowed",
                "Raw draft row add/delete requires a controlled Add/Remove Feature command.",
                row_identity=change.row_identity,
                field_name=change.field_name,
            ))
        if change.row_identity[0] == "derived_policy":
            _append_blocker_if_missing(blockers, _blocker(
                "derived_policy_persistence_required",
                "Derived policy changes cannot be written to schema.csv.",
                row_identity=change.row_identity,
                field_name=change.field_name,
            ))
    for change in restricted_draft_field_changes(draft):
        _append_blocker_if_missing(blockers, _blocker(
            "restricted_field_edit_not_allowed",
            "Restricted direct field edits require a controlled command.",
            row_identity=change.row_identity,
            field_name=change.field_name,
        ))
    return tuple(
        blocker
        for blocker in blockers
        if blocker.severity == "error" and blocker.target in {target, ""}
    )


def _append_blocker_if_missing(
    blockers: list[DataDefinitionSaveBlocker],
    candidate: DataDefinitionSaveBlocker,
) -> None:
    identity = (
        candidate.code,
        candidate.target,
        candidate.row_identity,
        candidate.field_name,
    )
    if not any(
        (item.code, item.target, item.row_identity, item.field_name) == identity
        for item in blockers
    ):
        blockers.append(candidate)


def _atomic_write_schema_csv(
    preview: DataDefinitionSchemaWritePreview,
    rows: tuple[dict[str, str], ...],
) -> DataDefinitionSchemaSaveResult:
    destination = preview.path
    destination.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = destination.parent / f".{destination.name}.{uuid4().hex}.tmp"
    backup_path: Path | None = None
    try:
        with tmp_path.open("w", encoding="utf-8", newline="") as output:
            writer = csv.DictWriter(output, fieldnames=REQUIRED_HEADERS)
            writer.writeheader()
            writer.writerows(rows)
        candidate_issues = _candidate_schema_issues(tmp_path)
        if candidate_issues:
            tmp_path.unlink(missing_ok=True)
            return DataDefinitionSchemaSaveResult(
                success=False,
                path=destination,
                rows_written=0,
                issues=candidate_issues,
                message="Candidate schema validation failed.",
                status="blocked",
            )
        if preview.backup_required:
            backup_path = _backup_destination(destination)
        os.replace(tmp_path, destination)
    except OSError as exc:
        tmp_path.unlink(missing_ok=True)
        return DataDefinitionSchemaSaveResult(
            success=False,
            path=destination,
            rows_written=0,
            issues=(),
            message=f"Schema write failed: {exc}",
            backup_path=backup_path,
            status="error",
        )
    return DataDefinitionSchemaSaveResult(
        success=True,
        path=destination,
        rows_written=len(rows),
        issues=(),
        message="Schema CSV written.",
        backup_path=backup_path,
        status="written",
    )


def _backup_destination(destination: Path) -> Path:
    backup_dir = destination.parent / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
    backup_path = backup_dir / f"{destination.stem}.{stamp}{destination.suffix}"
    shutil.copy2(destination, backup_path)
    return backup_path


def _candidate_schema_issues(tmp_path: Path) -> tuple[DataDefinitionSaveBlocker, ...]:
    catalog_issues = validate_predict_schema_catalog_v2_issues(
        load_predict_schema_catalog_v2(tmp_path),
    )
    if catalog_issues:
        return tuple(
            _blocker(
                "candidate_schema_validation_failed",
                issue.message,
                row_identity=("schema_row", issue.column_key) if issue.column_key else None,
                field_name=issue.field_name,
            )
            for issue in catalog_issues
        )
    candidate_draft = build_data_definition_draft(schema_path=tmp_path)
    candidate_report = build_data_definition_report(schema_path=tmp_path)
    candidate_issues = validate_data_definition_candidate(
        candidate_draft,
        candidate_report,
    )
    return tuple(
        _blocker(
            f"candidate_{issue.code}",
            issue.message,
            row_identity=issue.row_identity,
            field_name=issue.field_name,
        )
        for issue in candidate_issues
    )


def _csv_row(row: DataDefinitionDraftRow) -> dict[str, str]:
    return {
        "display_order": str(row.display_order),
        "column_key": row.column_key,
        "label": row.label,
        "role": row.role,
        "editor": row.editor,
        "data_type": row.data_type,
        "visible": _bool(row.visible),
        "required": _bool(row.required),
        "readonly": _bool(row.readonly),
        "value_source": row.value_source,
        "mapping_entity": row.mapping_entity,
        "mapping_attribute": row.mapping_attribute,
        "trigger_column": row.trigger_column,
        "rule_id": row.rule_id,
        "model_input_enabled": _bool(row.model_input_enabled),
        "ml_name": row.ml_name,
        "one_hot_group": row.one_hot_group,
        "active": _bool(row.active),
        "notes": row.notes,
    }


def _bool(value: bool) -> str:
    return "true" if value else "false"


def _blocker(
    code: str,
    message: str,
    *,
    row_identity: tuple[str, str] | None = None,
    field_name: str = "",
) -> DataDefinitionSaveBlocker:
    return DataDefinitionSaveBlocker(
        code,
        "error",
        message,
        "schema_csv",
        row_identity,
        field_name,
    )


def _blocked_result(
    path: Path | None,
    issues: tuple[DataDefinitionSaveBlocker, ...],
    message: str,
) -> DataDefinitionSchemaSaveResult:
    return DataDefinitionSchemaSaveResult(
        success=False,
        path=path,
        rows_written=0,
        issues=issues,
        message=message,
        status="blocked",
    )
