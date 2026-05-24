"""Bordered Tkinter input matrix with explicit editable-cell mapping.

This widget owns presentation and text parsing only. It does not import
calculator core or profile routing; visual values come from its Tkinter owner.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Callable, Mapping

from ui_tk.layout_constants import (
    TABLE_BODY_FONT,
    TABLE_CELL_PADX,
    TABLE_CELL_PADY,
    TABLE_DATA_COLUMN_CHARS,
    TABLE_DATA_COLUMN_WEIGHT,
    TABLE_EDITABLE_BG,
    TABLE_GRID_COLOR,
    TABLE_HEADER_BG,
    TABLE_HEADER_FG,
    TABLE_HEADER_FONT,
    TABLE_HEADER_PADY,
    TABLE_ROW_HEADER_CHARS,
    TABLE_ROW_HEADER_WEIGHT,
    TABLE_STATIC_BG,
    TABLE_STATIC_FG,
)
from ui_tk.table_grid_model import parse_numeric_cell

__all__ = ["MetricInputTable"]


ValuesChangedCallback = Callable[[], None]
CellAddress = tuple[str, str]


class MetricInputTable(ttk.Frame):
    """A bordered matrix table containing editable and static cells."""

    def __init__(
        self,
        master: tk.Misc,
        *,
        columns: tuple[tuple[str, str], ...],
        rows: tuple[tuple[str, str], ...],
        editable_cells: Mapping[CellAddress, str],
        row_header_chars: int = TABLE_ROW_HEADER_CHARS,
        data_column_chars: int = TABLE_DATA_COLUMN_CHARS,
        values_changed_callback: ValuesChangedCallback | None = None,
        **kwargs: object,
    ) -> None:
        super().__init__(master, **kwargs)
        self.columns = columns
        self.rows = rows
        self.editable_cells = dict(editable_cells)
        self.row_header_chars = row_header_chars
        self.data_column_chars = data_column_chars
        self.layout_policy = "responsive"
        self._values_changed_callback = values_changed_callback
        self._values: dict[str, str] = {
            field_key: "" for field_key in self.editable_cells.values()
        }
        self._variables: dict[str, tk.StringVar] = {}
        self._entries: dict[str, tk.Entry] = {}
        self.editable_entries = self._entries
        self.table_frame: tk.Frame
        self.header_cells: dict[str, tk.Frame] = {}
        self.row_header_cells: dict[str, tk.Frame] = {}
        self.editable_cell_frames: dict[str, tk.Frame] = {}
        self.static_cell_frames: dict[CellAddress, tk.Frame] = {}
        self.cell_frames: dict[CellAddress, tk.Frame] = {}
        if len(set(self.editable_cells.values())) != len(self.editable_cells):
            raise ValueError("metric input field keys must be unique")
        self.field_order: tuple[str, ...] = ()
        self._build_table()

    def _build_table(self) -> None:
        self.columnconfigure(0, weight=1)
        self.table_frame = tk.Frame(
            self,
            name="matrix_surface",
            background=TABLE_GRID_COLOR,
            borderwidth=1,
            relief=tk.SOLID,
        )
        self.table_frame.grid(row=0, column=0, sticky="ew")
        self.table_frame.surface_role = "table_frame"
        self.table_frame.layout_policy = self.layout_policy
        self._configure_column_weights()
        self._add_header_cell(column=0, key=None, label="")
        for column_number, (_key, label) in enumerate(self.columns, start=1):
            self._add_header_cell(column=column_number, key=_key, label=label)
        for row_number, (row_key, label) in enumerate(self.rows, start=1):
            self._add_row_header(row=row_number, key=row_key, label=label)
            for column_number, (column_key, _label) in enumerate(
                self.columns, start=1
            ):
                address = (row_key, column_key)
                field_key = self.editable_cells.get(address)
                if field_key is None:
                    self._add_static_cell(
                        row=row_number, column=column_number, address=address
                    )
                    continue
                self._add_editable_cell(
                    row=row_number,
                    column=column_number,
                    address=address,
                    field_key=field_key,
                )

    def _configure_column_weights(self) -> None:
        self.table_frame.columnconfigure(0, weight=TABLE_ROW_HEADER_WEIGHT)
        for column in range(1, len(self.columns) + 1):
            self.table_frame.columnconfigure(column, weight=TABLE_DATA_COLUMN_WEIGHT)

    def _add_header_cell(self, *, column: int, key: str | None, label: str) -> None:
        cell = self._make_cell_frame(
            row=0, column=column, role="header_cell", background=TABLE_HEADER_BG
        )
        if key is not None:
            cell.surface_key = key
            self.header_cells[key] = cell
        tk.Label(
            cell,
            text=label,
            width=self.row_header_chars if key is None else self.data_column_chars,
            background=TABLE_HEADER_BG,
            foreground=TABLE_HEADER_FG,
            font=TABLE_HEADER_FONT,
        ).pack(fill=tk.BOTH, expand=True, padx=TABLE_CELL_PADX, pady=TABLE_HEADER_PADY)

    def _add_row_header(self, *, row: int, key: str, label: str) -> None:
        cell = self._make_cell_frame(
            row=row, column=0, role="row_header_cell", background=TABLE_HEADER_BG
        )
        cell.surface_key = key
        self.row_header_cells[key] = cell
        tk.Label(
            cell,
            text=label,
            width=self.row_header_chars,
            anchor="w",
            background=TABLE_HEADER_BG,
            foreground=TABLE_HEADER_FG,
            font=TABLE_HEADER_FONT,
        ).pack(fill=tk.BOTH, expand=True, padx=TABLE_CELL_PADX, pady=TABLE_HEADER_PADY)

    def _add_static_cell(
        self, *, row: int, column: int, address: CellAddress
    ) -> None:
        cell = self._make_cell_frame(
            row=row, column=column, role="static_cell", background=TABLE_STATIC_BG
        )
        cell.surface_address = address
        self.cell_frames[address] = cell
        self.static_cell_frames[address] = cell
        tk.Label(
            cell,
            text="-",
            width=self.data_column_chars,
            background=TABLE_STATIC_BG,
            foreground=TABLE_STATIC_FG,
            font=TABLE_BODY_FONT,
        ).pack(fill=tk.BOTH, expand=True, padx=TABLE_CELL_PADX, pady=TABLE_CELL_PADY)

    def _add_editable_cell(
        self, *, row: int, column: int, address: CellAddress, field_key: str
    ) -> None:
        cell = self._make_cell_frame(
            row=row, column=column, role="editable_cell", background=TABLE_EDITABLE_BG
        )
        cell.surface_address = address
        self.cell_frames[address] = cell
        self.editable_cell_frames[field_key] = cell
        variable = tk.StringVar(master=self)
        variable.trace_add(
            "write",
            lambda *_args, field_key=field_key: self._handle_change(field_key),
        )
        entry = tk.Entry(
            cell,
            textvariable=variable,
            width=self.data_column_chars,
            relief=tk.FLAT,
            borderwidth=0,
            highlightthickness=0,
            justify=tk.CENTER,
            background=TABLE_EDITABLE_BG,
            font=TABLE_BODY_FONT,
        )
        entry.pack(fill=tk.BOTH, expand=True, padx=TABLE_CELL_PADX, pady=TABLE_CELL_PADY)
        entry.surface_role = "editable_entry"
        entry.bind(
            "<Return>",
            lambda _event, field_key=field_key: self._focus_next(field_key),
        )
        self._variables[field_key] = variable
        self._entries[field_key] = entry
        self.field_order += (field_key,)

    def _make_cell_frame(
        self, *, row: int, column: int, role: str, background: str
    ) -> tk.Frame:
        cell = tk.Frame(self.table_frame, background=background, borderwidth=0)
        cell.grid(row=row, column=column, sticky="nsew", padx=(0, 1), pady=(0, 1))
        cell.surface_role = role
        return cell

    def _handle_change(self, field_key: str) -> None:
        value = self._variables[field_key].get()
        if value == self._values[field_key]:
            return
        self._values[field_key] = value
        if self._values_changed_callback is not None:
            self._values_changed_callback()

    def _focus_next(self, field_key: str) -> str:
        index = self.field_order.index(field_key)
        following = self.field_order[(index + 1) % len(self.field_order)]
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
