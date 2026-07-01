"""KOREA tab containing KS C 9306 CSPF and HSPF metric surfaces."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from apps.calculator.ui.lifecycle import ProfileVisibleContentLifecycleController
from apps.calculator.ui.scrollable_frame import ScrollableFrame


class KoreaTab(ttk.Frame):
    """Top-level KOREA metric navigation skeleton."""

    def __init__(self, parent: tk.Widget) -> None:
        super().__init__(parent)
        self._scrollable = ScrollableFrame(self)
        self._scrollable.pack(fill=tk.BOTH, expand=True)
        self._content = self._scrollable.content

        self.metric_notebook = ttk.Notebook(self._content)
        self.metric_notebook.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        self.metric_notebook.bind("<<NotebookTabChanged>>", self._on_metric_changed)
        self.cspf_frame = ttk.Frame(self.metric_notebook)
        self.hspf_frame = ttk.Frame(self.metric_notebook)
        self.metric_notebook.add(self.cspf_frame, text="CSPF")
        self.metric_notebook.add(self.hspf_frame, text="HSPF")

        self._lifecycle = ProfileVisibleContentLifecycleController(
            owner=self,
            content=self._content,
            scrollable=self._scrollable,
            nested_notebook=self.metric_notebook,
            nested_notebook_active=self._is_visible_surface,
            nested_tab_settle_cycles=2,
        )
        self._measurement = self._lifecycle.measurement
        self._refit_scheduler = self._lifecycle.scheduler

    def preferred_initial_size(self) -> tuple[int, int]:
        return self._lifecycle.preferred_initial_size()

    def fit_toplevel_to_current_content_once(self) -> None:
        self._lifecycle.fit_toplevel_to_current_content_once()

    def on_parent_tab_selected(self) -> None:
        self._lifecycle.on_parent_tab_selected()

    def _on_metric_changed(self, _event: tk.Event | None = None) -> None:
        if self._is_visible_surface():
            self._lifecycle.on_nested_tab_changed()

    def _is_visible_surface(self) -> bool:
        parent = self.master
        if isinstance(parent, ttk.Notebook):
            return self in tuple(parent.nametowidget(tab) for tab in parent.tabs()) and (
                parent.select() == str(self)
            )
        return bool(self.winfo_ismapped())
