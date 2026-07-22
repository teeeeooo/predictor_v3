"""Input case row state for the Predict workspace."""

from dataclasses import dataclass, field
from collections.abc import Callable
from typing import Any


@dataclass
class CaseRow:
    """Editable input/autofill state for one prediction case."""

    case_id: str
    input_values: dict[str, Any] = field(default_factory=dict)
    autofill_values: dict[str, Any] = field(default_factory=dict)
    dirty_fields: set[str] = field(default_factory=set)
    _mutation_callback: Callable[[], None] | None = field(
        default=None, repr=False, compare=False
    )

    @property
    def is_dirty(self) -> bool:
        """Return whether any editable field has changed."""
        return bool(self.dirty_fields)

    def set_input_value(self, key: str, value: Any) -> None:
        """Update one editable input value and mark it dirty."""
        changed = self.input_values.get(key) != value or key not in self.dirty_fields
        self.input_values[key] = value
        self.dirty_fields.add(key)
        if changed and self._mutation_callback is not None:
            self._mutation_callback()

    def bind_mutation_callback(self, callback: Callable[[], None]) -> None:
        self._mutation_callback = callback
