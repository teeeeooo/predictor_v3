"""AHRI 210/240 tab containing SEER2 and HSPF2 metric surfaces."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from apps.calculator.ui.scrollable_frame import ScrollableFrame
from apps.calculator.ui.sections.ahri_seer2_section import AhriSeer2Section
from apps.calculator.ui.sections.ahri_hspf2_section import AhriHspf2Section
from apps.calculator.ui.window_measurement import TkVisibleContentMeasurement
from apps.calculator.ui.window_refit import DynamicContentRefitScheduler
from apps.calculator.ui.window_shell import TkContentHuggingShell


class Ahri210240Tab(ttk.Frame):
    """Top-level AHRI metric navigation."""

    def __init__(self, parent: tk.Widget) -> None:
        super().__init__(parent)
        self._scrollable = ScrollableFrame(self)
        self._scrollable.pack(fill=tk.BOTH, expand=True)
        self._content = self._scrollable.content
        self._refit_scheduler = DynamicContentRefitScheduler(
            self,
            self._fit_toplevel_to_current_content,
        )

        self.metric_notebook = ttk.Notebook(self._content)
        self.metric_notebook.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        self.metric_notebook.bind("<<NotebookTabChanged>>", self._on_metric_changed)
        self.seer2_frame = ttk.Frame(self.metric_notebook)
        self.hspf2_frame = ttk.Frame(self.metric_notebook)
        self.metric_notebook.add(self.seer2_frame, text="SEER2")
        self.metric_notebook.add(self.hspf2_frame, text="HSPF2")
        self.seer2_section = AhriSeer2Section(self.seer2_frame)
        self.seer2_section.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        self.hspf2_section = AhriHspf2Section(self.hspf2_frame)
        self.hspf2_section.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        self.result_panel = self.seer2_section.result_panel

        self._measurement = TkVisibleContentMeasurement(
            content=self._content,
            scrollbar=self._scrollable.scrollbar,
            overflow_source=self._scrollable,
            nested_notebook=self.metric_notebook,
            nested_notebook_active=lambda: True,
            suppress_measurement=self._refit_scheduler.suppress_requests,
        )
        shell = TkContentHuggingShell(self.winfo_toplevel())
        self._content_form = shell.register_content(
            snapshot_provider=self._measurement.snapshot,
            after_fit=lambda _result: self._scrollable.reset_scroll_position(),
        )

    def preferred_initial_size(self) -> tuple[int, int]:
        return self._measurement.preferred_size()

    def fit_toplevel_to_current_content_once(self) -> None:
        self._fit_toplevel_to_current_content()

    def _fit_toplevel_to_current_content(self) -> None:
        self.update_idletasks()
        self._content_form.fit()
        self.update_idletasks()

    def _on_metric_changed(self, _event: tk.Event | None = None) -> None:
        self._refit_scheduler.request_refit()
