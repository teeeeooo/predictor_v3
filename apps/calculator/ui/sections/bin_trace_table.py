"""Read-only bin trace table for Tkinter ISO/ISEER 2-point results."""

from __future__ import annotations

from collections.abc import Iterable, Mapping

import tkinter as tk
from tkinter import ttk

from apps.calculator.ui.table_clipboard import copy_table_to_clipboard
from apps.calculator.ui.layout_constants import (
    RESULT_STATUS_FG,
    TABLE_BODY_FONT,
    TABLE_CELL_PADX,
    TABLE_CELL_PADY,
    TABLE_DATA_COLUMN_CHARS,
)
from apps.calculator.ui.sections.bin_detail_schema import (
    BinDetailSchema,
    COOLING_BIN_DETAIL_SCHEMA,
)

_MAX_VISIBLE_ROWS = 10


class BinTraceTable:
    """Section-local, read-only table for calculator ``bin_details`` rows."""

    def __init__(
        self,
        parent: tk.Widget,
        *,
        title: str | None = None,
        schema: BinDetailSchema = COOLING_BIN_DETAIL_SCHEMA,
    ) -> None:
        self.layout_policy = "responsive"
        self.surface_role = "bin_trace_surface"
        self.schema = schema
        self.column_labels = schema.column_labels
        self.rows: tuple[tuple[str, ...], ...] = ()

        self._frame = ttk.Frame(parent)
        label_text = title if title is not None else schema.table_title
        self.title_label = ttk.Label(self._frame, text=label_text)
        self.title_label.pack(side=tk.TOP, anchor="w", pady=(0, 4))

        self._table_frame = ttk.Frame(self._frame)
        self._table_frame.pack(side=tk.TOP, fill=tk.X)
        self.table = ttk.Treeview(
            self._table_frame,
            columns=self.column_labels,
            show="headings",
            height=1,
            selectmode="browse",
        )
        self.table.surface_role = "bin_trace_table"
        self.scrollbar = ttk.Scrollbar(
            self._table_frame, orient=tk.VERTICAL, command=self.table.yview
        )
        self.table.configure(yscrollcommand=self.scrollbar.set)
        self.table.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        for column in self.column_labels:
            self.table.heading(column, text=column)
            self.table.column(
                column,
                anchor=tk.CENTER,
                width=TABLE_DATA_COLUMN_CHARS * 9,
                minwidth=80,
                stretch=True,
            )

        self.table.bind("<Control-c>", self.copy)
        self.table.bind("<Command-c>", self.copy)
        self.table.bind("<Control-a>", self.select_all)
        self.table.bind("<Command-a>", self.select_all)

        self.status_label = tk.Label(
            self._frame,
            text="",
            anchor="w",
            foreground=RESULT_STATUS_FG,
            font=TABLE_BODY_FONT,
            padx=TABLE_CELL_PADX,
            pady=TABLE_CELL_PADY,
        )
        self.status_label.surface_role = "bin_trace_status"

    def grid(self, **kwargs) -> None:
        self._frame.grid(**kwargs)

    def grid_remove(self) -> None:
        self._frame.grid_remove()

    def is_visible(self) -> bool:
        return bool(self._frame.winfo_manager())

    def set_data(self, bin_details: Iterable[Mapping[str, object]] | None) -> None:
        rows = tuple(_trace_row(item, self.schema.column_keys) for item in (bin_details or ()))
        self._clear_tree()
        self.rows = rows
        if self.status_label.winfo_manager():
            self.status_label.pack_forget()
        if not self._table_frame.winfo_manager():
            self._table_frame.pack(side=tk.TOP, fill=tk.X)
        self.table.configure(height=max(1, min(len(rows), _MAX_VISIBLE_ROWS)))
        for row in rows:
            self.table.insert("", tk.END, values=row)
        if not rows:
            self.set_status("상세 데이터 없음")

    def set_status(self, status: str) -> None:
        self._clear_tree()
        self.rows = ()
        self._table_frame.pack_forget()
        self.status_label.configure(text=status)
        if not self.status_label.winfo_manager():
            self.status_label.pack(side=tk.TOP, fill=tk.X)

    def table_rows(self) -> tuple[tuple[str, ...], ...]:
        return self.rows

    def table_export_data(self) -> tuple[tuple[str, ...], tuple[tuple[str, ...], ...]]:
        if self.rows:
            return self.column_labels, self.rows
        status = self.status_label.cget("text") or "상세 데이터 없음"
        return ("Status",), ((status,),)

    def copy_table(self) -> bool:
        headers, rows = self.table_export_data()
        return copy_table_to_clipboard(self.table, headers, rows)

    def as_text(self) -> str:
        if not self.rows:
            return self.status_label.cget("text")
        lines = ["\t".join(self.column_labels)]
        lines.extend("\t".join(row) for row in self.rows)
        return "\n".join(lines)

    def copy(self, _event: tk.Event | None = None) -> str:
        self.copy_table()
        return "break"

    def select_all(self, _event: tk.Event | None = None) -> str:
        self.table.selection_set(self.table.get_children())
        return "break"

    def _clear_tree(self) -> None:
        for item_id in self.table.get_children():
            self.table.delete(item_id)


def _trace_row(item: Mapping[str, object], column_keys: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(_format_value(item.get(key)) for key in column_keys)


def _format_value(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.2f}"
    return str(value)
