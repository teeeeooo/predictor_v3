"""Data Mapping Manager service for Train/Admin."""

from __future__ import annotations

from pathlib import Path

from core.data_definition.mapping_requirement_contract import (
    EffectiveMappingRequirement,
    MappingRequirementConflict,
    MappingRequirementContractResolution,
    resolve_mapping_requirement_contracts,
)
from core.mapping.editor_commands import (
    add_draft_row,
    delete_draft_row,
    duplicate_draft_row,
    set_draft_cell,
)
from core.mapping.editor_export import (
    MappingEditorExportResult,
    export_mapping_editor_snapshot_json,
    export_mapping_editor_snapshot_xlsx,
)
from core.mapping.editor_model import MappingEditorDraft, MappingEditorValidationResult
from core.mapping.editor_projection import (
    apply_effective_mapping_requirements_to_editor_draft,
    load_runtime_mapping_editor_draft,
    project_runtime_mapping_to_editor_draft,
)
from core.mapping.editor_persistence import MappingEditorSaveResult, save_mapping_editor_draft
from core.mapping.editor_validation import validate_mapping_editor_draft
from core.mapping.entity_runtime_adapter import runtime_mapping_source_label
from core.mapping.entity_model import MappingValidationError
from core.mapping.exchange import (
    MappingExchangeExportPlan,
    MappingExchangeExportResult,
    diff_mapping_exchange_drafts,
    exchange_draft_structure_issues,
    export_mapping_exchange,
    parse_mapping_exchange_bundle,
    plan_mapping_exchange_export,
)
from core.mapping.paths import MAPPING_JSON_FILE
from core.data_definition import MappingRequirement, build_data_definition_report
from apps.train.services.data_mapping_types import (
    DataMappingAction,
    DataMappingCellEdit,
    DataMappingImportApplyResult,
    DataMappingImportPreview,
    DataMappingMutationResult,
    DataMappingSnapshot,
    MappingDraftProvider,
)
from apps.train.services.data_mapping.draft_session import DataMappingDraftSession
from core.mapping.condenser_identity import condenser_requires_pi
from core.mapping.value_policy import canonicalize_mapping_cell_input


class FoundationMappingCatalogProvider:
    """Small sample provider for UI wiring tests only.

    It is not a production data source and does not read or write mapping.json.
    """

    source_label = "Foundation sample provider for UI wiring tests only"

    def load_draft(self) -> MappingEditorDraft:
        """Return a small valid draft used by Data Mapping UI tests."""
        return project_runtime_mapping_to_editor_draft(
            {
                "idu": {"IDU-A": {"ID Volume": 1.25, "Size": "S1"}},
                "evap_index": {
                    "EVAP-A": {"Size": "S1", "Evap Area": 8.2, "Evap Volume": 2.1}
                },
                "odu": {"ODU-A": {"OD Volume": 2.5}},
                "compressor": {"CMP-A": {"Comp EER": 3.2, "Comp cc": 11}},
                "ref_type": {"R32": {}, "R410A": {}},
                "exp_type": {"EEV": {}, "Capi": {}},
                "odu_cascade": {
                    "ODU-A": {
                        "Available_Fins": ["F&T"],
                        "Available_Pis": ["7"],
                        "Available_Rows": ["1"],
                    }
                },
                "cond_specs": {
                    "ODU-A F&T 7 1": {"Cond Area": 3.5, "Cond Volume": 4.5}
                },
            },
            source_label=self.source_label,
        )


class RuntimeMappingCatalogProvider:
    """Read-only provider backed by the existing runtime mapping repository."""

    def __init__(self, mapping_file: str | None = None) -> None:
        self._mapping_file = mapping_file

    @property
    def source_label(self) -> str:
        """Return the runtime mapping source displayed by the UI."""
        return runtime_mapping_source_label(self._mapping_file)

    @property
    def mapping_file(self) -> str:
        """Return the writable runtime mapping path."""
        return self._mapping_file or MAPPING_JSON_FILE

    def load_draft(self) -> MappingEditorDraft:
        """Return the current runtime mapping data as editor draft groups."""
        return load_runtime_mapping_editor_draft(self._mapping_file)


class DataDefinitionMappingRequirementProvider:
    """Read Data Definition mapping requirements for Data Mapping UI projection."""

    def __init__(self, schema_path: str | Path | None = None) -> None:
        self._schema_path = schema_path

    def load_mapping_requirements(self) -> tuple[MappingRequirement, ...]:
        """Return current Data Definition mapping requirements."""
        return build_data_definition_report(
            schema_path=self._schema_path,
        ).mapping_requirements


class EmptyMappingRequirementProvider:
    """No-op requirement provider for explicit test/custom draft providers."""

    def load_mapping_requirements(self) -> tuple[MappingRequirement, ...]:
        """Return no dynamic requirements."""
        return ()


class DataMappingService:
    """Provide editable Data Mapping Manager draft snapshots for Train/Admin UI."""

    def __init__(
        self,
        provider: MappingDraftProvider | None = None,
        mapping_requirement_provider: DataDefinitionMappingRequirementProvider | None = None,
    ) -> None:
        self._provider = provider or RuntimeMappingCatalogProvider()
        default_requirement_provider = (
            DataDefinitionMappingRequirementProvider()
            if provider is None else EmptyMappingRequirementProvider()
        )
        self._mapping_requirement_provider = mapping_requirement_provider or default_requirement_provider
        self._session = DataMappingDraftSession()
        self._runtime_requirements: tuple[MappingRequirement, ...] | None = None

    @property
    def source_label(self) -> str:
        """Return the configured provider source label before loading."""
        return self._provider.source_label

    def resource_status(self) -> str:
        """Return whether the configured runtime mapping resource exists."""
        mapping_file = getattr(self._provider, "mapping_file", None)
        if not mapping_file:
            return "available"
        return "exists" if Path(mapping_file).is_file() else "missing"

    @property
    def draft_revision(self) -> int:
        return self._session.revision

    @property
    def is_dirty(self) -> bool:
        return self._session.dirty

    def activate_initial_requirements(
        self, requirements: tuple[MappingRequirement, ...]
    ) -> None:
        """Bind startup requirements before the first Mapping draft is loaded."""
        if self._session.draft is not None:
            raise RuntimeError("initial Mapping requirements must be bound before load")
        self._runtime_requirements = requirements

    def preview_requirement_projection(
        self,
        requirements: tuple[MappingRequirement, ...],
    ) -> DataMappingSnapshot:
        """Project candidate requirements without mutating draft, baseline, or history."""
        current = self._session.draft
        if current is None:
            current = self._provider.load_draft()
        resolution = resolve_mapping_requirement_contracts(requirements)
        projected = apply_effective_mapping_requirements_to_editor_draft(
            current, resolution.contracts
        )
        return self._snapshot_without_session(projected, requirements, resolution)

    def commit_requirement_projection(
        self,
        requirements: tuple[MappingRequirement, ...],
        *,
        expected_revision: int,
    ) -> tuple[object, DataMappingSnapshot]:
        """Install a prepared clean projection after the coordinator stale guard."""
        if self._session.revision != expected_revision:
            raise ValueError("mapping draft revision changed after prepare")
        prior = self._session.state_token(), self._runtime_requirements
        snapshot = self.preview_requirement_projection(requirements)
        baseline = self._session.baseline
        projected_baseline = (
            apply_effective_mapping_requirements_to_editor_draft(
                baseline, resolve_mapping_requirement_contracts(requirements).contracts
            )
            if baseline is not None else snapshot.draft
        )
        self._session.project(snapshot.draft, projected_baseline)
        self._runtime_requirements = requirements
        return prior, self._snapshot(snapshot.draft, requirements)

    def rollback_requirement_projection(self, token: object) -> None:
        session_token, runtime_requirements = token
        draft, baseline, history = session_token
        self._session.restore(draft, baseline, history)
        self._runtime_requirements = runtime_requirements

    def discard_dirty_draft(self) -> DataMappingSnapshot:
        """Explicit reconciliation action that reloads concrete values."""
        return self.reload_snapshot()

    def load_snapshot(self) -> DataMappingSnapshot:
        """Return draft data, validation result, and disabled future actions."""
        requirements = self._load_mapping_requirements()
        resolution = resolve_mapping_requirement_contracts(requirements)
        if self._session.draft is None:
            draft = apply_effective_mapping_requirements_to_editor_draft(
                self._provider.load_draft(),
                resolution.contracts,
            )
            self._session.reset(draft)
            return self._snapshot(draft, requirements, resolution)
        draft = apply_effective_mapping_requirements_to_editor_draft(
            self._session.draft,
            resolution.contracts,
        )
        baseline = self._session.baseline
        projected_baseline = (
            apply_effective_mapping_requirements_to_editor_draft(
                baseline,
                resolution.contracts,
            )
            if baseline is not None
            else draft
        )
        self._session.project(
            draft,
            projected_baseline,
            history_projector=lambda item: (
                apply_effective_mapping_requirements_to_editor_draft(
                    item,
                    resolution.contracts,
                )
            ),
        )
        return self._snapshot(draft, requirements, resolution)

    def current_snapshot(self) -> DataMappingSnapshot | None:
        """Return the service-owned draft without reading the provider."""
        if self._session.draft is None:
            return None
        requirements = self._load_mapping_requirements()
        resolution = resolve_mapping_requirement_contracts(requirements)
        draft = apply_effective_mapping_requirements_to_editor_draft(
            self._session.draft,
            resolution.contracts,
        )
        baseline = self._session.baseline
        projected_baseline = (
            apply_effective_mapping_requirements_to_editor_draft(
                baseline,
                resolution.contracts,
            )
            if baseline is not None
            else draft
        )
        self._session.project(
            draft,
            projected_baseline,
            history_projector=lambda item: (
                apply_effective_mapping_requirements_to_editor_draft(
                    item,
                    resolution.contracts,
                )
            ),
        )
        return self._snapshot(draft, requirements, resolution)

    def reload_snapshot(self) -> DataMappingSnapshot:
        """Discard draft edits and reload from the provider."""
        requirements = self._load_mapping_requirements()
        resolution = resolve_mapping_requirement_contracts(requirements)
        draft = apply_effective_mapping_requirements_to_editor_draft(
            self._provider.load_draft(),
            resolution.contracts,
        )
        self._session.reset(draft)
        return self._snapshot(draft, requirements, resolution)

    def edit_cell(
        self,
        group_key: str,
        row_index: int,
        column: str,
        value: object,
    ) -> DataMappingSnapshot:
        """Apply one cell edit to the current draft."""
        snapshot, _result = self.edit_cells(
            group_key,
            (DataMappingCellEdit(row_index, column, value),),
        )
        return snapshot

    def edit_cells(
        self,
        group_key: str,
        edits: tuple[DataMappingCellEdit, ...],
    ) -> tuple[DataMappingSnapshot, DataMappingMutationResult]:
        """Apply one cell or rectangular batch as one undoable command."""
        draft = self.load_snapshot().draft
        next_draft = draft
        applied = 0
        blocked = 0
        for edit in edits:
            if not _cell_is_mutable(next_draft, group_key, edit.row_index, edit.column):
                blocked += 1
                continue
            group = next_draft.group(group_key)
            canonical_value = canonicalize_mapping_cell_input(group, edit.column, edit.value)
            candidate = set_draft_cell(
                next_draft,
                group_key,
                edit.row_index,
                edit.column,
                canonical_value,
            )
            if candidate != next_draft:
                applied += 1
                next_draft = candidate
        snapshot = self._store_command_result(draft, next_draft)
        message = _mutation_message(applied, blocked)
        return snapshot, DataMappingMutationResult(applied, blocked, message)

    def add_row(self, group_key: str) -> DataMappingSnapshot:
        """Append one blank row to a group."""
        draft = self.load_snapshot().draft
        return self._store_command_result(draft, add_draft_row(draft, group_key))

    def duplicate_row(self, group_key: str, row_index: int) -> DataMappingSnapshot:
        """Duplicate one group row."""
        draft = self.load_snapshot().draft
        return self._store_command_result(
            draft,
            duplicate_draft_row(draft, group_key, row_index),
        )

    def delete_row(self, group_key: str, row_index: int) -> DataMappingSnapshot:
        """Delete one group row."""
        draft = self.load_snapshot().draft
        return self._store_command_result(draft, delete_draft_row(draft, group_key, row_index))

    def undo(self) -> tuple[DataMappingSnapshot, DataMappingMutationResult]:
        """Restore the previous draft for the most recent user intent."""
        current = self.load_snapshot().draft
        restored = self._session.undo()
        if restored is None:
            return self._snapshot(current, self._load_mapping_requirements()), DataMappingMutationResult(
                message="Nothing to undo."
            )
        return self._snapshot(
            restored,
            self._load_mapping_requirements(),
        ), DataMappingMutationResult(applied=1, message="Undid the last change.")

    def save_mapping(self) -> tuple[MappingEditorSaveResult, DataMappingSnapshot]:
        """Save the current valid draft to runtime mapping JSON."""
        snapshot = self.load_snapshot()
        draft = snapshot.draft
        mapping_file = getattr(self._provider, "mapping_file", None)
        if not snapshot.validation_result.save_enabled:
            result = MappingEditorSaveResult(
                success=False,
                path=Path(mapping_file or ""),
                message="Resolve Issues before saving.",
            )
            return result, snapshot
        if not mapping_file:
            result = MappingEditorSaveResult(
                success=False,
                path=Path(""),
                message="No writable mapping file is configured.",
            )
            return result, snapshot
        result = save_mapping_editor_draft(draft, mapping_file)
        if result.success:
            self._session.mark_saved()
        return result, self._snapshot(draft, self._load_mapping_requirements())

    def export_snapshot(
        self,
        destination: str | Path,
        export_format: str = "json",
    ) -> tuple[MappingEditorExportResult, DataMappingSnapshot]:
        """Export the current draft as a read-only review snapshot."""
        snapshot = self.load_snapshot()
        if export_format == "xlsx":
            result = export_mapping_editor_snapshot_xlsx(
                snapshot.draft,
                snapshot.validation_errors,
                destination,
            )
        elif export_format == "json":
            result = export_mapping_editor_snapshot_json(
                snapshot.draft,
                snapshot.validation_errors,
                destination,
            )
        else:
            result = MappingEditorExportResult(
                success=False,
                path=Path(destination),
                message=f"Export failed: unsupported format '{export_format}'.",
            )
        return result, snapshot

    def plan_exchange_export(self, destination: str | Path) -> MappingExchangeExportPlan:
        """Calculate exchange targets and validation without writing files."""
        snapshot = self.load_snapshot()
        return plan_mapping_exchange_export(
            snapshot.draft,
            destination,
            snapshot.validation_errors,
        )

    def export_exchange(
        self,
        destination: str | Path,
    ) -> tuple[MappingExchangeExportResult, DataMappingSnapshot]:
        """Export the current service-owned draft as an exchange package."""
        snapshot = self.load_snapshot()
        result = export_mapping_exchange(
            snapshot.draft,
            destination,
            snapshot.validation_errors,
        )
        return result, snapshot

    def preview_exchange_import(
        self,
        source: str | Path,
    ) -> tuple[DataMappingImportPreview, DataMappingSnapshot]:
        """Parse an exchange file and prepare a non-mutating change preview."""
        snapshot = self.load_snapshot()
        source_path = Path(source)
        try:
            payload = source_path.read_bytes()
        except Exception as exc:
            blocker = MappingValidationError(
                code="import_source_read_failed",
                message=f"Unable to read import file '{source_path}': {exc}",
                entity_key="Import",
                field="source",
            )
            return (
                DataMappingImportPreview(
                    source_path=source_path,
                    format_version="",
                    blockers=(blocker,),
                    base_draft=snapshot.draft,
                ),
                snapshot,
            )
        parsed = parse_mapping_exchange_bundle(payload, snapshot.draft)
        candidate_blockers = (
            self._validate_draft(parsed.candidate).issues
            if parsed.candidate is not None
            else ()
        )
        candidate = parsed.candidate if not candidate_blockers else None
        diffs = (
            diff_mapping_exchange_drafts(snapshot.draft, candidate)
            if candidate is not None
            else ()
        )
        return (
            DataMappingImportPreview(
                source_path=source_path,
                format_version=parsed.format_version,
                group_diffs=diffs,
                blockers=(*parsed.blockers, *candidate_blockers),
                warnings=parsed.warnings,
                candidate=candidate,
                base_draft=snapshot.draft,
            ),
            snapshot,
        )

    def apply_exchange_import(
        self,
        preview: DataMappingImportPreview,
    ) -> tuple[DataMappingSnapshot, DataMappingImportApplyResult]:
        """Apply one fresh valid candidate as one grouped draft undo command."""
        snapshot = self.load_snapshot()
        if preview.base_draft != snapshot.draft:
            return snapshot, DataMappingImportApplyResult(
                success=False,
                stale=True,
                message="Import preview is stale. Review the current draft and import again.",
            )
        if not preview.can_apply or preview.candidate is None:
            return snapshot, DataMappingImportApplyResult(
                success=False,
                message="Import is blocked; review the listed issues first.",
            )
        candidate_issues = self._validate_draft(preview.candidate).issues
        if candidate_issues:
            issue = candidate_issues[0]
            return snapshot, DataMappingImportApplyResult(
                success=False,
                message=f"Import candidate is invalid ({issue.code}): {issue.message}",
            )
        if preview.candidate == snapshot.draft:
            return snapshot, DataMappingImportApplyResult(
                success=True,
                message="Import matches the current draft; no changes were applied.",
            )
        stored = self._session.store_command(snapshot.draft, preview.candidate)
        applied = self._snapshot(stored, self._load_mapping_requirements())
        return applied, DataMappingImportApplyResult(
            success=True,
            changed=True,
            message="Imported into the Unsaved draft. Review the changes, then use Save.",
        )

    def _store_command_result(
        self,
        previous: MappingEditorDraft,
        next_draft: MappingEditorDraft,
    ) -> DataMappingSnapshot:
        stored = self._session.store_command(previous, next_draft)
        return self._snapshot(stored, self._load_mapping_requirements())

    def _snapshot(
        self,
        draft: MappingEditorDraft,
        requirements: tuple[MappingRequirement, ...],
        resolution: MappingRequirementContractResolution | None = None,
    ) -> DataMappingSnapshot:
        resolution = resolution or resolve_mapping_requirement_contracts(requirements)
        validation_result = self._validate_draft(draft, requirements, resolution)
        return DataMappingSnapshot(
            draft=draft,
            validation_errors=validation_result.issues,
            validation_result=validation_result,
            source_label=self.source_label,
            actions=_future_actions(
                validation_result.save_enabled,
                can_save=bool(getattr(self._provider, "mapping_file", None)),
                exchange_enabled=(
                    validation_result.save_enabled
                    and not exchange_draft_structure_issues(draft)
                ),
            ),
            dirty=self._session.dirty,
            mapping_requirements=requirements,
            effective_mapping_requirements=resolution.contracts,
            mapping_requirement_conflicts=resolution.conflicts,
        )

    def _snapshot_without_session(
        self,
        draft: MappingEditorDraft,
        requirements: tuple[MappingRequirement, ...],
        resolution: MappingRequirementContractResolution,
    ) -> DataMappingSnapshot:
        validation_result = self._validate_draft(draft, requirements, resolution)
        return DataMappingSnapshot(
            draft=draft,
            validation_errors=validation_result.issues,
            validation_result=validation_result,
            source_label=self.source_label,
            actions=(),
            dirty=self._session.dirty,
            mapping_requirements=requirements,
            effective_mapping_requirements=resolution.contracts,
            mapping_requirement_conflicts=resolution.conflicts,
        )

    def _load_mapping_requirements(self) -> tuple[MappingRequirement, ...]:
        if self._runtime_requirements is not None:
            return self._runtime_requirements
        return self._mapping_requirement_provider.load_mapping_requirements()

    def _validate_draft(
        self,
        draft: MappingEditorDraft,
        requirements: tuple[MappingRequirement, ...] | None = None,
        resolution: MappingRequirementContractResolution | None = None,
    ) -> MappingEditorValidationResult:
        requirements = (
            requirements
            if requirements is not None
            else self._load_mapping_requirements()
        )
        resolution = resolution or resolve_mapping_requirement_contracts(requirements)
        validation_result = validate_mapping_editor_draft(draft)
        requirement_issues = (
            *_missing_requirement_group_issues(draft, resolution.contracts),
            *_requirement_conflict_issues(resolution.conflicts),
        )
        if not requirement_issues:
            return validation_result
        return type(validation_result)(
            issues=(*validation_result.issues, *requirement_issues)
        )


def _missing_requirement_group_issues(
    draft: MappingEditorDraft,
    requirements: tuple[EffectiveMappingRequirement, ...],
) -> tuple[MappingValidationError, ...]:
    return tuple(
        MappingValidationError(
            code="required_mapping_group_missing",
            message=f"{requirement.mapping_entity} mapping group is required.",
            entity_key=requirement.resolved_group_key,
            attribute_key=requirement.mapping_attribute,
            field=requirement.mapping_attribute,
        )
        for requirement in requirements
        if draft.group(requirement.resolved_group_key) is None
    )


def _requirement_conflict_issues(
    conflicts: tuple[MappingRequirementConflict, ...],
) -> tuple[MappingValidationError, ...]:
    return tuple(
        MappingValidationError(
            code="mapping_requirement_contract_conflict",
            message=conflict.message,
            entity_key=conflict.resolved_group_key,
            attribute_key=conflict.mapping_attribute,
            field=conflict.mapping_attribute,
            related_definition_keys=conflict.definition_column_keys,
        )
        for conflict in conflicts
    )


def _future_actions(
    save_enabled: bool = False,
    *,
    can_save: bool = False,
    exchange_enabled: bool | None = None,
) -> tuple[DataMappingAction, ...]:
    if exchange_enabled is None:
        exchange_enabled = save_enabled
    return (
        DataMappingAction(
            "export_csv_v2",
            "Export",
            True,
            "Export a read-only review snapshot. It cannot be imported back.",
        ),
        DataMappingAction(
            "export_mapping_exchange",
            "Mapping Exchange Package",
            exchange_enabled,
            "Resolve Issues or restore the seven exchange groups before exporting."
            if not exchange_enabled
            else "Export the current valid draft as a mapping exchange package.",
        ),
        DataMappingAction(
            "import_mapping_bundle",
            "Import Bundle…",
            True,
            "Import a sectioned mapping_bundle_v1 as an Unsaved draft after preview.",
        ),
        DataMappingAction(
            "save_mapping_json",
            "Save",
            save_enabled and can_save,
            _save_disabled_reason(save_enabled, can_save),
        ),
        DataMappingAction(
            "reload_runtime",
            "Reload",
            True,
            "Read the mapping source again; unsaved changes may be discarded.",
        ),
    )


def _save_disabled_reason(save_enabled: bool, can_save: bool) -> str:
    if not can_save:
        return "No writable mapping file is configured."
    if not save_enabled:
        return "Resolve Issues before saving."
    return ""


def _cell_is_mutable(
    draft: MappingEditorDraft,
    group_key: str,
    row_index: int,
    column: str,
) -> bool:
    group = draft.group(group_key)
    if group is None or column not in group.columns or not 0 <= row_index < len(group.rows):
        return False
    if group_key == "odu_cond_specs" and column == "Pi":
        fin_type = group.rows[row_index].value_for("Fin Type")
        return condenser_requires_pi(fin_type)
    return True


def _mutation_message(applied: int, blocked: int) -> str:
    if applied and blocked:
        return f"Applied {applied} cell(s); skipped {blocked} protected target(s)."
    if applied:
        return f"Applied {applied} cell(s)."
    if blocked:
        return f"No cells changed; skipped {blocked} protected target(s)."
    return "No cells changed."
