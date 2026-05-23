"""Compact Tkinter input table with explicit editable-cell mapping.

This widget owns presentation and text parsing only. It does not import
calculator core, profile routing, or visual-token styling.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Callable, Mapping

from ui_tk.table_grid_model import parse_numeric_cell

__all__ = ["MetricInputTable"]


ValuesChangedCallback = Callable[[], None]
CellAddress = tuple[str, str]


class MetricInputTable(ttk.Frame):
    """A compact metric card table containing editable and static cells."""

    def __init__(
        self,
        master: tk.Misc,
        *,
        columns: tuple[tuple[str, str], ...],
        rows: tuple[tuple[str, str], ...],
        editable_cells: Mapping[CellAddress, str],
        values_changed_callback: ValuesChangedCallback | None = None,
        **kwargs: object,
    ) -> None:
        super().__init__(master, **kwargs)
        self._columns = columns
        self._rows = rows
        self._editable_cells = dict(editable_cells)
        self._values_changed_callback = values_changed_callback
        self._values: dict[str, str] = {
            field_key: "" for field_key in self._editable_cells.values()
        }
        self._variables: dict[str, tk.StringVar] = {}
        self._entries: dict[str, ttk.Entry] = {}
        self._field_order = tuple(self._editable_cells.values())
        if len(set(self._field_order)) != len(self._field_order):
            raise ValueError("metric input field keys must be unique")
        self._build_table()

    def _build_table(self) -> None:
        ttk.Label(self, text="").grid(row=0, column=0, padx=6, pady=4)
        for column_number, (_key, label) in enumerate(self._columns, start=1):
            ttk.Label(self, text=label).grid(
                row=0, column=column_number, sticky="ew", padx=6, pady=4
            )
        for row_number, (row_key, label) in enumerate(self._rows, start=1):
            ttk.Label(self, text=label).grid(
                row=row_number, column=0, sticky="w", padx=6, pady=4
            )
            for column_number, (column_key, _label) in enumerate(
                self._columns, start=1
            ):
                address = (row_key, column_key)
                field_key = self._editable_cells.get(address)
                if field_key is None:
                    ttk.Label(self, text="-").grid(
                        row=row_number,
                        column=column_number,
                        sticky="ew",
                        padx=6,
                        pady=4,
                    )
                    continue
                variable = tk.StringVar(master=self)
                variable.trace_add(
                    "write",
                    lambda *_args, field_key=field_key: self._handle_change(field_key),
                )
                entry = ttk.Entry(self, textvariable=variable, width=14)
                entry.grid(
                    row=row_number,
                    column=column_number,
                    sticky="ew",
                    padx=6,
                    pady=4,
                )
                entry.bind(
                    "<Return>",
                    lambda _event, field_key=field_key: self._focus_next(field_key),
                )
                self._variables[field_key] = variable
                self._entries[field_key] = entry

    def _handle_change(self, field_key: str) -> None:
        value = self._variables[field_key].get()
        if value == self._values[field_key]:
            return
        self._values[field_key] = value
        if self._values_changed_callback is not None:
            self._values_changed_callback()

    def _focus_next(self, field_key: str) -> str:
        index = self._field_order.index(field_key)
        following = self._field_order[(index + 1) % len(self._field_order)]
        self._entries[following].focus_set()
        return "break"

    def set_values_changed_callback(
        self, callback: ValuesChangedCallback | None
    ) -> None:
        self._values_changed_callback = callback

    def set_value(self, field_key: str, value: str) -> bool:
        if field_key not in self._values:
            raise KeyError(f"Unknown metric input field key: {field_key!r}")
        if not isinstance(value, str):
            raise TypeError("metric input values must be strings")
        if self._values[field_key] == value:
            return False
        self._variables[field_key].set(value)
        return True

    def set_values(self, values: Mapping[str, str]) -> bool:
        changed = False
        for field_key, value in values.items():
            if self.set_value(field_key, value):
                changed = True
        return changed

    def get_numeric_values(self) -> dict[str, float]:
        """Return numeric values for editable cells or raise on invalid input."""
        return {
            field_key: parse_numeric_cell(value)
            for field_key, value in self._values.items()
        }

    def get_text_values(self) -> dict[str, str]:
        return dict(self._values)
