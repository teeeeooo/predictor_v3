"""Read-only result text panel for the Tkinter calculator MVP."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk


class ResultPanel:
    """Multi-line read-only text result + clipboard copy / clear."""

    def __init__(self, parent: tk.Widget, *, title: str = "결과") -> None:
        self._frame = ttk.LabelFrame(parent, text=title)
        self._text = tk.Text(self._frame, height=10, width=60, wrap="word")
        self._text.configure(state=tk.DISABLED)
        self._text.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=4, pady=4)
        ttk.Button(self._frame, text="결과 복사", command=self.copy).pack(
            side=tk.LEFT, padx=4, pady=4
        )
        ttk.Button(self._frame, text="결과 지우기", command=self.clear).pack(
            side=tk.LEFT, padx=4, pady=4
        )

    def pack(self, **kwargs) -> None:
        self._frame.pack(**kwargs)

    def append(self, text: str) -> None:
        self._text.configure(state=tk.NORMAL)
        if self._text.get("1.0", tk.END).strip():
            self._text.insert(tk.END, "\n")
        self._text.insert(tk.END, text)
        self._text.configure(state=tk.DISABLED)

    def set_text(self, text: str) -> None:
        self._text.configure(state=tk.NORMAL)
        self._text.delete("1.0", tk.END)
        self._text.insert(tk.END, text)
        self._text.configure(state=tk.DISABLED)

    def clear(self) -> None:
        self._text.configure(state=tk.NORMAL)
        self._text.delete("1.0", tk.END)
        self._text.configure(state=tk.DISABLED)

    def copy(self) -> None:
        contents = self._text.get("1.0", tk.END).rstrip()
        if not contents:
            return
        widget = self._text
        widget.clipboard_clear()
        widget.clipboard_append(contents)
