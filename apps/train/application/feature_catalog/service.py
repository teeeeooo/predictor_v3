"""Feature Catalog application service."""

from __future__ import annotations

from pathlib import Path
import re

from core.ml.feature_catalog import (
    DEFAULT_CATALOG_PATH,
    REQUIRED_HEADERS,
    FeatureCatalog,
    FeatureCatalogRow,
    load_feature_catalog,
    validate_feature_catalog,
    validate_registry_references,
)
from core.ml.feature_catalog_projection import UI_VISIBLE_ROLES
from core.ml.registry import MODEL_REGISTRY

from apps.train.application.feature_catalog.io_models import (
    FeatureCatalogExportResult,
    FeatureCatalogExportWriter,
    FeatureCatalogSaveResult,
)
from apps.train.application.feature_catalog.models import (
    DISPLAY_HEADERS,
    FeatureCatalogDraftRequest,
    FeatureCatalogFieldOptions,
    FeatureCatalogRecord,
    FeatureCatalogSnapshot,
    ValidationResult,
)

STRICT_BOOL_VALUES = frozenset({"true", "false"})
STRICT_ZERO_FILL_POLICIES = frozenset({"disallow", "mode_missing_allowed"})
NONEMPTY_SAVE_FIELDS = frozenset(
    {"order", "ml_name", "role", "zero_fill_policy", "active"}
)
SCHEMA_APPLY_MESSAGE = "Catalog saved. Restart app to apply table schema changes."
ROLE_OPTIONS = ("input", "auto", "result", "derived", "one_hot", "hidden")
ACTIVE_OPTIONS = ("true", "false")
ZERO_FILL_POLICY_OPTIONS = ("disallow", "mode_missing_allowed")


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
            display_headers=_display_headers(REQUIRED_HEADERS),
            rows=tuple(_record_from_row(row) for row in catalog.rows),
            active_count=len(catalog.active_rows),
            catalog_validation=ValidationResult(
                scope="Catalog validation",
                errors=catalog_errors,
            ),
            project_validation=project_validation,
            field_options=_field_options(catalog),
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

    def export_records(
        self,
        records: tuple[FeatureCatalogRecord, ...],
        base_snapshot: FeatureCatalogSnapshot,
        destination: str | Path,
    ) -> FeatureCatalogExportResult:
        """Export current table records, including unsaved edits."""
        if self._export_writer is None:
            raise RuntimeError("Feature Catalog export writer is not configured.")

        rows = tuple(record.values for record in records)
        messages = _validation_messages_for_records(records, self._catalog_path)
        path = self._export_writer.write_export(destination, base_snapshot.headers, rows)
        return FeatureCatalogExportResult(
            path=path,
            row_count=len(records),
            validation_status="failed" if messages else "ok",
            validation_messages=messages or ("Catalog validation: OK",),
        )

    def build_draft_record(
        self,
        records: tuple[FeatureCatalogRecord, ...],
        request: FeatureCatalogDraftRequest,
    ) -> FeatureCatalogRecord:
        """Build a new draft record with generated order and ui_key."""
        order = _next_order(records)
        ui_key = ""
        if request.role in UI_VISIBLE_ROLES:
            ui_key = _unique_ui_key(_slug_key(request.ml_name), _existing_ui_keys(records))
        values = {
            "order": str(order),
            "ml_name": request.ml_name.strip(),
            "role": request.role.strip(),
            "ui_key": ui_key,
            "label": request.label.strip(),
            "source": request.source.strip(),
            "mapping_key": request.mapping_key.strip(),
            "one_hot_group": request.one_hot_group.strip(),
            "zero_fill_policy": request.zero_fill_policy.strip(),
            "active": "true" if request.active else "false",
            "notes": request.notes.strip(),
        }
        return FeatureCatalogRecord(
            values=tuple(values.get(header, "") for header in REQUIRED_HEADERS)
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
            message=f"Feature Catalog saved and reloaded. {SCHEMA_APPLY_MESSAGE}",
            schema_apply_required=True,
            schema_apply_message=SCHEMA_APPLY_MESSAGE,
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


def _display_headers(headers: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(DISPLAY_HEADERS.get(header, header) for header in headers)


def _field_options(catalog: FeatureCatalog) -> FeatureCatalogFieldOptions:
    sources = tuple(sorted({row.source for row in catalog.rows if row.source}))
    mapping_keys = tuple(sorted({row.mapping_key for row in catalog.rows if row.mapping_key}))
    one_hot_groups = tuple(
        sorted({row.one_hot_group for row in catalog.rows if row.one_hot_group})
    )
    return FeatureCatalogFieldOptions(
        {
            "role": ROLE_OPTIONS,
            "active": ACTIVE_OPTIONS,
            "zero_fill_policy": ZERO_FILL_POLICY_OPTIONS,
            "source": sources,
            "mapping_key": mapping_keys,
            "one_hot_group": one_hot_groups,
        }
    )


def _validation_messages_for_records(
    records: tuple[FeatureCatalogRecord, ...],
    catalog_path: Path,
) -> tuple[str, ...]:
    rows, conversion_errors = _rows_from_records(records)
    if conversion_errors:
        return tuple(f"Catalog validation: {error}" for error in conversion_errors)
    draft = FeatureCatalog(
        rows=tuple(sorted(rows, key=lambda row: row.order)),
        headers=REQUIRED_HEADERS,
        path=catalog_path,
    )
    errors = tuple(validate_feature_catalog(draft)) + tuple(
        validate_registry_references(draft, MODEL_REGISTRY)
    )
    return tuple(f"Catalog validation: {error}" for error in errors)


def _next_order(records: tuple[FeatureCatalogRecord, ...]) -> int:
    orders: list[int] = []
    order_col = REQUIRED_HEADERS.index("order")
    for record in records:
        try:
            orders.append(int(record.value_at(order_col)))
        except ValueError:
            continue
    if not orders:
        return 10
    return max(orders) + 10


def _existing_ui_keys(records: tuple[FeatureCatalogRecord, ...]) -> set[str]:
    ui_key_col = REQUIRED_HEADERS.index("ui_key")
    return {record.value_at(ui_key_col) for record in records if record.value_at(ui_key_col)}


def _slug_key(value: str) -> str:
    key = re.sub(r"[^0-9A-Za-z]+", "_", value.strip().lower()).strip("_")
    return key or "feature"


def _unique_ui_key(base: str, existing: set[str]) -> str:
    candidate = base
    suffix = 2
    while candidate in existing:
        candidate = f"{base}_{suffix}"
        suffix += 1
    return candidate


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
