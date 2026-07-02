"""Controller boundary for the Train Feature Catalog panel."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from apps.train.adapters.feature_catalog import FeatureCatalogFileAdapter
from apps.train.application.feature_catalog import (
    FeatureCatalogDraftRequest,
    FeatureCatalogExportResult,
    FeatureCatalogRecord,
    FeatureCatalogSaveResult,
    FeatureCatalogService,
    FeatureCatalogSnapshot,
)


@dataclass(frozen=True)
class FeatureCatalogControllerState:
    """UI-facing Feature Catalog load state."""

    snapshot: FeatureCatalogSnapshot | None
    status: str
    message: str


@dataclass(frozen=True)
class FeatureCatalogExportState:
    """UI-facing Feature Catalog export state."""

    result: FeatureCatalogExportResult | None
    status: str
    message: str


@dataclass(frozen=True)
class FeatureCatalogSaveState:
    """UI-facing Feature Catalog save state."""

    result: FeatureCatalogSaveResult | None
    status: str
    message: str


class FeatureCatalogController:
    """Coordinate Feature Catalog application service calls for the UI."""

    def __init__(self, service: FeatureCatalogService | None = None) -> None:
        self._service = service or FeatureCatalogService(
            export_writer=FeatureCatalogFileAdapter()
        )

    def refresh(self) -> FeatureCatalogControllerState:
        """Load the current catalog and return controlled UI state."""
        try:
            snapshot = self._service.load_snapshot(include_project_consistency=True)
        except Exception as exc:
            return FeatureCatalogControllerState(
                snapshot=None,
                status="error",
                message=f"Feature Catalog load failed: {exc}",
            )

        if snapshot.has_errors:
            return FeatureCatalogControllerState(
                snapshot=snapshot,
                status="error",
                message="Feature Catalog validation failed.",
            )
        return FeatureCatalogControllerState(
            snapshot=snapshot,
            status="ready",
            message="Feature Catalog validation OK.",
        )

    def export_csv(
        self,
        snapshot: FeatureCatalogSnapshot,
        destination: str | Path,
    ) -> FeatureCatalogExportState:
        """Export the current catalog snapshot to a user-selected CSV path."""
        try:
            result = self._service.export_snapshot(snapshot, destination)
        except Exception as exc:
            return FeatureCatalogExportState(
                result=None,
                status="error",
                message=f"Feature Catalog export failed: {exc}",
            )
        validation_text = (
            "validation OK"
            if result.validation_status == "ok"
            else "validation has errors"
        )
        return FeatureCatalogExportState(
            result=result,
            status="ready",
            message=f"Exported {result.row_count} rows to {result.path} ({validation_text}).",
        )

    def export_records(
        self,
        records: tuple[FeatureCatalogRecord, ...],
        base_snapshot: FeatureCatalogSnapshot,
        destination: str | Path,
    ) -> FeatureCatalogExportState:
        """Export current table records, including unsaved edits."""
        try:
            result = self._service.export_records(records, base_snapshot, destination)
        except Exception as exc:
            return FeatureCatalogExportState(
                result=None,
                status="error",
                message=f"Feature Catalog export failed: {exc}",
            )
        validation_text = (
            "validation OK"
            if result.validation_status == "ok"
            else "validation has errors"
        )
        return FeatureCatalogExportState(
            result=result,
            status="ready",
            message=f"Exported {result.row_count} rows to {result.path} ({validation_text}).",
        )

    def build_draft_record(
        self,
        records: tuple[FeatureCatalogRecord, ...],
        request: FeatureCatalogDraftRequest,
    ) -> FeatureCatalogRecord:
        """Build a new draft record through the application service."""
        return self._service.build_draft_record(records, request)

    def save_records(
        self,
        records: tuple[FeatureCatalogRecord, ...],
    ) -> FeatureCatalogSaveState:
        """Validate and save edited catalog records through the service."""
        try:
            result = self._service.save_records(records)
        except Exception as exc:
            return FeatureCatalogSaveState(
                result=None,
                status="error",
                message=f"Feature Catalog save failed: {exc}",
            )
        if not result.saved:
            return FeatureCatalogSaveState(
                result=result,
                status="error",
                message=result.message,
            )
        return FeatureCatalogSaveState(
            result=result,
            status="ready",
            message=result.message,
        )
