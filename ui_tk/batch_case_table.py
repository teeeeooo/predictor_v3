"""Tkinter row-per-case batch table surface."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Mapping

from ui_tk.batch_models import (
    BatchColumnRole,
    BatchProfileSpec,
    BatchTableModel,
)
from ui_tk.layout_constants import TABLE_CELL_PADX, TABLE_CELL_PADY


class BatchCaseTable(ttk.Frame):
    """Editable input columns with read-only result/status columns."""

    def __init__(self, master: tk.Misc, spec: BatchProfileSpec, **kwargs: object) -> None:
        super().__init__(master, **kwargs)
        self.model = BatchTableModel(spec)
        self._variables: list[dict[str, tk.StringVar]] = []
        self._cell_widgets: list[dict[str, tk.Widget]] = []
        self._build_table()

    def add_row(self, values: Mapping[str, str] | None = None) -> None:
        self.model.add_row(values)
        self._rebuild_rows()

    def input_rows(self) -> list[dict[str, str]]:
        return [self.model.input_values(index) for index in range(len(self.model.rows))]

    def set_row_results(self, row_index: int, values: Mapping[str, str]) -> None:
        self.model.set_results(row_index, values)
        for key in (*self.model.spec.result_keys, *self.model.spec.status_keys):
            self._variables[row_index][key].set(self.model.rows[row_index][key])

    def clear_results(self) -> None:
        self.model.clear_results()
        for row_index, row in enumerate(self.model.rows):
            for key in (*self.model.spec.result_keys, *self.model.spec.status_keys):
                self._variables[row_index][key].set(row[key])

    def _build_table(self) -> None:
        self.columnconfigure(0, weight=1)
        self._table = ttk.Frame(self)
        self._table.grid(row=0, column=0, sticky="ew")
        self._build_headers()
        self._rebuild_rows()

    def _build_headers(self) -> None:
        for column_index, column in enumerate(self.model.spec.columns):
            label = ttk.Label(self._table, text=column.label)
            label.grid(
                row=0,
                column=column_index,
                sticky="ew",
                padx=TABLE_CELL_PADX,
                pady=TABLE_CELL_PADY,
            )
            self._table.columnconfigure(column_index, weight=1)

    def _rebuild_rows(self) -> None:
        for widgets in self._cell_widgets:
            for widget in widgets.values():
                widget.destroy()
        self._variables.clear()
        self._cell_widgets.clear()
        for row_index, row in enumerate(self.model.rows):
            self._build_row(row_index, row)

    def _build_row(self, row_index: int, row: Mapping[str, str]) -> None:
        variables: dict[str, tk.StringVar] = {}
        widgets: dict[str, tk.Widget] = {}
        for column_index, column in enumerate(self.model.spec.columns):
            variable = tk.StringVar(master=self, value=row.get(column.key, ""))
            variables[column.key] = variable
            if column.role is BatchColumnRole.INPUT:
                widget = ttk.Entry(
                    self._table,
                    textvariable=variable,
                    width=column.width_chars,
                )
                variable.trace_add(
                    "write",
                    lambda *_args, row_index=row_index, key=column.key, variable=variable:
                    self.model.set_cell(row_index, key, variable.get()),
                )
                widget.bind(
                    "<Control-v>",
                    lambda event, row=row_index, col=column_index: self._paste(event, row, col),
                )
                widget.bind(
                    "<Command-v>",
                    lambda event, row=row_index, col=column_index: self._paste(event, row, col),
                )
            else:
                widget = ttk.Label(
                    self._table,
                    textvariable=variable,
                    width=column.width_chars,
                    relief=tk.SUNKEN,
                    anchor="center",
                )
            widget.grid(
                row=row_index + 1,
                column=column_index,
                sticky="ew",
                padx=TABLE_CELL_PADX,
                pady=TABLE_CELL_PADY,
            )
            widgets[column.key] = widget
        self._variables.append(variables)
        self._cell_widgets.append(widgets)

    def _paste(self, event: tk.Event, row_index: int, column_index: int) -> str:
        try:
            text = self.clipboard_get()
        except tk.TclError:
            return "break"
        matrix = _parse_tsv(text)
        if not matrix:
            return "break"
        input_columns = [
            (index, column)
            for index, column in enumerate(self.model.spec.columns)
            if column.role is BatchColumnRole.INPUT
        ]
        input_positions = {index: offset for offset, (index, _column) in enumerate(input_columns)}
        start_offset = input_positions.get(column_index)
        if start_offset is None:
            return "break"
        for row_offset, values in enumerate(matrix):
            target_row = row_index + row_offset
            while target_row >= len(self.model.rows):
                self.model.add_row()
            for value_offset, value in enumerate(values):
                target_offset = start_offset + value_offset
                if target_offset >= len(input_columns):
                    continue
                _target_index, column = input_columns[target_offset]
                self.model.set_cell(target_row, column.key, value)
        self._rebuild_rows()
        return "break"


def _parse_tsv(text: str) -> list[list[str]]:
    rows = [line.split("\t") for line in text.rstrip("\n").splitlines()]
    return [row for row in rows if row]
