"""Feature Catalog application service."""

from __future__ import annotations

from pathlib import Path

from core.ml.feature_catalog import (
    DEFAULT_CATALOG_PATH,
    REQUIRED_HEADERS,
    FeatureCatalog,
    FeatureCatalogRow,
    load_feature_catalog,
    validate_feature_catalog,
    validate_registry_references,
)
from core.ml.registry import MODEL_REGISTRY

from apps.train.application.feature_catalog.io_models import (
    FeatureCatalogExportResult,
    FeatureCatalogExportWriter,
    FeatureCatalogSaveResult,
)
from apps.train.application.feature_catalog.models import (
    FeatureCatalogRecord,
    FeatureCatalogSnapshot,
    ValidationResult,
)

STRICT_BOOL_VALUES = frozenset({"true", "false"})
STRICT_ZERO_FILL_POLICIES = frozenset({"disallow", "mode_missing_allowed"})
NONEMPTY_SAVE_FIELDS = frozenset(
    {"order", "feature_id", "ml_name", "role", "zero_fill_policy", "active"}
)


class FeatureCatalogService:
    """Load and validate the ML Feature Catalog for Train/Admin UI."""

    def __init__(
        self,
        catalog_path: str | Path | None = None,
        export_writer: FeatureCatalogExportWriter | None = None,
    ) -> None:
        self._catalog_path = Path(catalog_path) if catalog_path is not None else DEFAULT_CATALOG_PATH
        self._export_writer = export_writer

    def load_snapshot(
        self,
        *,
        include_project_consistency: bool = True,
    ) -> FeatureCatalogSnapshot:
        """Return the current Feature Catalog table snapshot and validation state."""
        catalog = load_feature_catalog(self._catalog_path)
        catalog_errors = tuple(validate_feature_catalog(catalog))
        project_validation = None
        if include_project_consistency:
            project_validation = ValidationResult(
                scope="Project consistency validation",
                errors=tuple(validate_registry_references(catalog, MODEL_REGISTRY)),
            )
        return FeatureCatalogSnapshot(
            path=Path(catalog.path or self._catalog_path),
            headers=REQUIRED_HEADERS,
            rows=tuple(_record_from_row(row) for row in catalog.rows),
            active_count=len(catalog.active_rows),
            catalog_validation=ValidationResult(
                scope="Catalog validation",
                errors=catalog_errors,
            ),
            project_validation=project_validation,
        )

    def export_snapshot(
        self,
        snapshot: FeatureCatalogSnapshot,
        destination: str | Path,
    ) -> FeatureCatalogExportResult:
        """Export the current table snapshot through the configured writer."""
        if self._export_writer is None:
            raise RuntimeError("Feature Catalog export writer is not configured.")
        rows = tuple(record.values for record in snapshot.rows)
        path = self._export_writer.write_export(destination, snapshot.headers, rows)
        return FeatureCatalogExportResult(
            path=path,
            row_count=snapshot.row_count,
            validation_status="failed" if snapshot.has_errors else "ok",
            validation_messages=snapshot.validation_messages(),
        )

    def save_records(
        self,
        records: tuple[FeatureCatalogRecord, ...],
    ) -> FeatureCatalogSaveResult:
        """Validate and safely save edited records to the canonical catalog."""
        if self._export_writer is None:
            raise RuntimeError("Feature Catalog save writer is not configured.")

        rows, conversion_errors = _rows_from_records(records)
        if conversion_errors:
            return FeatureCatalogSaveResult(
                saved=False,
                snapshot=None,
                errors=conversion_errors,
                message="Feature Catalog save blocked by validation errors.",
            )

        draft = FeatureCatalog(
            rows=tuple(sorted(rows, key=lambda row: row.order)),
            headers=REQUIRED_HEADERS,
            path=self._catalog_path,
        )
        validation_errors = tuple(validate_feature_catalog(draft)) + tuple(
            validate_registry_references(draft, MODEL_REGISTRY)
        )
        if validation_errors:
            return FeatureCatalogSaveResult(
                saved=False,
                snapshot=None,
                errors=validation_errors,
                message="Feature Catalog save blocked by validation errors.",
            )

        export_rows = tuple(_record_from_row(row).values for row in draft.rows)
        self._export_writer.write_canonical(self._catalog_path, REQUIRED_HEADERS, export_rows)
        snapshot = self.load_snapshot(include_project_consistency=True)
        return FeatureCatalogSaveResult(
            saved=not snapshot.has_errors,
            snapshot=snapshot,
            errors=tuple(snapshot.validation_messages()) if snapshot.has_errors else (),
            message="Feature Catalog saved and reloaded.",
        )


def _record_from_row(row: FeatureCatalogRow) -> FeatureCatalogRecord:
    return FeatureCatalogRecord(
        values=tuple(_display_value(row, header) for header in REQUIRED_HEADERS)
    )


def _display_value(row: FeatureCatalogRow, header: str) -> str:
    value = getattr(row, header)
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def _rows_from_records(
    records: tuple[FeatureCatalogRecord, ...],
) -> tuple[tuple[FeatureCatalogRow, ...], tuple[str, ...]]:
    rows: list[FeatureCatalogRow] = []
    errors: list[str] = []
    for index, record in enumerate(records, start=2):
        row, row_errors = _row_from_record(index, record)
        errors.extend(row_errors)
        if row is not None:
            rows.append(row)
    if errors:
        return (), tuple(errors)
    return tuple(rows), ()


def _row_from_record(
    line_number: int,
    record: FeatureCatalogRecord,
) -> tuple[FeatureCatalogRow | None, tuple[str, ...]]:
    values = dict(zip(REQUIRED_HEADERS, record.values, strict=False))
    errors = _record_shape_errors(line_number, record, values)
    if errors:
        return None, errors

    order_text = values["order"]
    try:
        order = int(order_text)
    except ValueError:
        return None, (f"line {line_number}: invalid order '{order_text}'",)

    active_text = values["active"]
    if active_text not in STRICT_BOOL_VALUES:
        return None, (
            f"line {line_number}: invalid active '{active_text}' "
            "(allowed: true, false)",
        )
    zero_policy = values["zero_fill_policy"]
    if zero_policy not in STRICT_ZERO_FILL_POLICIES:
        return None, (
            f"line {line_number}: invalid zero_fill_policy '{zero_policy}' "
            "(allowed: disallow, mode_missing_allowed)",
        )

    return (
        FeatureCatalogRow(
            order=order,
            feature_id=values["feature_id"],
            ml_name=values["ml_name"],
            role=values["role"],
            ui_key=values["ui_key"],
            label=values["label"],
            source=values["source"],
            mapping_key=values["mapping_key"],
            one_hot_group=values["one_hot_group"],
            zero_fill_policy=zero_policy,
            active=active_text == "true",
            notes=values["notes"],
        ),
        (),
    )


def _record_shape_errors(
    line_number: int,
    record: FeatureCatalogRecord,
    values: dict[str, str],
) -> tuple[str, ...]:
    errors: list[str] = []
    if len(record.values) != len(REQUIRED_HEADERS):
        errors.append(
            f"line {line_number}: expected {len(REQUIRED_HEADERS)} fields, "
            f"got {len(record.values)}"
        )
    missing = [header for header in REQUIRED_HEADERS if header not in values]
    if missing:
        errors.append(f"line {line_number}: missing required field(s): {', '.join(missing)}")
    for field in sorted(NONEMPTY_SAVE_FIELDS):
        if values.get(field, "").strip() == "":
            errors.append(f"line {line_number}: required field '{field}' is empty")
    return tuple(errors)
