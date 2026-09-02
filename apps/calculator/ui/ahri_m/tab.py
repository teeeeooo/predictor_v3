"""Top-level AHRI 210/240 Appendix M calculator tab."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from apps.calculator.ui.lifecycle import ProfileVisibleContentLifecycleController
from apps.calculator.ui.scrollable_frame import ScrollableFrame
from .seer_section import AhriMSeerSection
from .hspf_section import AhriMHspfSection


class Ahri210240MTab(ttk.Frame):
    def __init__(self, parent: tk.Widget) -> None:
        super().__init__(parent)
        self._scrollable = ScrollableFrame(self)
        self._scrollable.pack(fill=tk.BOTH, expand=True)
        self._content = self._scrollable.content
        self.metric_notebook = ttk.Notebook(self._content)
        self.metric_notebook.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        self.metric_notebook.bind("<<NotebookTabChanged>>", self._on_metric_changed)
        self.seer_frame = ttk.Frame(self.metric_notebook)
        self.hspf_frame = ttk.Frame(self.metric_notebook)
        self.metric_notebook.add(self.seer_frame, text="SEER")
        self.metric_notebook.add(self.hspf_frame, text="HSPF")
        self._lifecycle = ProfileVisibleContentLifecycleController(
            owner=self, content=self._content, scrollable=self._scrollable,
            nested_notebook=self.metric_notebook, nested_notebook_active=self._is_visible_surface,
            nested_tab_settle_cycles=2,
        )
        self.seer_section = AhriMSeerSection(self.seer_frame, on_trace_visibility_changed=self._lifecycle.on_detail_visibility_changed)
        self.seer_section.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        self.hspf_section = AhriMHspfSection(self.hspf_frame, on_trace_visibility_changed=self._lifecycle.on_detail_visibility_changed)
        self.hspf_section.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        self.result_panel = self.seer_section.result_panel

    def preferred_initial_size(self) -> tuple[int, int]:
        return self._lifecycle.preferred_initial_size()

    def fit_toplevel_to_current_content_once(self) -> None:
        self._lifecycle.fit_toplevel_to_current_content_once()

    def _on_metric_changed(self, _event=None) -> None:
        if self._is_visible_surface():
            self._lifecycle.on_nested_tab_changed()

    def _is_visible_surface(self) -> bool:
        parent = self.master
        if parent.winfo_class() == "TNotebook":
            return self in tuple(parent.nametowidget(tab) for tab in parent.tabs()) and parent.select() == str(self)
        return bool(self.winfo_ismapped())
