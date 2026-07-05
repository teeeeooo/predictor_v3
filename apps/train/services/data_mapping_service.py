"""Data Mapping service foundation for Train/Admin."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from core.mapping.editor_model import MappingEditorDraft
from core.mapping.editor_projection import (
    load_runtime_mapping_editor_draft,
    project_runtime_mapping_to_editor_draft,
)
from core.mapping.entity_model import MappingValidationError
from core.mapping.entity_runtime_adapter import runtime_mapping_source_label


@dataclass(frozen=True)
class DataMappingAction:
    """Read-only action metadata for future Data Mapping workflows."""

    key: str
    label: str
    enabled: bool
    reason: str


@dataclass(frozen=True)
class DataMappingSnapshot:
    """Service snapshot for the Data Mapping Manager."""

    draft: MappingEditorDraft
    validation_errors: tuple[MappingValidationError, ...]
    source_label: str
    actions: tuple[DataMappingAction, ...]

    @property
    def is_valid(self) -> bool:
        """Return whether the mapping entity catalog has no validation errors."""
        return not self.validation_errors


class MappingDraftProvider(Protocol):
    """Provider interface for mapping editor draft data."""

    def load_draft(self) -> MappingEditorDraft:
        """Return a mapping editor draft."""
        ...

    @property
    def source_label(self) -> str:
        """Return a display label describing the provider source."""
        ...


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

    def load_draft(self) -> MappingEditorDraft:
        """Return the current runtime mapping data as editor draft groups."""
        return load_runtime_mapping_editor_draft(self._mapping_file)


class DataMappingService:
    """Provide read-only Mapping Entity catalog snapshots for Train/Admin UI."""

    def __init__(self, provider: MappingDraftProvider | None = None) -> None:
        self._provider = provider or RuntimeMappingCatalogProvider()

    @property
    def source_label(self) -> str:
        """Return the configured provider source label before loading."""
        return self._provider.source_label

    def load_snapshot(self) -> DataMappingSnapshot:
        """Return draft data, validation result, and disabled future actions."""
        draft = self._provider.load_draft()
        return DataMappingSnapshot(
            draft=draft,
            validation_errors=(),
            source_label=self.source_label,
            actions=_future_actions(),
        )


def _future_actions() -> tuple[DataMappingAction, ...]:
    disabled_reason = "Read-only mode."
    return (
        DataMappingAction("import_csv_v2", "Import", False, disabled_reason),
        DataMappingAction("export_csv_v2", "Export", False, disabled_reason),
        DataMappingAction("save_mapping_json", "Save", False, disabled_reason),
        DataMappingAction("reload_runtime", "Reload", False, disabled_reason),
    )
