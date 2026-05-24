"""Bordered Tkinter input matrix with explicit editable-cell mapping.

This widget owns presentation and text parsing only. It does not import
calculator core, profile routing, or visual-token styling.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Callable, Mapping

from ui_tk.layout_constants import MATRIX_DATA_COLUMN_WIDTH, MATRIX_ROW_HEADER_WIDTH
from ui_tk.table_grid_model import parse_numeric_cell

__all__ = ["MetricInputTable"]


ValuesChangedCallback = Callable[[], None]
CellAddress = tuple[str, str]

_GRID_LINE = "#c4ccd4"
_HEADER_BACKGROUND = "#e8edf2"
_EDITABLE_BACKGROUND = "#ffffff"
_STATIC_BACKGROUND = "#f1f3f5"
_HEADER_FOREGROUND = "#26333f"
_STATIC_FOREGROUND = "#66737f"


class MetricInputTable(ttk.Frame):
    """A bordered matrix table containing editable and static cells."""

    def __init__(
        self,
        master: tk.Misc,
        *,
        columns: tuple[tuple[str, str], ...],
        rows: tuple[tuple[str, str], ...],
        editable_cells: Mapping[CellAddress, str],
        row_header_width: int = MATRIX_ROW_HEADER_WIDTH,
        data_column_width: int = MATRIX_DATA_COLUMN_WIDTH,
        total_columns_hint: int | None = None,
        values_changed_callback: ValuesChangedCallback | None = None,
        **kwargs: object,
    ) -> None:
        super().__init__(master, **kwargs)
        self._columns = columns
        self._rows = rows
        self._editable_cells = dict(editable_cells)
        self.row_header_width = row_header_width
        self.data_column_width = data_column_width
        self.total_columns_hint = total_columns_hint or len(columns)
        if self.total_columns_hint < len(columns):
            raise ValueError("total_columns_hint must cover all visible data columns")
        self.content_width = (
            self.row_header_width + self.data_column_width * self.total_columns_hint
        )
        self._values_changed_callback = values_changed_callback
        self._values: dict[str, str] = {
            field_key: "" for field_key in self._editable_cells.values()
        }
        self._variables: dict[str, tk.StringVar] = {}
        self._entries: dict[str, tk.Entry] = {}
        self.table_frame: tk.Frame
        self.header_cells: dict[str, tk.Frame] = {}
        self.row_header_cells: dict[str, tk.Frame] = {}
        self.editable_cell_frames: dict[str, tk.Frame] = {}
        self.static_cell_frames: dict[CellAddress, tk.Frame] = {}
        self._field_order = tuple(self._editable_cells.values())
        if len(set(self._field_order)) != len(self._field_order):
            raise ValueError("metric input field keys must be unique")
        self._build_table()

    def _build_table(self) -> None:
        self.table_frame = tk.Frame(
            self,
            name="matrix_surface",
            background=_GRID_LINE,
            borderwidth=1,
            relief=tk.SOLID,
        )
        self.table_frame.grid(row=0, column=0, sticky="w")
        self.table_frame.surface_role = "table_frame"
        self.table_frame.content_width = self.content_width
        self._configure_column_widths()
        self._add_header_cell(column=0, key=None, label="")
        for column_number, (_key, label) in enumerate(self._columns, start=1):
            self._add_header_cell(column=column_number, key=_key, label=label)
        for row_number, (row_key, label) in enumerate(self._rows, start=1):
            self._add_row_header(row=row_number, key=row_key, label=label)
            for column_number, (column_key, _label) in enumerate(
                self._columns, start=1
            ):
                address = (row_key, column_key)
                field_key = self._editable_cells.get(address)
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

    def _configure_column_widths(self) -> None:
        self.table_frame.columnconfigure(0, minsize=self.row_header_width, weight=0)
        visible_columns = len(self._columns)
        slot_width = self.data_column_width * self.total_columns_hint // visible_columns
        remainder = (
            self.data_column_width * self.total_columns_hint
            - slot_width * visible_columns
        )
        for column in range(1, visible_columns + 1):
            extra = 1 if column <= remainder else 0
            self.table_frame.columnconfigure(
                column, minsize=slot_width + extra, weight=0
            )

    def _add_header_cell(self, *, column: int, key: str | None, label: str) -> None:
        cell = self._make_cell_frame(
            row=0, column=column, role="header_cell", background=_HEADER_BACKGROUND
        )
        if key is not None:
            cell.surface_key = key
            self.header_cells[key] = cell
        tk.Label(
            cell,
            text=label,
            background=_HEADER_BACKGROUND,
            foreground=_HEADER_FOREGROUND,
            font=("TkDefaultFont", 10, "bold"),
        ).pack(fill=tk.BOTH, expand=True, padx=10, pady=6)

    def _add_row_header(self, *, row: int, key: str, label: str) -> None:
        cell = self._make_cell_frame(
            row=row, column=0, role="row_header_cell", background=_HEADER_BACKGROUND
        )
        cell.surface_key = key
        self.row_header_cells[key] = cell
        tk.Label(
            cell,
            text=label,
            anchor="w",
            background=_HEADER_BACKGROUND,
            foreground=_HEADER_FOREGROUND,
            font=("TkDefaultFont", 10, "bold"),
        ).pack(fill=tk.BOTH, expand=True, padx=10, pady=6)

    def _add_static_cell(
        self, *, row: int, column: int, address: CellAddress
    ) -> None:
        cell = self._make_cell_frame(
            row=row, column=column, role="static_cell", background=_STATIC_BACKGROUND
        )
        cell.surface_address = address
        self.static_cell_frames[address] = cell
        tk.Label(
            cell,
            text="-",
            background=_STATIC_BACKGROUND,
            foreground=_STATIC_FOREGROUND,
        ).pack(fill=tk.BOTH, expand=True, padx=10, pady=7)

    def _add_editable_cell(
        self, *, row: int, column: int, address: CellAddress, field_key: str
    ) -> None:
        cell = self._make_cell_frame(
            row=row, column=column, role="editable_cell", background=_EDITABLE_BACKGROUND
        )
        cell.surface_address = address
        self.editable_cell_frames[field_key] = cell
        variable = tk.StringVar(master=self)
        variable.trace_add(
            "write",
            lambda *_args, field_key=field_key: self._handle_change(field_key),
        )
        entry = tk.Entry(
            cell,
            textvariable=variable,
            width=14,
            relief=tk.FLAT,
            borderwidth=0,
            highlightthickness=0,
            justify=tk.CENTER,
            background=_EDITABLE_BACKGROUND,
        )
        entry.pack(fill=tk.BOTH, expand=True, padx=10, pady=7)
        entry.surface_role = "editable_entry"
        entry.bind(
            "<Return>",
            lambda _event, field_key=field_key: self._focus_next(field_key),
        )
        self._variables[field_key] = variable
        self._entries[field_key] = entry

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
