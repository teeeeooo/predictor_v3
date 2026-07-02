"""I/O DTOs for Feature Catalog export and save workflows."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from apps.train.application.feature_catalog.models import FeatureCatalogSnapshot


class FeatureCatalogExportWriter(Protocol):
    """Writer protocol for Feature Catalog file adapters."""

    def write_export(
        self,
        path: str | Path,
        headers: tuple[str, ...],
        rows: tuple[tuple[str, ...], ...],
    ) -> Path:
        """Write export rows and return the resolved destination path."""
        ...

    def write_canonical(
        self,
        path: str | Path,
        headers: tuple[str, ...],
        rows: tuple[tuple[str, ...], ...],
    ) -> Path:
        """Safely write canonical rows and return the resolved path."""
        ...


@dataclass(frozen=True)
class FeatureCatalogExportResult:
    """Result of exporting a Feature Catalog snapshot."""

    path: Path
    row_count: int
    validation_status: str
    validation_messages: tuple[str, ...]


@dataclass(frozen=True)
class FeatureCatalogSaveResult:
    """Result of attempting to save Feature Catalog records."""

    saved: bool
    snapshot: FeatureCatalogSnapshot | None
    errors: tuple[str, ...]
    message: str
    schema_apply_required: bool = False
    schema_apply_message: str = ""
