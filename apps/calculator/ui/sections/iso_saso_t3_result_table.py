"""Read-only comparison result table for Tkinter SASO T3."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from apps.calculator.ui.layout_constants import (
    RESULT_STATUS_FG,
    TABLE_BODY_FONT,
    TABLE_CELL_PADX,
    TABLE_CELL_PADY,
)
from apps.calculator.ui.table.compact_result_grid import CompactResultGrid
from apps.calculator.ui.table.visual_policy import SemanticTone
from apps.calculator.ui.table_clipboard import copy_table_to_clipboard

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
        self.layout_policy = "content_hug"
        self.surface_role = "saso_t3_result_surface"
        self.column_labels = SASO_T3_RESULT_COLUMNS
        self.row_labels: tuple[str, ...] = ()
        self.rows: tuple[tuple[str, ...], ...] = ()
        self._placeholder_row_labels: tuple[str, ...] = ()

        self._frame = ttk.Frame(parent)
        self.title_label = ttk.Label(self._frame, text=title)
        self.title_label.pack(side=tk.TOP, anchor="w", pady=(0, 4))

        self.table = CompactResultGrid(
            self._frame,
            headers=self.column_labels,
            column_widths=(24, 12, 12, 12, 12, 12, 12, 12),
            surface_role="saso_t3_comparison_table",
        )
        self.table.pack(side=tk.TOP, anchor="w")

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

    def show_placeholder(self, row_labels: tuple[str, ...], *, status: str) -> None:
        """Show reserved comparison rows without making them exportable results."""
        self.rows = ()
        self.row_labels = ()
        self._placeholder_row_labels = row_labels
        self.table.set_rows(
            tuple((label, *("-" for _ in self.column_labels[1:])) for label in row_labels)
        )
        self._show_table()
        self.status_label.configure(text=status)
        if not self.status_label.winfo_manager():
            self.status_label.pack(side=tk.TOP, anchor="w", pady=(4, 0))
        self._set_copy_text(status)

    def grid(self, **kwargs) -> None:
        self._frame.grid(**kwargs)

    def set_rows(self, rows: tuple[tuple[str, ...], ...], *, status: str) -> None:
        self._show_table()
        self.rows = rows
        self.row_labels = tuple(row[0] for row in rows)
        self.table.set_rows(
            rows,
            tones={
                (row, column): SemanticTone.CALCULATED
                for row in range(len(rows))
                for column in range(1, len(self.column_labels))
            },
        )
        self.status_label.configure(text=status)
        if not self.status_label.winfo_manager():
            self.status_label.pack(side=tk.TOP, anchor="w", pady=(4, 0))
        self._set_copy_text(self.as_text())

    def set_status(self, status: str) -> None:
        self.show_placeholder(
            self._placeholder_row_labels or ("Required only (3-point)",),
            status=status,
        )

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
        return copy_table_to_clipboard(self.table.frame, headers, rows)

    def copy(self, _event: tk.Event | None = None) -> str:
        self.copy_table()
        return "break"

    def select_all(self, _event: tk.Event | None = None) -> str:
        return "break"

    def _show_table(self) -> None:
        if not self.table.winfo_manager():
            self.table.pack(side=tk.TOP, anchor="w")

    def _set_copy_text(self, text: str) -> None:
        self._text.configure(state=tk.NORMAL)
        self._text.delete("1.0", tk.END)
        self._text.insert(tk.END, text)
        self._text.configure(state=tk.DISABLED)
