"""AHRI 210/240 tab containing SEER2 and HSPF2 metric surfaces."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from apps.calculator.ui.lifecycle import ProfileVisibleContentLifecycleController
from apps.calculator.ui.scrollable_frame import ScrollableFrame
from apps.calculator.ui.sections.ahri_seer2_section import AhriSeer2Section
from apps.calculator.ui.sections.ahri_hspf2_section import AhriHspf2Section


class Ahri210240Tab(ttk.Frame):
    """Top-level AHRI metric navigation."""

    def __init__(self, parent: tk.Widget) -> None:
        super().__init__(parent)
        self._scrollable = ScrollableFrame(self)
        self._scrollable.pack(fill=tk.BOTH, expand=True)
        self._content = self._scrollable.content

        self.metric_notebook = ttk.Notebook(self._content)
        self.metric_notebook.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        self.metric_notebook.bind("<<NotebookTabChanged>>", self._on_metric_changed)
        self.seer2_frame = ttk.Frame(self.metric_notebook)
        self.hspf2_frame = ttk.Frame(self.metric_notebook)
        self.metric_notebook.add(self.seer2_frame, text="SEER2")
        self.metric_notebook.add(self.hspf2_frame, text="HSPF2")
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
        self.seer2_section = AhriSeer2Section(self.seer2_frame)
        self.seer2_section.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        self.hspf2_section = AhriHspf2Section(
            self.hspf2_frame,
            on_trace_visibility_changed=self._lifecycle.on_detail_visibility_changed,
        )
        self.hspf2_section.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        self.result_panel = self.seer2_section.result_panel

    def preferred_initial_size(self) -> tuple[int, int]:
        return self._lifecycle.preferred_initial_size()

    def fit_toplevel_to_current_content_once(self) -> None:
        self._lifecycle.fit_toplevel_to_current_content_once()

    def _on_metric_changed(self, _event: tk.Event | None = None) -> None:
        if self._is_visible_surface():
            self._lifecycle.on_nested_tab_changed()

    def _request_visible_lifecycle_refit(self, *, settle_cycles: int = 1) -> None:
        """Fit only after the selected AHRI metric surface has settled."""

        self._lifecycle.request_visible_lifecycle_refit(settle_cycles=settle_cycles)

    def _is_visible_surface(self) -> bool:
        parent = self.master
        if isinstance(parent, ttk.Notebook):
            return self in tuple(parent.nametowidget(tab) for tab in parent.tabs()) and (
                parent.select() == str(self)
            )
        return bool(self.winfo_ismapped())
