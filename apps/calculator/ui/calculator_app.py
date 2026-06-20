"""Tkinter calculator-only top-level shell.

This module (``apps.calculator.ui.calculator_app``) is the current Tkinter
calculator UI shell used by ``apps.calculator.app``.

The legacy PyQt calculator under ``ui/`` remains a read-only reference
only until its retirement. No PyQt imports are allowed in this module or in
this Tkinter UI package.

Responsibilities here are intentionally narrow:
- Build the Tk root window + ``ttk.Notebook``.
- Register the supported standard tabs.

Region selection, metric section composition, calculator dispatch,
result display, and input widgets all live in sibling modules.
"""

from __future__ import annotations

from typing import Optional

import tkinter as tk
from tkinter import ttk

from apps.calculator.ui.tabs.iso16358_tab import Iso16358Tab
from apps.calculator.ui.tabs.en14825_tab import En14825Tab
from apps.calculator.ui.tabs.ahri210240_tab import Ahri210240Tab
from apps.calculator.ui.window_geometry import (
    apply_overflow_correction,
    center_window,
    clamp_window_to_visible_bounds,
)


class CalculatorTkApp:
    """Top-level Tkinter calculator app shell.

    The constructor does not call ``mainloop()`` so tests can build the
    widget tree on a withdrawn root. ``run()`` shows the window and
    enters the event loop.
    """

    def __init__(self, root: Optional[tk.Tk] = None) -> None:
        self.root = root if root is not None else tk.Tk()
        self.root.title("Calculator (Tkinter)")

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.iso_tab = Iso16358Tab(self.notebook)
        self.notebook.add(self.iso_tab, text="ISO 16358")

        self.en14825_tab = En14825Tab(self.notebook)
        self.notebook.add(self.en14825_tab, text="EN14825")

        self.ahri210240_tab = Ahri210240Tab(self.notebook)
        self.notebook.add(self.ahri210240_tab, text="AHRI 210/240")

        self._ignore_initial_tab_changed = True
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)

        self.root.update_idletasks()
        initial_size = self.iso_tab.preferred_initial_size()
        self._set_notebook_content_size(initial_size)
        center_window(self.root, initial_size)
        apply_overflow_correction(self.root, self.iso_tab)
        clamp_window_to_visible_bounds(self.root)
        self.root.after(0, self._apply_initial_iso_fit)

    def _apply_initial_iso_fit(self) -> None:
        self._ignore_initial_tab_changed = False
        self.iso_tab.fit_toplevel_to_current_content_once()

    def _on_tab_changed(self, event: tk.Event) -> None:
        if self._ignore_initial_tab_changed:
            return
        notebook = event.widget
        selected_tab = notebook.nametowidget(notebook.select())
        if hasattr(selected_tab, "preferred_initial_size"):
            self._set_notebook_content_size(selected_tab.preferred_initial_size())
        if hasattr(selected_tab, "fit_toplevel_to_current_content_once"):
            selected_tab.fit_toplevel_to_current_content_once()

    def _set_notebook_content_size(self, size: tuple[int, int]) -> None:
        width, height = size
        self.notebook.configure(width=max(1, width), height=max(1, height))

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    CalculatorTkApp().run()


if __name__ == "__main__":
    main()
