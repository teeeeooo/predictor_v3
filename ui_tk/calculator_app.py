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


def centered_geometry(width: int, height: int, screen_width: int, screen_height: int) -> str:
    width = max(1, width)
    height = max(1, height)
    x = max(0, (screen_width - width) // 2)
    y = max(0, (screen_height - height) // 2)
    return f"{width}x{height}+{x}+{y}"


def center_window(root: tk.Tk) -> None:
    root.update_idletasks()
    width = max(root.winfo_reqwidth(), root.winfo_width())
    height = max(root.winfo_reqheight(), root.winfo_height())
    root.geometry(
        centered_geometry(width, height, root.winfo_screenwidth(), root.winfo_screenheight())
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
        center_window(self.root)

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    CalculatorTkApp().run()


if __name__ == "__main__":
    main()
