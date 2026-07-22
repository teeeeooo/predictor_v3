"""Cross-contract validator for Arc 15A Data Definition foundation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from core.data_definition.candidate_contract import (
    DataDefinitionCandidateIssue,
    candidate_mapping_contract_issues,
    mapping_contract_report_issues,
)
from core.data_definition.command_validation import validate_complete_row
from core.data_definition.draft import DataDefinitionDraft, DataDefinitionDraftRow
from core.data_definition.mapping_requirement_contract import (
    resolve_mapping_requirement_contracts,
)
from core.data_definition.model import OneHotRelationship, ProjectedFeatureRow
from core.data_definition.report_model import DataDefinitionIssue, DataDefinitionReport
from core.data_definition.projection import (
    data_definition_rows_from_catalog,
    extract_mapping_requirements,
    extract_mapping_requirements_from_draft,
    project_feature_catalog_from_catalog,
    project_feature_catalog_from_draft,
    projected_row_from_catalog_row,
)
from core.data_definition.readiness import build_readiness_checks
from core.ml.feature_catalog import load_feature_catalog
from core.ml.feature_catalog_projection import one_hot_groups
from core.predictor_schema.catalog_v2 import (
    load_predict_schema_catalog_v2,
    validate_predict_schema_catalog_v2,
)

_PROJECTED_FIELDS = (
    "order",
    "ml_name",
    "role",
    "ui_key",
    "label",
    "source",
    "mapping_key",
    "one_hot_group",
    "zero_fill_policy",
    "active",
)
_PROJECTED_TO_SCHEMA_FIELD = {
    "order": "display_order",
    "ml_name": "ml_name",
    "role": "role",
    "ui_key": "column_key",
    "label": "label",
    "source": "trigger_column",
    "mapping_key": "mapping_attribute",
    "one_hot_group": "one_hot_group",
    "zero_fill_policy": "ml_name",
    "active": "active",
}


@dataclass(frozen=True)
class _ProjectionParityMismatch:
    code: str
    issue: DataDefinitionIssue
    expected: ProjectedFeatureRow | None
    actual: ProjectedFeatureRow | None


def build_data_definition_report(
    schema_path: str | Path | None = None,
    feature_catalog_path: str | Path | None = None,
    training_data_path: str | Path | None = None,
) -> DataDefinitionReport:
    """Build a read-only Data Definition projection and validation report."""
    schema_catalog = load_predict_schema_catalog_v2(schema_path)
    feature_catalog = load_feature_catalog(feature_catalog_path)
    schema_rows = data_definition_rows_from_catalog(schema_catalog)
    projected = project_feature_catalog_from_catalog(schema_catalog)
    catalog_rows = tuple(projected_row_from_catalog_row(row) for row in feature_catalog.rows)
    schema_issues = _schema_issues(validate_predict_schema_catalog_v2(schema_catalog))
    parity_issues = compare_projected_features_to_catalog(projected, catalog_rows)
    one_hot_relationships, one_hot_issues = validate_one_hot_relationships(
        schema_catalog.active_rows,
        catalog_rows,
    )
    readiness = build_readiness_checks(projected, training_data_path)
    readiness_issues = _readiness_issues(readiness)
    mapping_requirements = extract_mapping_requirements(schema_rows)
    contract_issues = mapping_contract_report_issues(
        resolve_mapping_requirement_contracts(mapping_requirements).conflicts
    )
    issues = (
        schema_issues
        + parity_issues
        + one_hot_issues
        + readiness_issues
        + contract_issues
    )
    return DataDefinitionReport(
        projected_features=projected,
        catalog_features=catalog_rows,
        parity_issues=parity_issues,
        mapping_requirements=mapping_requirements,
        one_hot_relationships=one_hot_relationships,
        readiness=readiness,
        issues=issues,
    )


def compare_projected_features_to_catalog(
    projected: tuple[ProjectedFeatureRow, ...],
    catalog_rows: tuple[ProjectedFeatureRow, ...],
) -> tuple[DataDefinitionIssue, ...]:
    """Compare Feature Catalog-compatible rows, excluding notes by design."""
    return tuple(
        mismatch.issue
        for mismatch in _projection_parity_mismatches(projected, catalog_rows)
    )


def validate_data_definition_candidate(
    draft: DataDefinitionDraft,
    current_report: DataDefinitionReport,
) -> tuple[DataDefinitionCandidateIssue, ...]:
    """Validate row shape, full Feature Catalog parity, and one-hot relations."""
    issues: list[DataDefinitionCandidateIssue] = []
    schema_rows = tuple(
        row for row in draft.rows if row.source_kind == "schema_row"
    )
    for row in schema_rows:
        issues.extend(
            DataDefinitionCandidateIssue(
                issue.code,
                issue.message,
                row.identity,
                issue.field_name,
            )
            for issue in validate_complete_row(row)
        )
    contract_conflicts = resolve_mapping_requirement_contracts(
        extract_mapping_requirements_from_draft(draft)
    ).conflicts
    issues.extend(candidate_mapping_contract_issues(contract_conflicts))
    projected = project_feature_catalog_from_draft(draft)
    for mismatch in _projection_parity_mismatches(
        projected,
        current_report.catalog_features,
    ):
        issues.extend(_candidate_projection_issues(draft, mismatch))
    _, one_hot_issues = validate_one_hot_relationships(
        tuple(row for row in schema_rows if row.active),
        current_report.catalog_features,
    )
    issues.extend(
        _candidate_one_hot_issue(schema_rows, issue)
        for issue in one_hot_issues
    )
    return _dedupe_candidate_issues(issues)


def _projection_parity_mismatches(
    projected: tuple[ProjectedFeatureRow, ...],
    catalog_rows: tuple[ProjectedFeatureRow, ...],
) -> tuple[_ProjectionParityMismatch, ...]:
    mismatches: list[_ProjectionParityMismatch] = []
    max_len = max(len(projected), len(catalog_rows))
    for index in range(max_len):
        if index >= len(projected):
            row = catalog_rows[index]
            issue = _issue(
                "error",
                "catalog_orphan",
                _row_identity(row),
                f"row {index + 1}",
            )
            mismatches.append(_ProjectionParityMismatch(
                "catalog_orphan", issue, row, None,
            ))
            continue
        if index >= len(catalog_rows):
            row = projected[index]
            issue = _issue(
                "error",
                "projection_extra",
                _row_identity(row),
                f"row {index + 1}",
            )
            mismatches.append(_ProjectionParityMismatch(
                "projection_extra", issue, None, row,
            ))
            continue
        expected = catalog_rows[index]
        actual = projected[index]
        if actual.comparison_key() != expected.comparison_key():
            issue = DataDefinitionIssue(
                severity="error",
                code="feature_projection_mismatch",
                subject=expected.ml_name or actual.ml_name,
                message=(
                    "Projected feature row differs from current features.csv "
                    f"at row {index + 1}; expected={_row_identity(expected)}; "
                    f"actual={_row_identity(actual)}; notes are intentionally "
                    "excluded."
                ),
            )
            mismatches.append(_ProjectionParityMismatch(
                "feature_projection_mismatch", issue, expected, actual,
            ))
    return tuple(mismatches)


def _candidate_projection_issues(
    draft: DataDefinitionDraft,
    mismatch: _ProjectionParityMismatch,
) -> tuple[DataDefinitionCandidateIssue, ...]:
    reference = mismatch.actual or mismatch.expected
    row = _candidate_row_for_projection(draft, reference)
    identity = row.identity if row is not None else None
    if mismatch.expected is not None and mismatch.actual is not None:
        fields = tuple(
            _PROJECTED_TO_SCHEMA_FIELD[field_name]
            for field_name in _PROJECTED_FIELDS
            if field_name != "order"
            and getattr(mismatch.expected, field_name) != getattr(mismatch.actual, field_name)
        ) or ("display_order",)
    else:
        fields = (_projection_presence_field(row, mismatch),)
    return tuple(
        DataDefinitionCandidateIssue(
            mismatch.code,
            mismatch.issue.message,
            identity,
            field_name,
        )
        for field_name in dict.fromkeys(fields)
    )


def _candidate_row_for_projection(
    draft: DataDefinitionDraft,
    projected: ProjectedFeatureRow | None,
) -> DataDefinitionDraftRow | None:
    if projected is None:
        return None
    return next(
        (
            row
            for row in draft.rows
            if row.source_kind == "schema_row"
            and (
                (projected.ui_key and row.column_key == projected.ui_key)
                or (projected.ml_name and row.ml_name == projected.ml_name)
            )
        ),
        None,
    )


def _projection_presence_field(
    row: DataDefinitionDraftRow | None,
    mismatch: _ProjectionParityMismatch,
) -> str:
    if row is None:
        return "model_input_enabled"
    if mismatch.code == "projection_extra":
        return "model_input_enabled" if row.model_input_enabled else "ml_name"
    expected = mismatch.expected
    if not row.active:
        return "active"
    if expected is not None and expected.role == "result" and row.value_source != "result":
        return "value_source"
    if not row.model_input_enabled and row.role in {"input", "auto", "one_hot_feature"}:
        return "model_input_enabled"
    return "ml_name"


def _candidate_one_hot_issue(
    schema_rows: tuple[DataDefinitionDraftRow, ...],
    issue: DataDefinitionIssue,
) -> DataDefinitionCandidateIssue:
    row = next(
        (item for item in schema_rows if item.one_hot_group == issue.subject),
        None,
    )
    return DataDefinitionCandidateIssue(
        issue.code,
        issue.message,
        row.identity if row is not None else None,
        "one_hot_group",
    )


def _dedupe_candidate_issues(
    issues: list[DataDefinitionCandidateIssue],
) -> tuple[DataDefinitionCandidateIssue, ...]:
    seen: set[tuple[object, ...]] = set()
    unique: list[DataDefinitionCandidateIssue] = []
    for issue in issues:
        key = (issue.code, issue.row_identity, issue.field_name, issue.message)
        if key not in seen:
            seen.add(key)
            unique.append(issue)
    return tuple(unique)


def validate_one_hot_relationships(
    schema_rows,
    catalog_rows: tuple[ProjectedFeatureRow, ...],
) -> tuple[tuple[OneHotRelationship, ...], tuple[DataDefinitionIssue, ...]]:
    """Validate selector rows, emitted feature rows, and catalog parity."""
    selectors = {
        row.one_hot_group: row.column_key
        for row in schema_rows
        if row.active and row.role == "input" and row.value_source == "one_hot"
    }
    emitted: dict[str, list[tuple[int, str]]] = {}
    for row in schema_rows:
        if row.active and row.role == "one_hot_feature" and row.one_hot_group:
            emitted.setdefault(row.one_hot_group, []).append((row.display_order, row.ml_name))
    catalog_groups = one_hot_groups(_catalog_like_rows(catalog_rows))
    relationships: list[OneHotRelationship] = []
    issues: list[DataDefinitionIssue] = []
    for group_name, selector in sorted(selectors.items()):
        emitted_names = tuple(name for _, name in sorted(emitted.get(group_name, ())))
        catalog_names = tuple(catalog_groups.get(group_name, ()))
        relationships.append(
            OneHotRelationship(
                selector_column=selector,
                one_hot_group=group_name,
                emitted_ml_names=emitted_names,
                catalog_ml_names=catalog_names,
            )
        )
        if not emitted_names:
            issues.append(_issue("error", "one_hot_missing_emitted", group_name, selector))
        # Display order and global ML/category order are independent domains.
        # This legacy parity view checks membership only; the canonical v3
        # contract validates category-relative ML order by stable identity.
        if set(emitted_names) != set(catalog_names):
            issues.append(_issue("error", "one_hot_catalog_mismatch", group_name, selector))
    for group_name in sorted(set(emitted) - set(selectors)):
        issues.append(_issue("error", "one_hot_missing_selector", group_name, group_name))
    return tuple(relationships), tuple(issues)


def _schema_issues(errors: list[str]) -> tuple[DataDefinitionIssue, ...]:
    return tuple(
        DataDefinitionIssue(
            severity="error",
            code="schema_shape",
            message=message,
        )
        for message in errors
    )


def _readiness_issues(readiness) -> tuple[DataDefinitionIssue, ...]:
    return tuple(
        DataDefinitionIssue(
            severity="info",
            code=f"readiness_{check.name}",
            subject=check.name,
            message=check.message,
        )
        for check in readiness
        if check.status in {"unavailable", "not_evaluated"}
    )


def _issue(
    severity: str,
    code: str,
    subject: str,
    detail: str,
) -> DataDefinitionIssue:
    return DataDefinitionIssue(
        severity=severity,
        code=code,
        subject=subject,
        message=f"{code}: {subject} ({detail})",
    )


def _row_identity(row: ProjectedFeatureRow) -> str:
    key = row.ui_key or row.ml_name or "<blank>"
    return f"{key}/{row.ml_name or '<blank>'}/{row.role}"


def _catalog_like_rows(rows: tuple[ProjectedFeatureRow, ...]):
    return tuple(row for row in rows if row.role == "one_hot" and row.active)
