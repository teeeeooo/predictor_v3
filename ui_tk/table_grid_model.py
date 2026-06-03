"""Pure data model for a Tkinter table/grid input surface.

This module owns schema, text storage, and numeric validation state only.
It imports no GUI toolkit and contains no calculator/profile-specific logic.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import math
from typing import Mapping

__all__ = [
    "GridColumn",
    "GridRow",
    "GridCellState",
    "TableGridModel",
    "parse_numeric_cell",
]


@dataclass(frozen=True)
class GridColumn:
    """One numeric input column in a table/grid schema."""

    key: str
    label: str


@dataclass(frozen=True)
class GridRow:
    """One user-visible row in a table/grid schema."""

    key: str
    label: str


class GridCellState(str, Enum):
    """Validation state for numeric input text."""

    VALID = "valid"
    MISSING = "missing"
    INVALID = "invalid"


def parse_numeric_cell(value: str) -> float:
    """Parse numeric text after trimming whitespace and thousands commas."""
    text = value.strip().replace(",", "")
    if not text:
        raise ValueError("numeric cell is missing")
    try:
        parsed = float(text)
    except ValueError as exc:
        raise ValueError(f"invalid numeric cell value: {value!r}") from exc
    if not math.isfinite(parsed):
        raise ValueError(f"numeric cell must be finite: {value!r}")
    return parsed


class TableGridModel:
    """Row/column addressed text grid with derived numeric validation state."""

    def __init__(
        self,
        rows: tuple[GridRow, ...],
        columns: tuple[GridColumn, ...],
    ) -> None:
        if not rows:
            raise ValueError("table grid requires at least one row")
        if not columns:
            raise ValueError("table grid requires at least one column")
        self.rows = tuple(rows)
        self.columns = tuple(columns)
        self._row_keys = self._unique_keys(self.rows, "row")
        self._column_keys = self._unique_keys(self.columns, "column")
        self._values = {
            row.key: {column.key: "" for column in self.columns}
            for row in self.rows
        }

    @staticmethod
    def _unique_keys(items: tuple[object, ...], kind: str) -> tuple[str, ...]:
        keys = tuple(item.key for item in items)
        if len(set(keys)) != len(keys):
            raise ValueError(f"table grid {kind} keys must be unique")
        return keys

    def _assert_cell(self, row_key: str, column_key: str) -> None:
        if row_key not in self._row_keys:
            raise KeyError(f"Unknown grid row key: {row_key!r}")
        if column_key not in self._column_keys:
            raise KeyError(f"Unknown grid column key: {column_key!r}")

    def get_cell(self, row_key: str, column_key: str) -> str:
        """Return the text stored at a row/column address."""
        self._assert_cell(row_key, column_key)
        return self._values[row_key][column_key]

    def set_cell(self, row_key: str, column_key: str, value: str) -> bool:
        """Store text at a cell and report whether the value changed."""
        self._assert_cell(row_key, column_key)
        if not isinstance(value, str):
            raise TypeError("table grid values must be strings")
        if self._values[row_key][column_key] == value:
            return False
        self._values[row_key][column_key] = value
        return True

    def set_cells(self, values: Mapping[tuple[str, str], str]) -> bool:
        """Apply a set of row/column text values and report any change."""
        changed = False
        for (row_key, column_key), value in values.items():
            if self.set_cell(row_key, column_key, value):
                changed = True
        return changed

    def cell_state(self, row_key: str, column_key: str) -> GridCellState:
        """Return numeric validation state for one cell."""
        value = self.get_cell(row_key, column_key)
        if not value.strip():
            return GridCellState.MISSING
        try:
            parse_numeric_cell(value)
        except ValueError:
            return GridCellState.INVALID
        return GridCellState.VALID

    def invalid_cells(self) -> tuple[tuple[str, str], ...]:
        """Return missing or invalid numeric cells in schema order."""
        return tuple(
            (row.key, column.key)
            for row in self.rows
            for column in self.columns
            if self.cell_state(row.key, column.key) is not GridCellState.VALID
        )

    def as_text_table(self) -> dict[str, dict[str, str]]:
        """Return a detached nested mapping of all cell text."""
        return {
            row.key: {
                column.key: self.get_cell(row.key, column.key)
                for column in self.columns
            }
            for row in self.rows
        }

    def as_numeric_table(self) -> dict[str, dict[str, float]]:
        """Return parsed numeric values, failing on missing/invalid cells."""
        invalid = self.invalid_cells()
        if invalid:
            raise ValueError(f"table grid has invalid cells: {invalid!r}")
        return {
            row.key: {
                column.key: parse_numeric_cell(self.get_cell(row.key, column.key))
                for column in self.columns
            }
            for row in self.rows
        }
