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

from ui_tk.layout_constants import (
    APP_WINDOW_FALLBACK_MIN_HEIGHT,
    APP_WINDOW_FALLBACK_MIN_WIDTH,
    APP_WINDOW_MAX_HEIGHT_RATIO,
    APP_WINDOW_MAX_WIDTH_RATIO,
    APP_WINDOW_MIN_HEIGHT_RATIO,
    APP_WINDOW_MIN_VISIBLE_HEIGHT,
    APP_WINDOW_MIN_VISIBLE_WIDTH,
    APP_WINDOW_MIN_WIDTH_RATIO,
    APP_WINDOW_SCREEN_MARGIN_X_RATIO,
    APP_WINDOW_SCREEN_MARGIN_Y_RATIO,
)
from ui_tk.tabs.iso16358_tab import Iso16358Tab


def centered_geometry(
    width: int, height: int, screen_width: int, screen_height: int
) -> str:
    width = max(APP_WINDOW_MIN_VISIBLE_WIDTH, width)
    height = max(APP_WINDOW_MIN_VISIBLE_HEIGHT, height)
    x = max(APP_WINDOW_MIN_VISIBLE_WIDTH - 1, (screen_width - width) // 2)
    y = max(APP_WINDOW_MIN_VISIBLE_HEIGHT - 1, (screen_height - height) // 2)
    return f"{width}x{height}+{x}+{y}"


def initial_window_geometry(
    requested_width: int,
    requested_height: int,
    screen_width: int,
    screen_height: int,
) -> str:
    margin_x = int(screen_width * APP_WINDOW_SCREEN_MARGIN_X_RATIO)
    margin_y = int(screen_height * APP_WINDOW_SCREEN_MARGIN_Y_RATIO)
    min_width = min(
        max(APP_WINDOW_FALLBACK_MIN_WIDTH, int(screen_width * APP_WINDOW_MIN_WIDTH_RATIO)),
        screen_width,
    )
    min_height = min(
        max(APP_WINDOW_FALLBACK_MIN_HEIGHT, int(screen_height * APP_WINDOW_MIN_HEIGHT_RATIO)),
        screen_height,
    )
    max_width = max(
        APP_WINDOW_MIN_VISIBLE_WIDTH,
        min(screen_width - margin_x, int(screen_width * APP_WINDOW_MAX_WIDTH_RATIO)),
    )
    max_height = max(
        APP_WINDOW_MIN_VISIBLE_HEIGHT,
        min(screen_height - margin_y, int(screen_height * APP_WINDOW_MAX_HEIGHT_RATIO)),
    )
    width = min(max(min_width, requested_width), max_width)
    height = min(max(min_height, requested_height), max_height)
    return centered_geometry(width, height, screen_width, screen_height)


def resolve_min_window_size(screen_width: int, screen_height: int) -> tuple[int, int]:
    return (
        min(APP_WINDOW_FALLBACK_MIN_WIDTH, screen_width),
        min(APP_WINDOW_FALLBACK_MIN_HEIGHT, screen_height),
    )


def center_window(root: tk.Tk) -> None:
    root.update_idletasks()
    width = max(root.winfo_reqwidth(), root.winfo_width())
    height = max(root.winfo_reqheight(), root.winfo_height())
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.minsize(*resolve_min_window_size(screen_width, screen_height))
    root.geometry(initial_window_geometry(width, height, screen_width, screen_height))


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
