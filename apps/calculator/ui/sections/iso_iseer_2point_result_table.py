"""Read-only comparison result table for Tkinter ISO/ISEER 2-point."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from apps.calculator.ui.table_clipboard import copy_table_to_clipboard
from apps.calculator.ui.layout_constants import (
    RESULT_COMPARISON_VALUE_COLUMN_MIN_WIDTH_PX,
    RESULT_COMPARISON_VALUE_COLUMN_WIDTH_PX,
    RESULT_PROFILE_COLUMN_MIN_WIDTH_PX,
    RESULT_PROFILE_COLUMN_WIDTH_PX,
    RESULT_STATUS_FG,
    TABLE_BODY_FONT,
    TABLE_CELL_PADX,
    TABLE_CELL_PADY,
)

TWO_POINT_RESULT_COLUMNS: tuple[str, ...] = (
    "Region/Profile",
    "EER Full",
    "EER Half",
    "CSPF/ISEER",
    "CSTL [kWh]",
    "CSEC [kWh]",
)


class IsoIseer2PointResultTable:
    """Section-local, read-only profile comparison surface."""

    def __init__(self, parent: tk.Widget, *, title: str = "ISO / ISEER 결과") -> None:
        self.layout_policy = "content_hug"
        self.surface_role = "two_point_result_surface"
        self.column_labels = TWO_POINT_RESULT_COLUMNS
        self.row_labels: tuple[str, ...] = ()
        self.rows: tuple[tuple[str, ...], ...] = ()

        self._frame = ttk.Frame(parent)
        self.title_label = ttk.Label(self._frame, text=title)
        self.title_label.pack(side=tk.TOP, anchor="w", pady=(0, 4))

        self.table = ttk.Treeview(
            self._frame,
            columns=self.column_labels,
            show="headings",
            height=2,
            selectmode="browse",
        )
        self.table.surface_role = "two_point_comparison_table"
        self.table.pack(side=tk.TOP, anchor="w")
        for column in self.column_labels:
            self.table.heading(column, text=column)
            self.table.column(
                column,
                anchor=tk.CENTER,
                width=RESULT_COMPARISON_VALUE_COLUMN_WIDTH_PX,
                minwidth=RESULT_COMPARISON_VALUE_COLUMN_MIN_WIDTH_PX,
                stretch=False,
            )
        self.table.column(
            "Region/Profile",
            anchor=tk.W,
            width=RESULT_PROFILE_COLUMN_WIDTH_PX,
            minwidth=RESULT_PROFILE_COLUMN_MIN_WIDTH_PX,
            stretch=False,
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
        self.status_label.surface_role = "two_point_result_status"

        self._text = tk.Text(self._frame, height=6, width=70, wrap="none")
        self._text.configure(state=tk.DISABLED)

    def grid(self, **kwargs) -> None:
        self._frame.grid(**kwargs)

    def set_rows(self, rows: tuple[tuple[str, ...], ...], *, status: str) -> None:
        self._show_table()
        self._clear_tree()
        self.rows = rows
        self.row_labels = tuple(row[0] for row in rows)
        for row in rows:
            self.table.insert("", tk.END, values=row)
        self.status_label.configure(text=status)
        if not self.status_label.winfo_manager():
            self.status_label.pack(side=tk.TOP, anchor="w", pady=(4, 0))
        self._set_copy_text(self.as_text())

    def set_status(self, status: str) -> None:
        self._clear_tree()
        self.rows = ()
        self.row_labels = ()
        self.table.pack_forget()
        self.status_label.configure(text=status)
        if not self.status_label.winfo_manager():
            self.status_label.pack(side=tk.TOP, anchor="w", pady=(4, 0))
        self._set_copy_text(status)

    def clear(self) -> None:
        self._clear_tree()
        self.rows = ()
        self.row_labels = ()
        self.status_label.configure(text="")
        self.status_label.pack_forget()
        self.table.pack_forget()
        self._set_copy_text("")

    def as_text(self) -> str:
        if not self.rows:
            return self.status_label.cget("text")
        lines = ["\t".join(self.column_labels)]
        lines.extend("\t".join(row) for row in self.rows)
        status = self.status_label.cget("text")
        if status:
            lines.append(status)
        return "\n".join(lines)

    def table_export_data(self) -> tuple[tuple[str, ...], tuple[tuple[str, ...], ...]]:
        if self.rows:
            return self.column_labels, self.rows
        status = self.status_label.cget("text") or "No result rows"
        return ("Status",), ((status,),)

    def copy_table(self) -> bool:
        headers, rows = self.table_export_data()
        return copy_table_to_clipboard(self.table, headers, rows)

    def copy(self, _event: tk.Event | None = None) -> str:
        self.copy_table()
        return "break"

    def select_all(self, _event: tk.Event | None = None) -> str:
        self.table.selection_set(self.table.get_children())
        return "break"

    def _show_table(self) -> None:
        if not self.table.winfo_manager():
            self.table.pack(side=tk.TOP, anchor="w")

    def _clear_tree(self) -> None:
        for item_id in self.table.get_children():
            self.table.delete(item_id)

    def _set_copy_text(self, text: str) -> None:
        self._text.configure(state=tk.NORMAL)
        self._text.delete("1.0", tk.END)
        self._text.insert(tk.END, text)
        self._text.configure(state=tk.DISABLED)
