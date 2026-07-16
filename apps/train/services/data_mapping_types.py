"""Shared Data Mapping service DTOs and provider protocol."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol

from core.data_definition.mapping_requirement_contract import (
    EffectiveMappingRequirement,
    MappingRequirementConflict,
)
from core.mapping.editor_model import MappingEditorDraft, MappingEditorValidationResult
from core.mapping.exchange.diff import MappingExchangeGroupDiff
from core.mapping.entity_model import MappingValidationError
from core.data_definition import MappingRequirement


@dataclass(frozen=True)
class DataMappingAction:
    """Action metadata for Data Mapping workflows."""

    key: str
    label: str
    enabled: bool
    reason: str


@dataclass(frozen=True)
class DataMappingCellEdit:
    """One visible mapping-cell mutation requested by the UI."""

    row_index: int
    column: str
    value: Any


@dataclass(frozen=True)
class DataMappingMutationResult:
    """Outcome for one grouped mapping mutation intent."""

    applied: int = 0
    blocked: int = 0
    message: str = ""


@dataclass(frozen=True)
class DataMappingSnapshot:
    """Service snapshot for the Data Mapping Manager."""

    draft: MappingEditorDraft
    validation_errors: tuple[MappingValidationError, ...]
    validation_result: MappingEditorValidationResult
    source_label: str
    actions: tuple[DataMappingAction, ...]
    dirty: bool = False
    mapping_requirements: tuple[MappingRequirement, ...] = ()
    effective_mapping_requirements: tuple[EffectiveMappingRequirement, ...] = ()
    mapping_requirement_conflicts: tuple[MappingRequirementConflict, ...] = ()

    @property
    def is_valid(self) -> bool:
        """Return whether the mapping editor draft has no blocking issues."""
        return self.validation_result.save_enabled


@dataclass(frozen=True)
class DataMappingImportPreview:
    """Prepared, non-mutating full-snapshot import preview."""

    source_path: Path
    format_version: str
    group_diffs: tuple[MappingExchangeGroupDiff, ...] = ()
    blockers: tuple[MappingValidationError, ...] = ()
    warnings: tuple[MappingValidationError, ...] = ()
    candidate: MappingEditorDraft | None = field(default=None, repr=False, compare=False)
    base_draft: MappingEditorDraft | None = field(default=None, repr=False, compare=False)

    @property
    def can_apply(self) -> bool:
        """Return whether Apply to Draft is allowed."""
        return self.candidate is not None and not self.blockers

    @property
    def affected_group_count(self) -> int:
        """Return the number of groups with a visible semantic change."""
        return sum(
            bool(diff.added_rows or diff.removed_rows or diff.changed_rows)
            for diff in self.group_diffs
        )


@dataclass(frozen=True)
class DataMappingImportApplyResult:
    """Outcome of applying a prepared import candidate."""

    success: bool
    changed: bool = False
    stale: bool = False
    message: str = ""


class MappingDraftProvider(Protocol):
    """Provider interface for mapping editor draft data."""

    def load_draft(self) -> MappingEditorDraft:
        """Return a mapping editor draft."""
        ...

    @property
    def source_label(self) -> str:
        """Return a display label describing the provider source."""
        ...
