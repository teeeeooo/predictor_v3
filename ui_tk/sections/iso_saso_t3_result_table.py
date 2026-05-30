"""Read-only comparison result table for Tkinter SASO T3."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from ui_tk.table_clipboard import copy_table_to_clipboard
from ui_tk.layout_constants import (
    RESULT_STATUS_FG,
    TABLE_BODY_FONT,
    TABLE_CELL_PADX,
    TABLE_CELL_PADY,
    TABLE_DATA_COLUMN_CHARS,
)

SASO_T3_RESULT_COLUMNS: tuple[str, ...] = (
    "Scenario",
    "EER 46 Full",
    "EER 35 Full",
    "EER 35 Half",
    "EER 35 Min",
    "CSPF",
    "CSTL [kWh]",
    "CSEC [kWh]",
)


class IsoSasoT3ResultTable:
    """Section-local, read-only SASO 3-point/4-point comparison surface."""

    def __init__(self, parent: tk.Widget, *, title: str = "SASO T3 결과") -> None:
        self.layout_policy = "responsive"
        self.surface_role = "saso_t3_result_surface"
        self.column_labels = SASO_T3_RESULT_COLUMNS
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
        self.table.surface_role = "saso_t3_comparison_table"
        self.table.pack(side=tk.TOP, fill=tk.X)
        for column in self.column_labels:
            self.table.heading(column, text=column)
            self.table.column(
                column,
                anchor=tk.CENTER,
                width=TABLE_DATA_COLUMN_CHARS * 9,
                minwidth=80,
                stretch=True,
            )
        self.table.column("Scenario", anchor=tk.W, width=180, minwidth=150)
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
        self.status_label.surface_role = "saso_t3_result_status"

        self._text = tk.Text(self._frame, height=6, width=90, wrap="none")
        self._text.configure(state=tk.DISABLED)

    def grid(self, **kwargs) -> None:
        self._frame.grid(**kwargs)

    def set_rows(self, rows: tuple[tuple[str, ...], ...], *, status: str) -> None:
        self._show_table()
        self._clear_tree()
        self.rows = rows
        self.row_labels = tuple(row[0] for row in rows)
        self.table.configure(height=max(1, len(rows)))
        for row in rows:
            self.table.insert("", tk.END, values=row)
        self.status_label.configure(text=status)
        if not self.status_label.winfo_manager():
            self.status_label.pack(side=tk.TOP, fill=tk.X, pady=(4, 0))
        self._set_copy_text(self.as_text())

    def set_status(self, status: str) -> None:
        self._clear_tree()
        self.rows = ()
        self.row_labels = ()
        self.table.pack_forget()
        self.status_label.configure(text=status)
        if not self.status_label.winfo_manager():
            self.status_label.pack(side=tk.TOP, fill=tk.X, pady=(4, 0))
        self._set_copy_text(status)

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
            self.table.pack(side=tk.TOP, fill=tk.X)

    def _clear_tree(self) -> None:
        for item_id in self.table.get_children():
            self.table.delete(item_id)

    def _set_copy_text(self, text: str) -> None:
        self._text.configure(state=tk.NORMAL)
        self._text.delete("1.0", tk.END)
        self._text.insert(tk.END, text)
        self._text.configure(state=tk.DISABLED)
