"""Feature Catalog application service."""

from __future__ import annotations

from pathlib import Path

from core.ml.feature_catalog import (
    DEFAULT_CATALOG_PATH,
    REQUIRED_HEADERS,
    FeatureCatalogRow,
    load_feature_catalog,
    validate_feature_catalog,
    validate_registry_references,
)
from core.ml.registry import MODEL_REGISTRY

from apps.train.application.feature_catalog.models import (
    FeatureCatalogRecord,
    FeatureCatalogSnapshot,
    ValidationResult,
)


class FeatureCatalogService:
    """Load and validate the ML Feature Catalog for Train/Admin UI."""

    def __init__(self, catalog_path: str | Path | None = None) -> None:
        self._catalog_path = Path(catalog_path) if catalog_path is not None else DEFAULT_CATALOG_PATH

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


def _record_from_row(row: FeatureCatalogRow) -> FeatureCatalogRecord:
    return FeatureCatalogRecord(
        values=tuple(_display_value(row, header) for header in REQUIRED_HEADERS)
    )


def _display_value(row: FeatureCatalogRow, header: str) -> str:
    value = getattr(row, header)
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)
