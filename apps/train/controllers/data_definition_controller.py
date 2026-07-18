"""Controller boundary for the Train Data Definition panel."""

from __future__ import annotations

from dataclasses import replace

from apps.train.application.data_mapping import DataMappingNavigationRequest
from apps.train.application.data_mapping.handoff import build_saved_mapping_handoffs
from apps.train.application.data_definition import PreparedFeatureCommand
from apps.train.controllers.data_definition_state_builder import (
    DRAFT_FIELDS,
    DRAFT_HEADERS,
    DataDefinitionControllerState,
    DataDefinitionDraftCellState,
    error_state as _error_state,
    save_status as _save_status,
    state_from_report as _state_from_report,
)
from apps.train.controllers.derived_operand_projection import (
    DerivedOperandOption,
    project_derived_operand_options,
)
from apps.train.services.data_definition_service import DataDefinitionService
from core.data_definition import (
    AddDefinitionIntent,
    DataDefinitionCommandResult,
    DataDefinitionCommandIssue,
    DataDefinitionDraft,
    DuplicateDefinitionIntent,
    EditDefinitionIntent,
    FeatureCommandIntent,
    MoveDefinitionIntent,
    RemoveDefinitionIntent,
    RenameDefinitionIntent,
    SetDefinitionActiveIntent,
    DerivedCommandIntent,
)


class DataDefinitionController:
    """Coordinate Data Definition report and draft refresh for the UI."""

    def __init__(self, service: DataDefinitionService | None = None) -> None:
        if service is None:
            raise ValueError("DataDefinitionController requires an explicit service")
        self._service = service
        self._draft: DataDefinitionDraft | None = None
        self._draft_revision = 0
        self._saved_mapping_handoffs: tuple[DataMappingNavigationRequest, ...] = ()

    def refresh(self) -> DataDefinitionControllerState:
        """Return current Data Definition view state and reload the draft."""
        try:
            report = self._service.refresh_report()
            self._draft = self._service.refresh_draft()
            self._draft_revision += 1
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
            if result.accepted:
                self._draft_revision += 1
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

    def rename_definition(self, intent: RenameDefinitionIntent) -> DataDefinitionControllerState:
        return self._apply_command("rename", intent)

    def duplicate_definition(self, intent: DuplicateDefinitionIntent) -> DataDefinitionControllerState:
        return self._apply_command("duplicate", intent)

    def remove_definition(self, intent: RemoveDefinitionIntent) -> DataDefinitionControllerState:
        return self._apply_command("remove", intent)

    def set_definition_active(
        self,
        intent: SetDefinitionActiveIntent,
    ) -> DataDefinitionControllerState:
        return self._apply_command("active", intent)

    def move_definition(self, intent: MoveDefinitionIntent) -> DataDefinitionControllerState:
        return self._apply_command("move", intent)

    def preview_feature_command(self, intent: FeatureCommandIntent) -> PreparedFeatureCommand:
        """Preview a command while preserving the controller's current draft."""
        if self._draft is None:
            self._draft = self._service.load_draft()
            self._draft_revision += 1
        draft = self._draft
        report = self._service.refresh_report()
        return self._service.prepare_feature_command(
            draft,
            intent,
            source_revision=self._draft_revision,
            current_report=report,
        )

    def preview_derived_command(self, intent: DerivedCommandIntent) -> PreparedFeatureCommand:
        """Preview the exact restricted Derived transition."""
        if self._draft is None:
            self._draft = self._service.load_draft()
            self._draft_revision += 1
        report = self._service.refresh_report()
        return self._service.prepare_feature_command(
            self._draft,
            intent,
            source_revision=self._draft_revision,
            current_report=report,
        )

    def derived_operand_options(
        self,
        consumer_identity: str = "",
    ) -> tuple[DerivedOperandOption, ...]:
        """Return application-owned operand presentation for Add or Edit."""
        if self._draft is None:
            self._draft = self._service.load_draft()
            self._draft_revision += 1
        return project_derived_operand_options(
            self._draft,
            consumer_identity=consumer_identity,
        )

    def apply_prepared_derived_command(
        self,
        prepared: PreparedFeatureCommand,
    ) -> DataDefinitionControllerState:
        return self.apply_prepared_feature_command(prepared)

    def apply_prepared_feature_command(
        self,
        prepared: PreparedFeatureCommand,
    ) -> DataDefinitionControllerState:
        """Apply exactly the previewed result when its source revision is current."""
        draft = self._draft or self._service.load_draft()
        if (
            prepared.source_revision != self._draft_revision
            or prepared.source_generation_id != draft.base_generation_id
            or prepared.source_draft is not draft
        ):
            issue = DataDefinitionCommandIssue(
                "prepared_preview_stale",
                "draft",
                "This Impact Preview no longer matches the current draft.",
                "Open a new Impact Preview and confirm it again.",
            )
            result = DataDefinitionCommandResult(
                draft,
                False,
                None,
                prepared.result.action,
                (issue,),
            )
            return self._state_from_command_result(draft, result, "feature")
        return self._state_from_command_result(draft, prepared.result, "feature")

    def apply_feature_command(
        self,
        intent: FeatureCommandIntent,
    ) -> DataDefinitionControllerState:
        return self._apply_command("feature", intent)

    def _apply_command(
        self,
        operation: str,
        intent: FeatureCommandIntent,
    ) -> DataDefinitionControllerState:
        try:
            draft = self._draft or self._service.load_draft()
            result: DataDefinitionCommandResult = self._service.apply_feature_command(
                draft,
                intent,
            )
            return self._state_from_command_result(draft, result, operation)
        except Exception as exc:
            return self._error_state(exc)

    def _state_from_command_result(
        self,
        draft: DataDefinitionDraft,
        result: DataDefinitionCommandResult,
        operation: str,
    ) -> DataDefinitionControllerState:
        try:
            before_identities = tuple(row.identity for row in draft.rows)
            self._draft = result.draft
            if result.accepted:
                self._draft_revision += 1
            focus_identity = result.identity if result.accepted else None
            if result.accepted and (operation == "remove" or result.action == "Remove"):
                removed = result.affected_identities[0] if result.affected_identities else None
                if removed in before_identities:
                    index = before_identities.index(removed)
                    remaining = tuple(row.identity for row in self._draft.rows)
                    focus_identity = (
                        remaining[min(index, len(remaining) - 1)] if remaining else None
                    )
            report = self._service.refresh_report()
            return _state_from_report(
                report,
                self._draft,
                self._service.preview_save_plan(self._draft, current_report=report),
                message=result.message,
                status="draft_changed" if result.accepted and self._draft.is_changed else None,
                last_action_ok=result.accepted,
                focus_identity=focus_identity,
                command_issue_rows=tuple(
                    (
                        issue.code,
                        issue.field_name,
                        issue.message + (f" Next: {issue.resolution}" if issue.resolution else ""),
                    )
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
            self._draft_revision += 1
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
            changed_identities = {
                change.row_identity for change in draft.changes()
            }
            changed_identities.update(
                (row.source_kind, row.column_key)
                for row in draft.rows
                if row.identity in changed_identities and row.column_key
            )
            report_before = self._service.refresh_report()
            result = self._service.save_schema_draft(draft, current_report=report_before)
            if result.status == "written":
                self._draft = self._service.refresh_draft()
            else:
                self._draft = draft
            self._draft_revision += 1
            report_after = self._service.refresh_report()
            if result.status == "written":
                self._saved_mapping_handoffs = build_saved_mapping_handoffs(
                    report_after,
                    self._draft,
                    frozenset(changed_identities),
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
