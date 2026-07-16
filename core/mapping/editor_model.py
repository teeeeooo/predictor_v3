"""Qt-free user-facing mapping editor draft models."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from core.mapping.entity_model import MappingValidationError


@dataclass(frozen=True)
class MappingRequirementProjection:
    """Provenance for the current Data Definition overlay on one group."""

    base_columns: tuple[str, ...]
    base_notes: str = ""
    base_column_data_types: Mapping[str, str] = field(default_factory=dict)
    base_required_columns: tuple[str, ...] = ()
    requirement_columns: tuple[str, ...] = ()


@dataclass(frozen=True)
class MappingEditorRow:
    """One user-facing draft row."""

    values: Mapping[str, Any] = field(default_factory=dict)
    source_key: str = ""
    unresolved: bool = False
    notes: str = ""

    def value_for(self, column: str, default: Any = "") -> Any:
        """Return one column value."""
        return self.values.get(column, default)

    def has_concrete_value_for(self, column: str) -> bool:
        """Return whether runtime/import/user state owns this value key."""
        return column in self.values


@dataclass(frozen=True)
class MappingEditorGroup:
    """One user-facing Data Mapping Manager group."""

    group_key: str
    label: str
    columns: tuple[str, ...]
    rows: tuple[MappingEditorRow, ...] = ()
    runtime_sections: tuple[str, ...] = ()
    notes: str = ""
    column_data_types: Mapping[str, str] = field(default_factory=dict)
    required_columns: tuple[str, ...] = ()
    requirement_projection: MappingRequirementProjection | None = None


@dataclass(frozen=True)
class MappingEditorDraft:
    """User-facing projection of runtime mapping data."""

    groups: tuple[MappingEditorGroup, ...]
    unowned_sections: Mapping[str, Any] = field(default_factory=dict)
    source_label: str = ""

    def group(self, group_key: str) -> MappingEditorGroup | None:
        """Return a group by key."""
        return next((group for group in self.groups if group.group_key == group_key), None)


@dataclass(frozen=True)
class MappingEditorValidationResult:
    """Validation result for a mapping editor draft."""

    issues: tuple[MappingValidationError, ...] = ()

    @property
    def save_enabled(self) -> bool:
        """Return whether the draft can be saved."""
        return not any(issue.severity == "error" for issue in self.issues)
