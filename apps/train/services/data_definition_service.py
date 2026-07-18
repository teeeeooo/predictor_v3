"""Data Definition service for Train/Admin."""

from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path

from apps.train.application.data_definition import (
    DataDefinitionGenerationRepositoryPort,
    PreparedFeatureCommand,
)
from core.data_definition import (
    AddDefinitionIntent,
    DataDefinitionDraft,
    DataDefinitionCommandResult,
    DataDefinitionReport,
    DataDefinitionSchemaSaveResult,
    DataDefinitionSavePlan,
    DataDefinitionSaveBlocker,
    DataDefinitionRestartImpact,
    FeatureCommandIntent,
    FeatureImpactPreview,
    EditDefinitionIntent,
    DuplicateDefinitionIntent,
    MoveDefinitionIntent,
    RemoveDefinitionIntent,
    RenameDefinitionIntent,
    SetDefinitionActiveIntent,
    DerivedCommandIntent,
    apply_derived_command,
    apply_add_definition_command,
    apply_edit_definition_command,
    apply_duplicate_definition_command,
    apply_remove_definition_command,
    apply_rename_definition_command,
    apply_set_definition_active_command,
    apply_move_definition_command,
    build_data_definition_draft,
    build_data_definition_report,
    build_data_definition_save_plan,
    build_feature_impact_preview,
    field_editability,
    save_data_definition_schema_draft,
)
from core.data_definition.contract import candidate_manifest_from_draft, scoped_fingerprints
from core.data_definition.derived.intents import DERIVED_INTENT_TYPES
from core.data_definition.draft import replace_draft_row
from apps.train.services.data_definition_persistence_service import (
    DataDefinitionPersistenceService,
)

BOOLEAN_DRAFT_FIELDS = frozenset(
    {"visible", "required", "readonly", "model_input_enabled", "active"}
)


@dataclass(frozen=True)
class DataDefinitionDraftEditResult:
    """Service result for one in-memory draft edit."""

    draft: DataDefinitionDraft
    accepted: bool
    message: str


class DataDefinitionService:
    """Load and mutate in-memory Data Definition state."""

    def __init__(
        self,
        *,
        schema_path: str | Path | None = None,
        generation_repository: DataDefinitionGenerationRepositoryPort | None = None,
    ) -> None:
        if (schema_path is None) == (generation_repository is None):
            raise ValueError(
                "DataDefinitionService requires exactly one persistence owner: "
                "generation_repository or explicit schema_path"
            )
        self._schema_path = Path(schema_path) if schema_path is not None else None
        self._persistence = (
            DataDefinitionPersistenceService(generation_repository)
            if generation_repository is not None else None
        )

    @property
    def schema_path(self) -> Path:
        """Return the explicit schema path owned by the Train service."""
        return self._active_schema_path()

    def load_report(
        self,
        *,
        training_data_path: str | Path | None = None,
    ) -> DataDefinitionReport:
        """Return the current read-only Data Definition report."""
        return build_data_definition_report(
            schema_path=self._active_schema_path(),
            feature_catalog_path=(
                self._persistence.active_feature_catalog_path
                if self._persistence is not None else None
            ),
            training_data_path=training_data_path,
        )

    def refresh_report(
        self,
        *,
        training_data_path: str | Path | None = None,
    ) -> DataDefinitionReport:
        """Reload the report for refresh actions."""
        return self.load_report(training_data_path=training_data_path)

    def load_draft(self) -> DataDefinitionDraft:
        """Return an in-memory editable draft loaded from the schema owner path."""
        if self._persistence is not None:
            return self._persistence.load_draft()
        return build_data_definition_draft(schema_path=self._active_schema_path())

    def refresh_draft(self) -> DataDefinitionDraft:
        """Discard in-memory edits and reload the draft."""
        return self.load_draft()

    def edit_draft_cell(
        self,
        draft: DataDefinitionDraft,
        row_identity: tuple[str, str],
        field_name: str,
        value: object,
    ) -> DataDefinitionDraftEditResult:
        """Return a new draft after applying one UI-originated cell edit."""
        resolved_identity = draft.resolve_identity(row_identity)
        row = next((item for item in draft.rows if item.identity == resolved_identity), None)
        if row is None:
            return DataDefinitionDraftEditResult(
                draft,
                False,
                f"Draft row not found: {row_identity}",
            )
        if field_name == "ml_name":
            rename = self.rename_definition(
                draft,
                RenameDefinitionIntent(
                    resolved_identity,
                    ml_name=str(value),
                ),
            )
            return DataDefinitionDraftEditResult(
                rename.draft,
                rename.accepted,
                rename.message,
            )
        editability = field_editability(row, field_name)
        if not editability.editable:
            return DataDefinitionDraftEditResult(draft, False, editability.reason)
        coerced, error = _coerce_draft_value(field_name, value)
        if error:
            return DataDefinitionDraftEditResult(draft, False, error)
        updated = replace_draft_row(draft, resolved_identity, **{field_name: coerced})
        return DataDefinitionDraftEditResult(updated, True, "Draft cell updated.")

    def add_definition(
        self,
        draft: DataDefinitionDraft,
        intent: AddDefinitionIntent,
    ) -> DataDefinitionCommandResult:
        """Apply one complete controlled Add command without file writes."""
        return apply_add_definition_command(draft, intent)

    def edit_definition(
        self,
        draft: DataDefinitionDraft,
        intent: EditDefinitionIntent,
    ) -> DataDefinitionCommandResult:
        """Apply one complete controlled Edit command without file writes."""
        updates = dict(intent.updates)
        if (
            "column_key" in updates or "ml_name" in updates
        ) and not (set(updates) - {"label", "column_key", "ml_name"}):
            return apply_rename_definition_command(
                draft,
                RenameDefinitionIntent(
                    intent.identity,
                    label=str(updates["label"]) if "label" in updates else None,
                    column_key=(
                        str(updates["column_key"]) if "column_key" in updates else None
                    ),
                    ml_name=str(updates["ml_name"]) if "ml_name" in updates else None,
                ),
            )
        return apply_edit_definition_command(draft, intent)

    def rename_definition(
        self,
        draft: DataDefinitionDraft,
        intent: RenameDefinitionIntent,
    ) -> DataDefinitionCommandResult:
        return apply_rename_definition_command(draft, intent)

    def duplicate_definition(
        self,
        draft: DataDefinitionDraft,
        intent: DuplicateDefinitionIntent,
    ) -> DataDefinitionCommandResult:
        return apply_duplicate_definition_command(draft, intent)

    def remove_definition(
        self,
        draft: DataDefinitionDraft,
        intent: RemoveDefinitionIntent,
    ) -> DataDefinitionCommandResult:
        return apply_remove_definition_command(draft, intent)

    def set_definition_active(
        self,
        draft: DataDefinitionDraft,
        intent: SetDefinitionActiveIntent,
    ) -> DataDefinitionCommandResult:
        return apply_set_definition_active_command(draft, intent)

    def move_definition(
        self,
        draft: DataDefinitionDraft,
        intent: MoveDefinitionIntent,
    ) -> DataDefinitionCommandResult:
        return apply_move_definition_command(draft, intent)

    def apply_feature_command(
        self,
        draft: DataDefinitionDraft,
        intent: FeatureCommandIntent,
    ) -> DataDefinitionCommandResult:
        """Dispatch one controlled command without I/O."""
        if isinstance(intent, AddDefinitionIntent):
            return self.add_definition(draft, intent)
        if isinstance(intent, EditDefinitionIntent):
            return self.edit_definition(draft, intent)
        if isinstance(intent, RenameDefinitionIntent):
            return self.rename_definition(draft, intent)
        if isinstance(intent, DuplicateDefinitionIntent):
            return self.duplicate_definition(draft, intent)
        if isinstance(intent, RemoveDefinitionIntent):
            return self.remove_definition(draft, intent)
        if isinstance(intent, SetDefinitionActiveIntent):
            return self.set_definition_active(draft, intent)
        if isinstance(intent, MoveDefinitionIntent):
            return self.move_definition(draft, intent)
        raise TypeError(f"Unsupported Feature command intent: {type(intent).__name__}")

    def apply_derived_command(
        self,
        draft: DataDefinitionDraft,
        intent: DerivedCommandIntent,
    ) -> DataDefinitionCommandResult:
        """Dispatch one restricted Derived command without I/O."""
        return apply_derived_command(draft, intent)

    def preview_feature_command(
        self,
        draft: DataDefinitionDraft,
        intent: FeatureCommandIntent,
        *,
        current_report: DataDefinitionReport | None = None,
    ) -> FeatureImpactPreview:
        """Preview the exact hypothetical command without changing draft state."""
        return self.prepare_feature_command(
            draft,
            intent,
            source_revision=0,
            current_report=current_report,
        ).preview

    def prepare_feature_command(
        self,
        draft: DataDefinitionDraft,
        intent: FeatureCommandIntent | DerivedCommandIntent,
        *,
        source_revision: int,
        current_report: DataDefinitionReport | None = None,
    ) -> PreparedFeatureCommand:
        """Execute once and retain the exact immutable transition for approval."""
        result = (
            self.apply_derived_command(draft, intent)
            if isinstance(intent, DERIVED_INTENT_TYPES)
            else self.apply_feature_command(draft, intent)
        )
        report = current_report or self.load_report()
        plan = self.preview_save_plan(result.draft, current_report=report)
        base = draft.base_manifest if hasattr(draft.base_manifest, "features") else None
        preview = build_feature_impact_preview(
            base,
            result,
            plan,
            source_draft=draft,
        )
        return PreparedFeatureCommand(
            source_revision,
            draft.base_generation_id,
            draft,
            result,
            preview,
        )

    def preview_save_plan(
        self,
        draft: DataDefinitionDraft,
        *,
        current_report: DataDefinitionReport | None = None,
    ) -> DataDefinitionSavePlan:
        """Build the current draft save-plan preview without writing files."""
        report = current_report or self.load_report()
        plan = build_data_definition_save_plan(draft, current_report=report)
        return self._canonical_save_impact(draft, plan)

    def save_schema_draft(
        self,
        draft: DataDefinitionDraft,
        *,
        current_report: DataDefinitionReport | None = None,
    ) -> DataDefinitionSchemaSaveResult:
        """Save the draft through the guarded schema writer."""
        report = current_report or self.load_report()
        save_plan = self.preview_save_plan(draft, current_report=report)
        if self._persistence is not None:
            return self._persistence.save(draft, save_plan)
        return save_data_definition_schema_draft(
            draft,
            self._legacy_schema_path(),
            save_plan=save_plan,
        )

    def _active_schema_path(self) -> Path:
        if self._persistence is not None:
            return self._persistence.active_schema_path
        return self._legacy_schema_path()

    def _legacy_schema_path(self) -> Path:
        if self._schema_path is None:
            raise RuntimeError("legacy schema path is unavailable in canonical mode")
        return self._schema_path

    def _canonical_save_impact(
        self,
        draft: DataDefinitionDraft,
        plan: DataDefinitionSavePlan,
    ) -> DataDefinitionSavePlan:
        """Expose Phase 4B compatibility protection in the pre-write UI plan."""
        if self._persistence is None or not draft.is_changed or draft.base_manifest is None:
            return plan
        try:
            candidate = candidate_manifest_from_draft(draft, draft.base_manifest)
            changed = (
                scoped_fingerprints(draft.base_manifest).model_compatibility
                != scoped_fingerprints(candidate).model_compatibility
            )
        except (KeyError, ValueError):
            return plan
        if not changed:
            return plan
        blockers = plan.blocked_reasons
        if not any(item.code == "model_compatibility_migration_required" for item in blockers):
            blockers = (*blockers, DataDefinitionSaveBlocker(
                "model_compatibility_migration_required",
                "error",
                "Ordered ML/model compatibility changed; complete retraining or consumer migration before publication.",
                "model_artifact",
            ))
        return replace(
            plan,
            can_save_schema=False,
            requires_retrain=True,
            blocked_reasons=blockers,
            restart_impact=DataDefinitionRestartImpact(
                requires_restart=plan.requires_restart,
                requires_retrain=True,
                message=(
                    "Schema restart and model retrain are required before activation."
                    if plan.requires_restart
                    else "Model retraining or consumer migration is required before publication."
                ),
            ),
        )


def _coerce_draft_value(field_name: str, value: object) -> tuple[object, str]:
    if field_name not in BOOLEAN_DRAFT_FIELDS:
        return "" if value is None else str(value), ""
    if isinstance(value, bool):
        return value, ""
    text = "" if value is None else str(value).strip().lower()
    if text in {"true", "1", "yes", "y"}:
        return True, ""
    if text in {"false", "0", "no", "n", ""}:
        return False, ""
    return value, f"{field_name} must be true or false."
