"""Tkinter Entry-grid adapter for :mod:`ui_tk.table_grid_model`.

This is a reusable input foundation only. It does not call calculator core,
perform auto-calc/debounce, or apply the visual-token foundation to widgets.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Callable

from ui_tk.table_grid_model import GridColumn, GridRow, TableGridModel

__all__ = ["TableGrid"]


ValuesChangedCallback = Callable[[], None]


class TableGrid(ttk.Frame):
    """Editable table-shaped grid backed by :class:`TableGridModel`."""

    def __init__(
        self,
        master: tk.Misc,
        rows: tuple[GridRow, ...],
        columns: tuple[GridColumn, ...],
        *,
        values_changed_callback: ValuesChangedCallback | None = None,
        **kwargs: object,
    ) -> None:
        super().__init__(master, **kwargs)
        self.model = TableGridModel(rows, columns)
        self._values_changed_callback = values_changed_callback
        self._variables: dict[tuple[str, str], tk.StringVar] = {}
        self._entries: dict[tuple[str, str], ttk.Entry] = {}
        self._coordinates = tuple(
            (row.key, column.key)
            for row in self.model.rows
            for column in self.model.columns
        )
        self._build_grid()

    def _build_grid(self) -> None:
        ttk.Label(self, text="").grid(row=0, column=0, sticky="w")
        for column_number, column in enumerate(self.model.columns, start=1):
            ttk.Label(self, text=column.label).grid(
                row=0, column=column_number, sticky="ew", padx=2, pady=2
            )
        for row_number, row in enumerate(self.model.rows, start=1):
            ttk.Label(self, text=row.label).grid(
                row=row_number, column=0, sticky="w", padx=2, pady=2
            )
            for column_number, column in enumerate(self.model.columns, start=1):
                address = (row.key, column.key)
                variable = tk.StringVar(value=self.model.get_cell(*address))
                variable.trace_add(
                    "write",
                    lambda *_args, address=address: self._handle_value_change(address),
                )
                entry = ttk.Entry(self, textvariable=variable)
                entry.grid(
                    row=row_number,
                    column=column_number,
                    sticky="ew",
                    padx=2,
                    pady=2,
                )
                entry.bind(
                    "<Return>",
                    lambda _event, address=address: self._focus_next_cell(address),
                )
                self._variables[address] = variable
                self._entries[address] = entry

    def _handle_value_change(self, address: tuple[str, str]) -> None:
        if self.model.set_cell(*address, self._variables[address].get()):
            if self._values_changed_callback is not None:
                self._values_changed_callback()

    def _focus_next_cell(self, address: tuple[str, str]) -> str:
        current = self._coordinates.index(address)
        following = self._coordinates[(current + 1) % len(self._coordinates)]
        self.focus_cell(*following)
        return "break"

    def set_values_changed_callback(
        self, callback: ValuesChangedCallback | None
    ) -> None:
        """Set a high-level callback invoked once for each changed cell text."""
        self._values_changed_callback = callback

    def set_cell(self, row_key: str, column_key: str, value: str) -> bool:
        """Update an Entry-backed cell, invoking callback only on change."""
        if not isinstance(value, str):
            raise TypeError("table grid values must be strings")
        if self.model.get_cell(row_key, column_key) == value:
            return False
        self._variables[(row_key, column_key)].set(value)
        return True

    def get_text_table(self) -> dict[str, dict[str, str]]:
        """Return all entered text in row/column form."""
        return self.model.as_text_table()

    def get_numeric_table(self) -> dict[str, dict[str, float]]:
        """Return parsed values, failing if any cell is missing/invalid."""
        return self.model.as_numeric_table()

    def invalid_cells(self) -> tuple[tuple[str, str], ...]:
        """Return missing or invalid numeric cells from the model."""
        return self.model.invalid_cells()

    def clear_validation_state(self) -> None:
        """Reserved adapter hook; this slice does not apply visual styling."""

    def focus_cell(self, row_key: str, column_key: str) -> None:
        """Move keyboard focus to the addressed cell."""
        self.model.get_cell(row_key, column_key)
        self._entries[(row_key, column_key)].focus_set()
