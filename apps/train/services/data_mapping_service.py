"""Data Mapping Manager service for Train/Admin."""

from __future__ import annotations

from pathlib import Path

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
from core.mapping.editor_model import MappingEditorDraft
from core.mapping.editor_projection import (
    apply_mapping_requirements_to_editor_draft,
    load_runtime_mapping_editor_draft,
    mapping_group_key_for_requirement,
    project_runtime_mapping_to_editor_draft,
)
from core.mapping.editor_persistence import MappingEditorSaveResult, save_mapping_editor_draft
from core.mapping.editor_validation import validate_mapping_editor_draft
from core.mapping.entity_runtime_adapter import runtime_mapping_source_label
from core.mapping.entity_model import MappingValidationError
from core.mapping.paths import MAPPING_JSON_FILE
from core.data_definition import MappingRequirement, build_data_definition_report
from apps.train.services.data_mapping_types import (
    DataMappingAction,
    DataMappingSnapshot,
    MappingDraftProvider,
)


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

    def load_mapping_requirements(self) -> tuple[MappingRequirement, ...]:
        """Return current Data Definition mapping requirements."""
        return build_data_definition_report().mapping_requirements


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
        self._draft: MappingEditorDraft | None = None
        self._dirty = False

    @property
    def source_label(self) -> str:
        """Return the configured provider source label before loading."""
        return self._provider.source_label

    def load_snapshot(self) -> DataMappingSnapshot:
        """Return draft data, validation result, and disabled future actions."""
        requirements = self._load_mapping_requirements()
        draft = apply_mapping_requirements_to_editor_draft(
            self._draft or self._provider.load_draft(),
            requirements,
        )
        self._draft = draft
        return self._snapshot(draft, requirements)

    def reload_snapshot(self) -> DataMappingSnapshot:
        """Discard draft edits and reload from the provider."""
        requirements = self._load_mapping_requirements()
        self._draft = apply_mapping_requirements_to_editor_draft(
            self._provider.load_draft(),
            requirements,
        )
        self._dirty = False
        return self._snapshot(self._draft, requirements)

    def edit_cell(
        self,
        group_key: str,
        row_index: int,
        column: str,
        value: object,
    ) -> DataMappingSnapshot:
        """Apply one cell edit to the current draft."""
        draft = self.load_snapshot().draft
        next_draft = set_draft_cell(draft, group_key, row_index, column, value)
        return self._store_command_result(draft, next_draft)

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
            self._dirty = False
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

    def _store_command_result(
        self,
        previous: MappingEditorDraft,
        next_draft: MappingEditorDraft,
    ) -> DataMappingSnapshot:
        if next_draft != previous:
            self._draft = next_draft
            self._dirty = True
        return self._snapshot(self._draft or next_draft, self._load_mapping_requirements())

    def _snapshot(
        self,
        draft: MappingEditorDraft,
        requirements: tuple[MappingRequirement, ...],
    ) -> DataMappingSnapshot:
        base_validation = validate_mapping_editor_draft(draft)
        dynamic_issues = _required_mapping_value_issues(draft, requirements)
        validation_result = type(base_validation)(
            issues=(*base_validation.issues, *dynamic_issues)
        )
        return DataMappingSnapshot(
            draft=draft,
            validation_errors=validation_result.issues,
            validation_result=validation_result,
            source_label=self.source_label,
            actions=_future_actions(
                validation_result.save_enabled,
                can_save=bool(getattr(self._provider, "mapping_file", None)),
            ),
            dirty=self._dirty,
        )

    def _load_mapping_requirements(self) -> tuple[MappingRequirement, ...]:
        return self._mapping_requirement_provider.load_mapping_requirements()


def _required_mapping_value_issues(
    draft: MappingEditorDraft,
    requirements: tuple[MappingRequirement, ...],
) -> tuple[MappingValidationError, ...]:
    issues: list[MappingValidationError] = []
    for requirement in requirements:
        group_key = mapping_group_key_for_requirement(requirement)
        group = draft.group(group_key)
        if group is None:
            issues.append(
                MappingValidationError(
                    code="required_mapping_group_missing",
                    message=f"{requirement.mapping_entity} mapping group is required.",
                    entity_key=requirement.mapping_entity,
                    attribute_key=requirement.mapping_attribute,
                    field=requirement.mapping_attribute,
                )
            )
            continue
        issues.extend(_missing_value_issues(group, requirement.mapping_attribute))
    return tuple(issues)


def _missing_value_issues(group, attribute: str) -> tuple[MappingValidationError, ...]:  # noqa: ANN001
    if not group.rows:
        return (
            MappingValidationError(
                code="required_mapping_value_missing",
                message=f"{attribute} is required by Data Definition but the group has no rows.",
                entity_key=group.label,
                attribute_key=attribute,
                field=attribute,
            ),
        )
    issues: list[MappingValidationError] = []
    for index, row in enumerate(group.rows, start=1):
        if str(row.value_for(attribute, "")).strip():
            continue
        issues.append(
            MappingValidationError(
                code="required_mapping_value_missing",
                message=f"{attribute} is required by Data Definition.",
                entity_key=group.label,
                attribute_key=attribute,
                row_key=row.source_key or str(index),
                field=attribute,
            )
        )
    return tuple(issues)


def _future_actions(
    save_enabled: bool = False,
    *,
    can_save: bool = False,
) -> tuple[DataMappingAction, ...]:
    disabled_reason = "Import is not supported. Edit mappings in this screen."
    return (
        DataMappingAction("import_csv_v2", "Import", False, disabled_reason),
        DataMappingAction(
            "export_csv_v2",
            "Export",
            True,
            "Export a read-only review snapshot. It cannot be imported back.",
        ),
        DataMappingAction(
            "save_mapping_json",
            "Save",
            save_enabled and can_save,
            _save_disabled_reason(save_enabled, can_save),
        ),
        DataMappingAction("reload_runtime", "Reload", True, ""),
    )


def _save_disabled_reason(save_enabled: bool, can_save: bool) -> str:
    if not can_save:
        return "No writable mapping file is configured."
    if not save_enabled:
        return "Resolve Issues before saving."
    return ""
