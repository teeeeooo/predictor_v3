"""Common Toplevel dialog shell for batch calculation matrix views."""

from __future__ import annotations

import tkinter as tk
from collections.abc import Callable
from typing import Protocol

from apps.calculator.ui.window_geometry import parent_centered_content_geometry


class BatchProfileAdapter(Protocol):
    """Protocol for profile-specific batch matrix widgets."""

    @property
    def title(self) -> str:
        ...

    @property
    def min_size(self) -> tuple[int, int]:
        ...

    def build_content(self, parent: tk.Widget) -> tk.Widget:
        ...

    def dispose(self) -> None:
        ...

    def snapshot(self) -> list[dict[str, str]]:
        ...


class BatchDialogShell:
    """Generic Toplevel container for a BatchProfileAdapter."""

    def __init__(
        self,
        parent: tk.Widget,
        adapter: BatchProfileAdapter,
        *,
        on_close: Callable[[list[dict[str, str]]], None] | None = None,
    ) -> None:
        self._on_close = on_close
        self._adapter = adapter
        self.window = tk.Toplevel(parent)
        self.window.withdraw()
        self.window.title(self._adapter.title)
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)

        # Build content using the adapter
        self.content_widget = self._adapter.build_content(self.window)
        self.content_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # hidden-first geometry settle and show
        self._apply_initial_geometry(parent)
        self.window.protocol("WM_DELETE_WINDOW", self.close)
        self.window.deiconify()
        self.window.lift()

    def _apply_initial_geometry(self, parent: tk.Widget) -> None:
        parent_toplevel = parent.winfo_toplevel()
        parent_toplevel.update_idletasks()
        self.window.update_idletasks()
        min_size = self._adapter.min_size
        self.window.minsize(*min_size)
        geometry = parent_centered_content_geometry(
            parent_toplevel.geometry(),
            (self.window.winfo_reqwidth(), self.window.winfo_reqheight()),
            self.window.winfo_screenwidth(),
            self.window.winfo_screenheight(),
            min_size,
        )
        self.window.geometry(geometry)

    def snapshot(self) -> list[dict[str, str]]:
        return self._adapter.snapshot()

    def close(self) -> None:
        snapshot = self.snapshot()
        self._adapter.dispose()
        if self.window.winfo_exists():
            self.window.destroy()
        if self._on_close is not None:
            self._on_close(snapshot)

    def focus(self) -> None:
        if self.window.winfo_exists():
            self.window.lift()
            self.window.focus_force()
