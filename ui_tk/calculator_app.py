"""Tkinter calculator-only top-level shell.

This module is the production-candidate top-level shell for the
lightweight calculator-only deployment direction (see
``docs/designs/2026-05-22-lightweight-calculator-ui-feasibility.md``).
The PyQt5 calculator UI under ``ui/`` remains the reference
implementation; this shell does not replace it. No PyQt imports.

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

from ui_tk.tabs.iso16358_tab import Iso16358Tab
from ui_tk.window_geometry import (
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

        notebook = ttk.Notebook(self.root)
        notebook.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.iso_tab = Iso16358Tab(notebook)
        notebook.add(self.iso_tab, text="ISO 16358")
        self.root.update_idletasks()
        center_window(self.root, self.iso_tab.preferred_initial_size())
        apply_overflow_correction(self.root, self.iso_tab)
        clamp_window_to_visible_bounds(self.root)
        self.root.after_idle(self.iso_tab.fit_toplevel_to_current_content_once)

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    CalculatorTkApp().run()


if __name__ == "__main__":
    main()
