"""Controller boundary for the Train Data Mapping panel."""

from __future__ import annotations

from pathlib import Path

from apps.train.application.data_mapping import (
    DataMappingNavigationRequest,
    DataMappingNavigationResult,
)
from apps.train.controllers.data_mapping.navigation import open_mapping_requirement
from apps.train.controllers.data_mapping.presentation import (
    DataMappingAttributeRow,
    DataMappingControllerState,
    DataMappingEntitySummary,
    DataMappingValueRow,
    display_source_label,
    error_state,
    exception_summary,
    missing_state,
    operation_issue,
    project_snapshot,
)
from apps.train.services.data_mapping_service import DataMappingService
from apps.train.services.data_mapping.legacy_bootstrap import DataMappingLegacyBootstrapPreview
from apps.train.services.data_mapping_types import (
    DataMappingCellEdit,
    DataMappingImportPreview,
    DataMappingSnapshot,
)
from core.mapping.entity_model import MappingValidationError
from core.mapping.exchange import MappingExchangeExportPlan

# Compatibility aliases for the existing focused controller contract.
_exception_summary = exception_summary
_display_source_label = display_source_label


class DataMappingController:
    """Coordinate Data Mapping service calls for the UI."""

    def __init__(self, service: DataMappingService | None = None) -> None:
        self._service = service or DataMappingService()

    def refresh(self, selected_entity_key: str = "") -> DataMappingControllerState:
        """Refresh derived state without replacing the service-owned draft."""
        resource_status = self._service.resource_status()
        try:
            snapshot = self._service.load_snapshot()
        except Exception as exc:
            if resource_status == "missing":
                return missing_state(
                    source_label=display_source_label(self._service.source_label),
                    bootstrap_enabled=self._service.legacy_bootstrap_available,
                )
            return error_state(
                "Unable to load mapping data.",
                source_label=display_source_label(self._service.source_label),
                detail_message=exception_summary(exc),
            )
        return self._state_from_snapshot(
            snapshot,
            selected_entity_key,
            resource_status=resource_status,
        )

    def resource_status(self) -> str:
        """Return mapping resource availability through the service boundary."""
        return self._service.resource_status()

    def open_requirement(
        self,
        request: DataMappingNavigationRequest,
        current_group_key: str = "",
    ) -> tuple[DataMappingControllerState, DataMappingNavigationResult]:
        """Refresh requirements and resolve one public navigation request."""
        return open_mapping_requirement(
            self._service,
            request,
            current_group_key,
            self.refresh,
        )

    def edit_cell(
        self,
        group_key: str,
        row_index: int,
        column: str,
        value: object,
    ) -> DataMappingControllerState:
        """Apply one cell edit and return refreshed state."""
        snapshot = self._service.edit_cell(group_key, row_index, column, value)
        return self._state_from_snapshot(snapshot, group_key)

    def edit_cells(
        self,
        group_key: str,
        edits: tuple[DataMappingCellEdit, ...],
    ) -> DataMappingControllerState:
        """Apply a grouped rectangular edit intent."""
        snapshot, result = self._service.edit_cells(group_key, edits)
        return self._state_from_snapshot(
            snapshot,
            group_key,
            message=result.message,
            operation_applied=result.applied,
            operation_blocked=result.blocked,
        )

    def undo(self, selected_group_key: str = "") -> DataMappingControllerState:
        """Undo the most recent service-owned draft command."""
        snapshot, result = self._service.undo()
        return self._state_from_snapshot(
            snapshot,
            selected_group_key,
            message=result.message,
            operation_applied=result.applied,
            operation_blocked=result.blocked,
        )

    def add_row(self, group_key: str) -> DataMappingControllerState:
        """Add one blank row and return refreshed state."""
        return self._state_from_snapshot(self._service.add_row(group_key), group_key)

    def duplicate_row(self, group_key: str, row_index: int) -> DataMappingControllerState:
        """Duplicate one row and return refreshed state."""
        return self._state_from_snapshot(
            self._service.duplicate_row(group_key, row_index),
            group_key,
        )

    def delete_row(self, group_key: str, row_index: int) -> DataMappingControllerState:
        """Delete one row and return refreshed state."""
        return self._state_from_snapshot(self._service.delete_row(group_key, row_index), group_key)

    def reload(self, selected_group_key: str = "") -> DataMappingControllerState:
        """Discard draft edits and reload from the provider."""
        try:
            snapshot = self._service.reload_snapshot()
        except Exception as exc:
            cached_snapshot = _safe_current_snapshot(self._service)
            if cached_snapshot is not None:
                summary = exception_summary(exc)
                return self._state_from_snapshot(
                    cached_snapshot,
                    selected_group_key,
                    status="error",
                    message="Reload failed. Current draft preserved.",
                    extra_issues=(
                        operation_issue(
                            "reload_failed",
                            "Reload",
                            "source",
                            f"Reload failed: {summary}",
                        ),
                    ),
                )
            if self._service.resource_status() == "missing":
                return missing_state(
                    source_label=display_source_label(self._service.source_label),
                    bootstrap_enabled=self._service.legacy_bootstrap_available,
                )
            return error_state(
                "Unable to reload mapping data.",
                source_label=display_source_label(self._service.source_label),
                detail_message=exception_summary(exc),
            )
        return self._state_from_snapshot(
            snapshot,
            selected_group_key,
            message="Reloaded from source.",
        )

    def save(self, selected_group_key: str = "") -> DataMappingControllerState:
        """Save the current draft and return refreshed state."""
        result, snapshot = self._service.save_mapping()
        if result.success:
            message = result.message
            if result.backup_path is not None:
                message = f"{message} Backup: {result.backup_path}."
            return self._state_from_snapshot(snapshot, selected_group_key, message=message)
        return self._state_from_snapshot(
            snapshot,
            selected_group_key,
            status="error",
            message="Save failed.",
            extra_issues=(operation_issue("save_failed", "Save", "file", result.message),),
        )

    def export_json(self, destination: str | Path) -> DataMappingControllerState:
        """Export the current draft as JSON and return current state."""
        return self.export_snapshot(destination, "json")

    def export_xlsx(self, destination: str | Path) -> DataMappingControllerState:
        """Export the current draft as XLSX and return current state."""
        return self.export_snapshot(destination, "xlsx")

    def export_snapshot(
        self,
        destination: str | Path,
        export_format: str,
        selected_group_key: str = "",
    ) -> DataMappingControllerState:
        """Export the current draft in the requested review snapshot format."""
        result, snapshot = self._service.export_snapshot(destination, export_format)
        if result.success:
            return self._state_from_snapshot(
                snapshot,
                selected_group_key,
                message="Exported.",
            )
        return self._state_from_snapshot(
            snapshot,
            selected_group_key,
            status="error",
            message="Export failed.",
            extra_issues=(
                operation_issue("export_failed", "Export", "file", result.message),
            ),
        )

    def plan_exchange_export(self, destination: str | Path) -> MappingExchangeExportPlan:
        """Return exchange targets and blockers without changing draft state."""
        return self._service.plan_exchange_export(destination)

    def export_exchange(
        self,
        destination: str | Path,
        selected_group_key: str = "",
    ) -> DataMappingControllerState:
        """Publish the current valid draft as an exchange package."""
        result, snapshot = self._service.export_exchange(destination)
        if result.success:
            return self._state_from_snapshot(
                snapshot,
                selected_group_key,
                message=result.message,
            )
        return self._state_from_snapshot(
            snapshot,
            selected_group_key,
            status="error",
            message="Exchange export failed.",
            extra_issues=(*result.issues, operation_issue(
                "exchange_export_failed",
                "Exchange Export",
                "destination",
                result.message,
            )),
        )

    def preview_legacy_bootstrap(
        self,
        source: str | Path,
    ) -> DataMappingLegacyBootstrapPreview:
        """Prepare a strict legacy-wide candidate without mutating Mapping state."""
        return self._service.preview_legacy_bootstrap(source)

    def apply_legacy_bootstrap(
        self,
        preview: DataMappingLegacyBootstrapPreview,
        selected_group_key: str = "",
        *,
        allow_replace_current: bool = False,
    ) -> DataMappingControllerState:
        """Install a fresh bootstrap candidate as an Unsaved Data Mapping draft."""
        snapshot, result = self._service.apply_legacy_bootstrap(
            preview, allow_replace_current=allow_replace_current
        )
        if result.success and snapshot is not None:
            return self._state_from_snapshot(
                snapshot,
                selected_group_key,
                message=result.message,
            )
        issue_code = (
            "legacy_bootstrap_stale"
            if result.stale
            else (
                "legacy_bootstrap_confirmation_required"
                if result.confirmation_required
                else "legacy_bootstrap_blocked"
            )
        )
        issue = operation_issue(
            issue_code,
            "Legacy Bootstrap",
            "source",
            result.message,
        )
        if snapshot is not None:
            return self._state_from_snapshot(
                snapshot,
                selected_group_key,
                status="error",
                message="Legacy bootstrap was not applied.",
                extra_issues=(issue,),
            )
        if self._service.resource_status() == "missing":
            return missing_state(
                source_label=display_source_label(self._service.source_label),
                bootstrap_enabled=self._service.legacy_bootstrap_available,
                message="Legacy bootstrap was not applied.",
                extra_issues=(issue,),
            )
        try:
            current = self._service.load_snapshot()
        except Exception as exc:
            return error_state(
                "Legacy bootstrap was not applied.",
                source_label=display_source_label(self._service.source_label),
                detail_message=exception_summary(exc),
            )
        return self._state_from_snapshot(
            current,
            selected_group_key,
            status="error",
            message="Legacy bootstrap was not applied.",
            extra_issues=(issue,),
        )

    def preview_exchange_import(
        self,
        source: str | Path,
    ) -> DataMappingImportPreview:
        """Prepare a Qt-free exchange preview without mutating controller state."""
        preview, _snapshot = self._service.preview_exchange_import(source)
        return preview

    def apply_exchange_import(
        self,
        preview: DataMappingImportPreview,
        selected_group_key: str = "",
    ) -> DataMappingControllerState:
        """Apply a prepared exchange candidate to the service-owned draft only."""
        snapshot, result = self._service.apply_exchange_import(preview)
        if result.success:
            return self._state_from_snapshot(
                snapshot,
                selected_group_key,
                message=result.message,
            )
        issue_code = "import_preview_stale" if result.stale else "import_apply_blocked"
        return self._state_from_snapshot(
            snapshot,
            selected_group_key,
            status="error",
            message="Import was not applied.",
            extra_issues=(
                operation_issue(
                    issue_code,
                    "Import",
                    "preview",
                    result.message,
                ),
            ),
        )

    def _state_from_snapshot(
        self,
        snapshot: DataMappingSnapshot,
        selected_group_key: str,
        *,
        status: str | None = None,
        message: str | None = None,
        extra_issues: tuple[MappingValidationError, ...] = (),
        resource_status: str | None = None,
        operation_applied: int = 0,
        operation_blocked: int = 0,
    ) -> DataMappingControllerState:
        resolved_resource_status = resource_status or self._service.resource_status()
        return project_snapshot(
            snapshot,
            selected_group_key,
            status=status,
            message=message,
            extra_issues=extra_issues,
            resource_status=resolved_resource_status,
            operation_applied=operation_applied,
            operation_blocked=operation_blocked,
        )

def _safe_current_snapshot(service: DataMappingService) -> DataMappingSnapshot | None:
    try:
        return service.current_snapshot()
    except Exception:
        return None
