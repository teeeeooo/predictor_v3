"""Controller boundary for the Train Data Definition panel."""

from __future__ import annotations

from dataclasses import replace

from apps.train.application.data_mapping import DataMappingNavigationRequest
from apps.train.application.data_mapping.handoff import build_saved_mapping_handoffs
from apps.train.controllers.data_definition_state_builder import (
    DRAFT_FIELDS,
    DRAFT_HEADERS,
    DataDefinitionControllerState,
    DataDefinitionDraftCellState,
    error_state as _error_state,
    save_status as _save_status,
    state_from_report as _state_from_report,
)
from apps.train.services.data_definition_service import DataDefinitionService
from core.data_definition import (
    AddDefinitionIntent,
    DataDefinitionCommandResult,
    DataDefinitionDraft,
    EditDefinitionIntent,
)


class DataDefinitionController:
    """Coordinate Data Definition report and draft refresh for the UI."""

    def __init__(self, service: DataDefinitionService | None = None) -> None:
        self._service = service or DataDefinitionService()
        self._draft: DataDefinitionDraft | None = None
        self._saved_mapping_handoffs: tuple[DataMappingNavigationRequest, ...] = ()

    def refresh(self) -> DataDefinitionControllerState:
        """Return current Data Definition view state and reload the draft."""
        try:
            report = self._service.refresh_report()
            self._draft = self._service.refresh_draft()
        except Exception as exc:
            return self._error_state(exc)
        return _state_from_report(
            report,
            self._draft,
            self._service.preview_save_plan(self._draft, current_report=report),
            saved_mapping_handoffs=self._saved_mapping_handoffs,
        )

    def edit_cell(
        self,
        row_identity: tuple[str, str],
        field_name: str,
        value: object,
    ) -> DataDefinitionControllerState:
        """Apply one draft edit and return refreshed preview state."""
        try:
            draft = self._draft or self._service.load_draft()
            result = self._service.edit_draft_cell(draft, row_identity, field_name, value)
            self._draft = result.draft
            report = self._service.refresh_report()
            state = _state_from_report(
                report,
                self._draft,
                self._service.preview_save_plan(self._draft, current_report=report),
                message=result.message,
                status="draft_changed" if result.accepted and self._draft.is_changed else None,
                last_action_ok=result.accepted,
                saved_mapping_handoffs=self._saved_mapping_handoffs,
            )
        except Exception as exc:
            return self._error_state(exc)
        return state

    def add_definition(self, intent: AddDefinitionIntent) -> DataDefinitionControllerState:
        """Apply one controlled Add intent and return its projected draft state."""
        return self._apply_command("add", intent)

    def edit_definition(self, intent: EditDefinitionIntent) -> DataDefinitionControllerState:
        """Apply one controlled Edit intent and return its projected draft state."""
        return self._apply_command("edit", intent)

    def _apply_command(
        self,
        operation: str,
        intent: AddDefinitionIntent | EditDefinitionIntent,
    ) -> DataDefinitionControllerState:
        try:
            draft = self._draft or self._service.load_draft()
            result: DataDefinitionCommandResult = (
                self._service.add_definition(draft, intent)
                if operation == "add" and isinstance(intent, AddDefinitionIntent)
                else self._service.edit_definition(draft, intent)
                if operation == "edit" and isinstance(intent, EditDefinitionIntent)
                else raise_type_error(operation)
            )
            self._draft = result.draft
            report = self._service.refresh_report()
            return _state_from_report(
                report,
                self._draft,
                self._service.preview_save_plan(self._draft, current_report=report),
                message=result.message,
                status="draft_changed" if result.accepted and self._draft.is_changed else None,
                last_action_ok=result.accepted,
                focus_identity=result.identity if result.accepted else None,
                command_issue_rows=tuple(
                    (issue.code, issue.field_name, issue.message)
                    for issue in result.issues
                ),
                saved_mapping_handoffs=self._saved_mapping_handoffs,
            )
        except Exception as exc:
            return self._error_state(exc)

    def reset_draft(self) -> DataDefinitionControllerState:
        """Discard in-memory edits and reload draft state from the service."""
        try:
            report = self._service.refresh_report()
            self._draft = self._service.refresh_draft()
        except Exception as exc:
            return self._error_state(exc)
        return _state_from_report(
            report,
            self._draft,
            self._service.preview_save_plan(self._draft, current_report=report),
            message="Draft reset from schema.",
            saved_mapping_handoffs=self._saved_mapping_handoffs,
        )

    def save_schema(self) -> DataDefinitionControllerState:
        """Run the guarded schema save workflow and return updated UI state."""
        try:
            draft = self._draft or self._service.load_draft()
            changed_identities = frozenset(
                change.row_identity for change in draft.changes()
            )
            report_before = self._service.refresh_report()
            result = self._service.save_schema_draft(draft, current_report=report_before)
            if result.status == "written":
                self._draft = self._service.refresh_draft()
            else:
                self._draft = draft
            report_after = self._service.refresh_report()
            if result.status == "written":
                self._saved_mapping_handoffs = build_saved_mapping_handoffs(
                    report_after,
                    self._draft,
                    changed_identities,
                )
            plan = self._service.preview_save_plan(self._draft, current_report=report_after)
        except Exception as exc:
            return self._error_state(exc)
        return _state_from_report(
            report_after,
            self._draft,
            plan,
            message=result.message,
            status=_save_status(result),
            save_result=result,
            last_action_ok=result.status in {"written", "noop"},
            saved_mapping_handoffs=self._saved_mapping_handoffs,
        )

    def _error_state(self, exc: Exception) -> DataDefinitionControllerState:
        """Preserve the latest successful handoff across recoverable failures."""
        return replace(
            _error_state(exc),
            saved_mapping_handoffs=self._saved_mapping_handoffs,
        )


def raise_type_error(operation: str) -> DataDefinitionCommandResult:
    """Fail fast on an internal controller/intent routing mismatch."""
    raise TypeError(f"Invalid controlled command intent for operation: {operation}")
