"""EN14825 standard tab containing the SEER calculation section."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from apps.calculator.ui.sections.en14825_seer_section import En14825SeerSection
from apps.calculator.ui.scrollable_frame import ScrollableFrame
from apps.calculator.ui.window_measurement import TkVisibleContentMeasurement
from apps.calculator.ui.window_refit import DynamicContentRefitScheduler
from apps.calculator.ui.window_shell import TkContentHuggingShell


class En14825Tab(ttk.Frame):
    """Tab container for the EN14825 SEER calculator UI."""

    def __init__(self, parent: tk.Widget) -> None:
        super().__init__(parent)

        self._scrollable = ScrollableFrame(self)
        self._scrollable.pack(fill=tk.BOTH, expand=True)
        self._content = self._scrollable.content

        # Composes the SEER section
        self.seer_section = En14825SeerSection(self._content)
        self.seer_section.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        # Alias for result panel validation compatibility
        self.result_panel = self.seer_section.result_panel

        self._refit_scheduler = DynamicContentRefitScheduler(
            self,
            self._fit_toplevel_to_current_content,
        )

        self._measurement = TkVisibleContentMeasurement(
            content=self._content,
            scrollbar=self._scrollbar,
            overflow_source=self._scrollable,
            nested_notebook=None,
            nested_notebook_active=lambda: False,
            suppress_measurement=self._refit_scheduler.suppress_requests,
        )
        self._content_shell = TkContentHuggingShell(self.winfo_toplevel())
        self._content_form = self._content_shell.register_content(
            snapshot_provider=self._measurement.snapshot,
            after_fit=lambda _result: self._scrollable.reset_scroll_position(),
        )

    @property
    def _canvas(self) -> tk.Canvas:
        return self._scrollable.canvas

    @property
    def _scrollbar(self) -> ttk.Scrollbar:
        return self._scrollable.scrollbar

    @property
    def _scrollbar_visible(self) -> bool:
        return self._scrollable.scrollbar_visible

    def _contains_widget(self, widget) -> bool:
        return self._scrollable._contains_widget(widget)

    def _on_mousewheel(self, event) -> str:
        return self._scrollable._on_mousewheel(event)

    def vertical_overflow_delta(self) -> int:
        return self._measurement.vertical_overflow_delta()

    def preferred_initial_size(self) -> tuple[int, int]:
        return self._measurement.preferred_size()

    def _fit_toplevel_to_current_content(self) -> None:
        self.update_idletasks()
        self._content_form.fit()
        self.update_idletasks()

    def fit_toplevel_to_current_content_once(self) -> None:
        self._fit_toplevel_to_current_content()
