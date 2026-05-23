"""Summary result panel with retained text/copy compatibility APIs."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Iterable

from ui_tk.result_models import ResultSummary


class ResultPanel:
    """Latest summary cards plus clipboard copy / clear."""

    def __init__(self, parent: tk.Widget, *, title: str = "결과") -> None:
        self._frame = ttk.LabelFrame(parent, text=title)
        self._summary_holder = ttk.Frame(self._frame)
        self._summary_holder.pack(side=tk.TOP, fill=tk.X, padx=6, pady=6)
        self._text = tk.Text(self._frame, height=10, width=60, wrap="word")
        self._text.configure(state=tk.DISABLED)
        ttk.Button(self._frame, text="결과 복사", command=self.copy).pack(
            side=tk.LEFT, padx=4, pady=4
        )
        ttk.Button(self._frame, text="결과 지우기", command=self.clear).pack(
            side=tk.LEFT, padx=4, pady=4
        )

    def pack(self, **kwargs) -> None:
        self._frame.pack(**kwargs)

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
        for child in self._summary_holder.winfo_children():
            child.destroy()
        for row, summary in enumerate(summaries):
            card = ttk.LabelFrame(self._summary_holder, text=summary.title)
            card.grid(row=row, column=0, sticky="ew", pady=(0, 8))
            self._summary_holder.columnconfigure(0, weight=1)
            if summary.fields:
                for column, (label, value) in enumerate(summary.fields):
                    ttk.Label(card, text=label).grid(
                        row=0, column=column, sticky="w", padx=10, pady=(6, 2)
                    )
                    ttk.Label(card, text=value).grid(
                        row=1, column=column, sticky="w", padx=10, pady=(2, 6)
                    )
            ttk.Label(card, text=summary.status).grid(
                row=2 if summary.fields else 0,
                column=0,
                columnspan=max(len(summary.fields), 1),
                sticky="w",
                padx=10,
                pady=(2, 6),
            )
        self._set_copy_text("\n\n".join(summary.as_text() for summary in summaries))

    def clear(self) -> None:
        for child in self._summary_holder.winfo_children():
            child.destroy()
        self._hide_text_mode()
        self._set_copy_text("")

    def _set_copy_text(self, text: str) -> None:
        self._text.configure(state=tk.NORMAL)
        self._text.delete("1.0", tk.END)
        self._text.insert(tk.END, text)
        self._text.configure(state=tk.DISABLED)

    def _show_text_mode(self) -> None:
        for child in self._summary_holder.winfo_children():
            child.destroy()
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
