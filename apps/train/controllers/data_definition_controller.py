"""Controller boundary for the Train Data Definition panel."""

from __future__ import annotations

from dataclasses import dataclass

from apps.train.services.data_definition_service import DataDefinitionService
from core.data_definition import DataDefinitionIssue, DataDefinitionReport


@dataclass(frozen=True)
class DataDefinitionControllerState:
    """UI-facing Data Definition read-only state."""

    status: str
    message: str
    summary_rows: tuple[tuple[str, str], ...]
    projected_feature_rows: tuple[tuple[str, ...], ...]
    mapping_requirement_rows: tuple[tuple[str, ...], ...]
    one_hot_rows: tuple[tuple[str, ...], ...]
    readiness_rows: tuple[tuple[str, ...], ...]
    issue_rows: tuple[tuple[str, ...], ...]


class DataDefinitionController:
    """Coordinate Data Definition report refresh for the UI."""

    def __init__(self, service: DataDefinitionService | None = None) -> None:
        self._service = service or DataDefinitionService()

    def refresh(self) -> DataDefinitionControllerState:
        """Return current read-only Data Definition view state."""
        try:
            report = self._service.refresh_report()
        except Exception as exc:
            return _error_state(exc)
        return _state_from_report(report)


def _state_from_report(report: DataDefinitionReport) -> DataDefinitionControllerState:
    parity_count = len(report.parity_issues)
    issue_count = len([issue for issue in report.issues if issue.severity == "error"])
    status = "ready" if report.ok else "error"
    message = "Data Definition report ready." if report.ok else "Data Definition issues found."
    summary_rows = (
        ("Status", "OK" if report.ok else "Issues"),
        ("Projected features", str(len(report.projected_features))),
        ("Current catalog features", str(len(report.catalog_features))),
        ("Parity issues", str(parity_count)),
        ("Mapping requirements", str(len(report.mapping_requirements))),
        ("One-hot relationships", str(len(report.one_hot_relationships))),
        ("Readiness", _readiness_summary(report)),
        ("Error issues", str(issue_count)),
    )
    return DataDefinitionControllerState(
        status=status,
        message=message,
        summary_rows=summary_rows,
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
    )


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
        projected_feature_rows=(),
        mapping_requirement_rows=(),
        one_hot_rows=(),
        readiness_rows=(),
        issue_rows=(("error", "load_failed", "Data Definition", str(exc)),),
    )
