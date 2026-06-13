"""Summary result panel with retained text/copy compatibility APIs."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Iterable

from apps.calculator.ui.layout_constants import (
    RESULT_HEADER_BG,
    RESULT_STATUS_FG,
    RESULT_TITLE_BG,
    RESULT_VALUE_BG,
    TABLE_BODY_FONT,
    TABLE_CELL_PADX,
    TABLE_CELL_PADY,
    TABLE_GRID_COLOR,
    TABLE_HEADER_FONT,
    TABLE_HEADER_PADY,
)
from apps.calculator.ui.result_models import ResultSummary


class ResultPanel:
    """Latest compact summary tables with retained text compatibility APIs."""

    def __init__(
        self,
        parent: tk.Widget,
        *,
        title: str = "결과",
        layout_policy: str = "content_hug",
    ) -> None:
        if layout_policy not in {"responsive", "content_hug"}:
            raise ValueError(
                "ResultPanel layout_policy must be 'responsive' or 'content_hug'"
            )
        self.layout_policy = layout_policy
        self._frame = ttk.Frame(parent)
        self.title_label = ttk.Label(self._frame, text=title)
        self.title_label.pack(side=tk.TOP, anchor="w", pady=(0, 4))
        self._summary_holder = ttk.Frame(self._frame)
        if self.layout_policy == "content_hug":
            self._summary_holder.pack(side=tk.TOP, anchor="w")
        else:
            self._summary_holder.pack(side=tk.TOP, fill=tk.X)
        self.summary_tables: dict[str, tk.Frame] = {}
        self.summary_header_cells: dict[str, tuple[tk.Frame, ...]] = {}
        self.summary_value_cells: dict[str, tuple[tk.Frame, ...]] = {}
        self.summary_value_labels: dict[str, tuple[tk.Label, ...]] = {}
        self.summary_status_labels: dict[str, tk.Label] = {}
        self._summary_shapes: dict[str, tuple[str, tuple[str, ...]]] = {}
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
        if self._can_update_in_place(summaries):
            self._update_summary_values(summaries)
        else:
            external_focus = self._capture_external_focus()
            self._clear_summary_tables()
            for row, summary in enumerate(summaries):
                self._render_summary_table(row, summary)
            if external_focus is not None:
                self._restore_focus_if_alive(external_focus)
        self._set_copy_text("\n\n".join(summary.as_text() for summary in summaries))

    def clear(self) -> None:
        self._clear_summary_tables()
        self._hide_text_mode()
        self._set_copy_text("")

    @staticmethod
    def _shape_for(summary: ResultSummary) -> tuple[str, tuple[str, ...]]:
        return (summary.title, tuple(label for label, _value in summary.fields))

    def _can_update_in_place(self, summaries: tuple[ResultSummary, ...]) -> bool:
        if not self.summary_tables:
            return False
        new_shapes = {summary.title: self._shape_for(summary) for summary in summaries}
        if set(self._summary_shapes) != set(new_shapes):
            return False
        return all(
            self._summary_shapes[title] == new_shapes[title]
            for title in self._summary_shapes
        )

    def _update_summary_values(self, summaries: tuple[ResultSummary, ...]) -> None:
        for summary in summaries:
            value_labels = self.summary_value_labels.get(summary.title)
            if value_labels:
                for label, (_, value) in zip(value_labels, summary.fields):
                    label.configure(text=value)
            status_label = self.summary_status_labels.get(summary.title)
            if status_label is not None:
                status_label.configure(text=summary.status)

    def _make_summary_cell(
        self, card: tk.Frame, *, row: int, column: int, background: str
    ) -> tk.Frame:
        cell = tk.Frame(card, background=background, borderwidth=0)
        cell.grid(row=row, column=column, sticky="nsew", padx=(0, 1), pady=(0, 1))
        card.columnconfigure(
            column,
            weight=0 if self.layout_policy == "content_hug" else 1,
        )
        return cell

    def _render_summary_table(self, row: int, summary: ResultSummary) -> None:
        card = tk.Frame(
            self._summary_holder,
            name=f"{summary.title.lower()}_summary",
            background=TABLE_GRID_COLOR,
            borderwidth=1,
            relief=tk.SOLID,
        )
        card.grid(
            row=row,
            column=0,
            sticky="w" if self.layout_policy == "content_hug" else "ew",
            pady=(0, 8),
        )
        card.layout_policy = self.layout_policy
        self.summary_tables[summary.title] = card
        self._summary_shapes[summary.title] = self._shape_for(summary)
        self._summary_holder.columnconfigure(
            0,
            weight=0 if self.layout_policy == "content_hug" else 1,
        )
        if not summary.fields:
            card.surface_role = "status_surface"
            self._render_status(card, summary, row=0)
            return

        card.surface_role = "summary_table"
        title_label = tk.Label(
            card,
            text=summary.title,
            anchor="w",
            background=RESULT_TITLE_BG,
            font=TABLE_HEADER_FONT,
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
        if not summary.fields:
            card.columnconfigure(
                0,
                weight=0 if self.layout_policy == "content_hug" else 1,
            )
        status = tk.Label(
            card,
            text=summary.status,
            anchor="w",
            background=RESULT_VALUE_BG,
            foreground=RESULT_STATUS_FG,
            font=TABLE_BODY_FONT,
            padx=TABLE_CELL_PADX,
            pady=TABLE_CELL_PADY,
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
        value_labels: list[tk.Label] = []
        for column, (label, value) in enumerate(summary.fields):
            card.columnconfigure(
                column,
                weight=0 if self.layout_policy == "content_hug" else 1,
            )
            header = self._make_summary_cell(
                card, row=1, column=column, background=RESULT_HEADER_BG
            )
            header.surface_role = "summary_header_cell"
            tk.Label(
                header,
                text=label,
                background=RESULT_HEADER_BG,
                font=TABLE_HEADER_FONT,
            ).pack(
                fill=tk.BOTH,
                expand=True,
                padx=TABLE_CELL_PADX,
                pady=TABLE_HEADER_PADY,
            )
            value_cell = self._make_summary_cell(
                card, row=2, column=column, background=RESULT_VALUE_BG
            )
            value_cell.surface_role = "summary_value_cell"
            value_label = tk.Label(
                value_cell, text=value, background=RESULT_VALUE_BG, font=TABLE_BODY_FONT
            )
            value_label.pack(fill=tk.BOTH, expand=True, padx=TABLE_CELL_PADX, pady=TABLE_CELL_PADY)
            headers.append(header)
            values.append(value_cell)
            value_labels.append(value_label)
        self.summary_header_cells[summary.title] = tuple(headers)
        self.summary_value_cells[summary.title] = tuple(values)
        self.summary_value_labels[summary.title] = tuple(value_labels)

    def _clear_summary_tables(self) -> None:
        for child in self._summary_holder.winfo_children():
            child.destroy()
        self.summary_tables.clear()
        self._summary_shapes.clear()
        self.summary_header_cells.clear()
        self.summary_value_cells.clear()
        self.summary_value_labels.clear()
        self.summary_status_labels.clear()

    def _capture_external_focus(self) -> tk.Widget | None:
        focused = self._frame.focus_get()
        if focused is None:
            return None
        if self._is_descendant_of_panel(focused):
            return None
        return focused

    def _is_descendant_of_panel(self, widget: tk.Widget) -> bool:
        try:
            while widget is not None:
                if widget == self._frame:
                    return True
                parent = widget.winfo_parent()
                if not parent:
                    break
                widget = widget.nametowidget(parent)
        except tk.TclError:
            pass
        return False

    def _restore_focus_if_alive(self, widget: tk.Widget) -> None:
        try:
            if widget.winfo_exists():
                widget.focus_set()
        except tk.TclError:
            pass

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
