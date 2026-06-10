"""Reusable Tkinter input widget primitives for the calculator MVP.

Only stdlib Tkinter / ttk imports. No PyQt imports.
"""

from __future__ import annotations

from typing import Optional

import tkinter as tk
from tkinter import ttk


class NumericEntryRow:
    """One labeled numeric entry. ``get_value`` returns ``None`` when
    blank and ``allow_empty=True``; otherwise raises ``ValueError``.
    """

    def __init__(
        self,
        parent: tk.Widget,
        label: str,
        *,
        width: int = 12,
        label_width: int = 22,
    ) -> None:
        self._frame = ttk.Frame(parent)
        ttk.Label(self._frame, text=label, width=label_width, anchor="w").pack(
            side=tk.LEFT
        )
        self._entry = ttk.Entry(self._frame, width=width)
        self._entry.pack(side=tk.LEFT)

    def grid(self, **kwargs) -> None:
        self._frame.grid(**kwargs)

    def pack(self, **kwargs) -> None:
        self._frame.pack(**kwargs)

    def get_value(self, *, allow_empty: bool = False) -> Optional[float]:
        text = self._entry.get().strip().replace(",", "")
        if not text:
            if allow_empty:
                return None
            raise ValueError("값이 비어 있습니다.")
        return float(text)

    def set_value(self, text: str) -> None:
        self._entry.delete(0, tk.END)
        self._entry.insert(0, text)
