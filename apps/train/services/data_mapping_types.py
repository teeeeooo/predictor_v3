"""Shared Data Mapping service DTOs and provider protocol."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from core.mapping.editor_model import MappingEditorDraft, MappingEditorValidationResult
from core.mapping.entity_model import MappingValidationError


@dataclass(frozen=True)
class DataMappingAction:
    """Action metadata for Data Mapping workflows."""

    key: str
    label: str
    enabled: bool
    reason: str


@dataclass(frozen=True)
class DataMappingSnapshot:
    """Service snapshot for the Data Mapping Manager."""

    draft: MappingEditorDraft
    validation_errors: tuple[MappingValidationError, ...]
    validation_result: MappingEditorValidationResult
    source_label: str
    actions: tuple[DataMappingAction, ...]
    dirty: bool = False

    @property
    def is_valid(self) -> bool:
        """Return whether the mapping editor draft has no blocking issues."""
        return self.validation_result.save_enabled


class MappingDraftProvider(Protocol):
    """Provider interface for mapping editor draft data."""

    def load_draft(self) -> MappingEditorDraft:
        """Return a mapping editor draft."""
        ...

    @property
    def source_label(self) -> str:
        """Return a display label describing the provider source."""
        ...
