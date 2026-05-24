"""Summary result panel with retained text/copy compatibility APIs."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Iterable

from ui_tk.result_models import ResultSummary

_GRID_LINE = "#c4ccd4"
_TITLE_BACKGROUND = "#f1f3f5"
_HEADER_BACKGROUND = "#e8edf2"
_VALUE_BACKGROUND = "#ffffff"
_STATUS_FOREGROUND = "#52606d"


class ResultPanel:
    """Latest compact summary tables with retained text compatibility APIs."""

    def __init__(self, parent: tk.Widget, *, title: str = "결과") -> None:
        self._frame = ttk.LabelFrame(parent, text=title)
        self._summary_holder = ttk.Frame(self._frame)
        self._summary_holder.pack(side=tk.TOP, fill=tk.X, padx=6, pady=6)
        self.summary_tables: dict[str, tk.Frame] = {}
        self.summary_header_cells: dict[str, tuple[tk.Frame, ...]] = {}
        self.summary_value_cells: dict[str, tuple[tk.Frame, ...]] = {}
        self.summary_status_labels: dict[str, tk.Label] = {}
        self._text = tk.Text(self._frame, height=10, width=60, wrap="word")
        self._text.configure(state=tk.DISABLED)

    def pack(self, **kwargs) -> None:
        self._frame.pack(**kwargs)

    def grid(self, **kwargs) -> None:
        self._frame.grid(**kwargs)

    def append(self, text: str) -> None:
        self._show_text_mode()
        self._text.configure(state=tk.NORMAL)
        if self._text.get("1.0", tk.END).strip():
            self._text.insert(tk.END, "\n")
        self._text.insert(tk.END, text)
        self._text.configure(state=tk.DISABLED)

    def set_text(self, text: str) -> None:
        self._show_text_mode()
        self._text.configure(state=tk.NORMAL)
        self._text.delete("1.0", tk.END)
        self._text.insert(tk.END, text)
        self._text.configure(state=tk.DISABLED)

    def set_summaries(self, summaries: Iterable[ResultSummary]) -> None:
        """Render latest metric summaries as compact cards and copy text."""
        summaries = tuple(summaries)
        self._hide_text_mode()
        self._clear_summary_tables()
        for row, summary in enumerate(summaries):
            self._render_summary_table(row, summary)
        self._set_copy_text("\n\n".join(summary.as_text() for summary in summaries))

    def clear(self) -> None:
        self._clear_summary_tables()
        self._hide_text_mode()
        self._set_copy_text("")

    def _make_summary_cell(
        self, card: tk.Frame, *, row: int, column: int, background: str
    ) -> tk.Frame:
        cell = tk.Frame(card, background=background, borderwidth=0)
        cell.grid(row=row, column=column, sticky="nsew", padx=(0, 1), pady=(0, 1))
        card.columnconfigure(column, weight=1)
        return cell

    def _render_summary_table(self, row: int, summary: ResultSummary) -> None:
        card = tk.Frame(
            self._summary_holder,
            name=f"{summary.title.lower()}_summary",
            background=_GRID_LINE,
            borderwidth=1,
            relief=tk.SOLID,
        )
        card.grid(row=row, column=0, sticky="ew", pady=(0, 8))
        self.summary_tables[summary.title] = card
        self._summary_holder.columnconfigure(0, weight=1)
        if not summary.fields:
            card.surface_role = "status_surface"
            self._render_status(card, summary, row=0)
            return

        card.surface_role = "summary_table"
        title_label = tk.Label(
            card,
            text=summary.title,
            anchor="w",
            background=_TITLE_BACKGROUND,
            font=("TkDefaultFont", 10, "bold"),
        )
        title_label.grid(
            row=0,
            column=0,
            columnspan=max(len(summary.fields), 1),
            sticky="ew",
            padx=(0, 1),
            pady=(0, 1),
        )
        title_label.surface_role = "summary_title"
        self._render_result_values(card, summary)
        self._render_status(card, summary, row=3)

    def _render_status(
        self, card: tk.Frame, summary: ResultSummary, *, row: int
    ) -> None:
        status = tk.Label(
            card,
            text=summary.status,
            anchor="w",
            background=_VALUE_BACKGROUND,
            foreground=_STATUS_FOREGROUND,
            padx=10,
            pady=5,
        )
        status.grid(
            row=row,
            column=0,
            columnspan=max(len(summary.fields), 1),
            sticky="ew",
            padx=(0, 1),
            pady=(0, 1),
        )
        status.surface_role = "summary_status"
        self.summary_status_labels[summary.title] = status

    def _render_result_values(self, card: tk.Frame, summary: ResultSummary) -> None:
        headers = []
        values = []
        for column, (label, value) in enumerate(summary.fields):
            header = self._make_summary_cell(
                card, row=1, column=column, background=_HEADER_BACKGROUND
            )
            header.surface_role = "summary_header_cell"
            tk.Label(
                header,
                text=label,
                background=_HEADER_BACKGROUND,
                font=("TkDefaultFont", 10, "bold"),
            ).pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
            value_cell = self._make_summary_cell(
                card, row=2, column=column, background=_VALUE_BACKGROUND
            )
            value_cell.surface_role = "summary_value_cell"
            tk.Label(
                value_cell, text=value, background=_VALUE_BACKGROUND
            ).pack(fill=tk.BOTH, expand=True, padx=10, pady=6)
            headers.append(header)
            values.append(value_cell)
        self.summary_header_cells[summary.title] = tuple(headers)
        self.summary_value_cells[summary.title] = tuple(values)

    def _clear_summary_tables(self) -> None:
        for child in self._summary_holder.winfo_children():
            child.destroy()
        self.summary_tables.clear()
        self.summary_header_cells.clear()
        self.summary_value_cells.clear()
        self.summary_status_labels.clear()

    def _set_copy_text(self, text: str) -> None:
        self._text.configure(state=tk.NORMAL)
        self._text.delete("1.0", tk.END)
        self._text.insert(tk.END, text)
        self._text.configure(state=tk.DISABLED)

    def _show_text_mode(self) -> None:
        self._clear_summary_tables()
        if not self._text.winfo_manager():
            self._text.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=4, pady=4)

    def _hide_text_mode(self) -> None:
        self._text.pack_forget()

    def copy(self) -> None:
        contents = self._text.get("1.0", tk.END).rstrip()
        if not contents:
            return
        widget = self._text
        widget.clipboard_clear()
        widget.clipboard_append(contents)
