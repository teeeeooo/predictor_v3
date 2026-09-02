"""Tkinter calculator-only top-level shell.

This module (``apps.calculator.ui.calculator_app``) is the current Tkinter
calculator UI shell used by ``apps.calculator.app``.

The retired PyQt calculator path must not be imported or recreated here. No Qt
imports are allowed in this module or in this Tkinter UI package.

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

from apps.calculator.ui.layout_constants import TOP_NOTEBOOK_SELECTED_FG
from apps.calculator.ui.theme import apply_calculator_theme
from apps.calculator.ui.tabs.iso16358_tab import Iso16358Tab
from apps.calculator.ui.tabs.en14825_tab import En14825Tab
from apps.calculator.ui.ahri_m import Ahri210240MTab
from apps.calculator.ui.tabs.ahri210240_tab import Ahri210240Tab
from apps.calculator.ui.tabs.korea_tab import KoreaTab
from apps.calculator.ui.window_geometry import center_window


class CalculatorTkApp:
    """Top-level Tkinter calculator app shell.

    The constructor does not call ``mainloop()`` so tests can build the
    widget tree on a withdrawn root. ``run()`` shows the window and
    enters the event loop.
    """

    _INITIAL_SETTLE_CYCLES = 3

    def __init__(self, root: Optional[tk.Tk] = None) -> None:
        self.root = root if root is not None else tk.Tk()
        self.root.withdraw()
        self.root.title("Seasonal Efficiency Calculator")
        apply_calculator_theme(self.root)
        self._configure_top_notebook_style()

        self.notebook = ttk.Notebook(
            self.root,
            style="CalculatorTop.TNotebook",
        )
        self.notebook.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.iso_tab = Iso16358Tab(self.notebook)
        self.notebook.add(self.iso_tab, text="ISO 16358")

        self.en14825_tab = En14825Tab(self.notebook)
        self.notebook.add(self.en14825_tab, text="EN14825")

        self.ahri210240_m_tab = Ahri210240MTab(self.notebook)
        self.notebook.add(self.ahri210240_m_tab, text="AHRI 210/240 M")

        self.ahri210240_tab = Ahri210240Tab(self.notebook)
        self.notebook.add(self.ahri210240_tab, text="AHRI 210/240 M1")

        self.korea_tab = KoreaTab(self.notebook)
        self.notebook.add(self.korea_tab, text="KS C 9306")

        self._ignore_initial_tab_changed = True
        self._initial_fit_complete = False
        self._initial_settle_remaining = self._INITIAL_SETTLE_CYCLES
        self._run_requested = False
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)

        self.root.update_idletasks()
        initial_size = self.iso_tab.preferred_initial_size()
        self._set_notebook_content_size(initial_size)
        center_window(self.root, initial_size)
        # Mainloop (or a test-driven update) lets the hidden widget tree settle
        # before the one final content fit. Calling ``update()`` from a
        # constructor can re-enter recurring Tk callbacks and hang startup.
        self.root.after_idle(self._settle_initial_fit)

    def _settle_initial_fit(self) -> None:
        if self._initial_fit_complete:
            return
        # This callback already runs only after Tk drains the current idle
        # queue. Re-entering ``update_idletasks()`` from inside it can trap
        # macOS Tk in a nested idle loop after an earlier root was destroyed.
        self._initial_settle_remaining -= 1
        if self._initial_settle_remaining > 0:
            self.root.after_idle(self._settle_initial_fit)
            return
        # A zero-delay timer is intentionally used for the final mutation.
        # ``update_idletasks()`` may drain nested-tab refit idles first, but it
        # will not run this timer ahead of them.
        self.root.after(0, self._apply_initial_iso_fit)

    def _apply_initial_iso_fit(self) -> None:
        if self._initial_fit_complete:
            return
        self._ignore_initial_tab_changed = False
        self.iso_tab.fit_toplevel_to_current_content_once()
        self._initial_fit_complete = True
        if self._run_requested:
            self._show_window()

    def _on_tab_changed(self, event: tk.Event) -> None:
        if self._ignore_initial_tab_changed:
            return
        notebook = event.widget
        selected_tab = notebook.nametowidget(notebook.select())
        if hasattr(selected_tab, "preferred_initial_size"):
            self._set_notebook_content_size(
                selected_tab.preferred_initial_size()
            )
        if hasattr(selected_tab, "fit_toplevel_to_current_content_once"):
            selected_tab.fit_toplevel_to_current_content_once()
        on_parent_tab_selected = getattr(
            selected_tab,
            "on_parent_tab_selected",
            None,
        )
        if callable(on_parent_tab_selected):
            on_parent_tab_selected()

    def _set_notebook_content_size(self, size: tuple[int, int]) -> None:
        width, height = size
        self.notebook.configure(
            width=max(1, width),
            height=max(1, height),
        )

    def _configure_top_notebook_style(self) -> None:
        style = ttk.Style(self.root)
        style.map(
            "CalculatorTop.TNotebook.Tab",
            foreground=[("selected", TOP_NOTEBOOK_SELECTED_FG)],
        )

    def run(self) -> None:
        self._run_requested = True
        if self._initial_fit_complete:
            self._show_window()
        self.root.mainloop()

    def _show_window(self) -> None:
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()


def main() -> None:
    CalculatorTkApp().run()


if __name__ == "__main__":
    main()
