"""Cross-contract validator for Arc 15A Data Definition foundation."""

from __future__ import annotations

from pathlib import Path

from core.data_definition.model import OneHotRelationship, ProjectedFeatureRow
from core.data_definition.report_model import DataDefinitionIssue, DataDefinitionReport
from core.data_definition.projection import (
    data_definition_rows_from_catalog,
    extract_mapping_requirements,
    project_feature_catalog_from_catalog,
    projected_row_from_catalog_row,
)
from core.data_definition.readiness import build_readiness_checks
from core.ml.feature_catalog import load_feature_catalog
from core.ml.feature_catalog_projection import one_hot_groups
from core.predictor_schema.catalog_v2 import (
    load_predict_schema_catalog_v2,
    validate_predict_schema_catalog_v2,
)


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
    issues = schema_issues + parity_issues + one_hot_issues + readiness_issues
    return DataDefinitionReport(
        projected_features=projected,
        catalog_features=catalog_rows,
        parity_issues=parity_issues,
        mapping_requirements=extract_mapping_requirements(schema_rows),
        one_hot_relationships=one_hot_relationships,
        readiness=readiness,
        issues=issues,
    )


def compare_projected_features_to_catalog(
    projected: tuple[ProjectedFeatureRow, ...],
    catalog_rows: tuple[ProjectedFeatureRow, ...],
) -> tuple[DataDefinitionIssue, ...]:
    """Compare Feature Catalog-compatible rows, excluding notes by design."""
    issues: list[DataDefinitionIssue] = []
    max_len = max(len(projected), len(catalog_rows))
    for index in range(max_len):
        if index >= len(projected):
            row = catalog_rows[index]
            issues.append(
                _issue(
                    "error",
                    "catalog_orphan",
                    _row_identity(row),
                    f"row {index + 1}",
                )
            )
            continue
        if index >= len(catalog_rows):
            row = projected[index]
            issues.append(
                _issue(
                    "error",
                    "projection_extra",
                    _row_identity(row),
                    f"row {index + 1}",
                )
            )
            continue
        expected = catalog_rows[index]
        actual = projected[index]
        if actual.comparison_key() != expected.comparison_key():
            issues.append(
                DataDefinitionIssue(
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
            )
    return tuple(issues)


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
        if emitted_names != catalog_names:
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
