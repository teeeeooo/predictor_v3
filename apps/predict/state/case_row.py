"""Input case row state for the Predict workspace."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class CaseRow:
    """Editable input/autofill state for one prediction case."""

    case_id: str
    input_values: dict[str, Any] = field(default_factory=dict)
    autofill_values: dict[str, Any] = field(default_factory=dict)
    dirty_fields: set[str] = field(default_factory=set)

    @property
    def is_dirty(self) -> bool:
        """Return whether any editable field has changed."""
        return bool(self.dirty_fields)

    def set_input_value(self, key: str, value: Any) -> None:
        """Update one editable input value and mark it dirty."""
        self.input_values[key] = value
        self.dirty_fields.add(key)
