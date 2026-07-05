"""Qt-free user-facing mapping editor draft models."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from core.mapping.entity_model import MappingValidationError


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


@dataclass(frozen=True)
class MappingEditorGroup:
    """One user-facing Data Mapping Manager group."""

    group_key: str
    label: str
    columns: tuple[str, ...]
    rows: tuple[MappingEditorRow, ...] = ()
    runtime_sections: tuple[str, ...] = ()
    notes: str = ""


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
