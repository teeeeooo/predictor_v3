"""Small grouped undo stack for spreadsheet-like UI table edits."""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class CellChange:
    """One cell value change inside a grouped table action."""

    row: int
    col: int
    old_value: Any
    new_value: Any


class TableUndoStack:
    """Store grouped table edit/paste/clear changes."""

    def __init__(self, limit: int = 64) -> None:
        self._limit = limit
        self._undo: list[tuple[CellChange, ...]] = []

    def push(self, changes: list[CellChange]) -> None:
        """Push one undo group when it contains real changes."""
        group = tuple(changes)
        if not group:
            return
        self._undo.append(group)
        if len(self._undo) > self._limit:
            del self._undo[0]

    def pop(self) -> tuple[CellChange, ...]:
        """Return the most recent undo group."""
        if not self._undo:
            return ()
        return self._undo.pop()

    def clear(self) -> None:
        """Clear all undo history."""
        self._undo.clear()

    def __len__(self) -> int:
        return len(self._undo)
