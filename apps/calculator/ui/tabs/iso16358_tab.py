"""ISO 16358 standard tab — region selector + metric sections.

Composition only. Region/metric → profile_id is delegated to
``apps.calculator.ui.profile_resolver``; each metric section owns the result shown
immediately below its inputs.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from apps.calculator.ui.lifecycle import ProfileVisibleContentLifecycleController
from apps.calculator.ui.profile_resolver import (
    MODE_HONG_KONG,
    MODE_ISO_ISEER_2POINT,
    MODE_SASO_T3,
    calculation_mode_labels,
    region_labels,
    supported_metrics_for,
)
from apps.calculator.ui.sections.hong_kong_cspf_section import HongKongCspfSection
from apps.calculator.ui.sections.hong_kong_hspf_section import HongKongHspfSection
from apps.calculator.ui.sections.iso_iseer_2point_section import IsoIseer2PointSection
from apps.calculator.ui.sections.iso_saso_t3_section import IsoSasoT3Section
from apps.calculator.ui.scrollable_frame import ScrollableFrame


_SECTION_FACTORIES = {
    "CSPF": HongKongCspfSection,
    "HSPF": HongKongHspfSection,
}


def mousewheel_units(event) -> int:
    from apps.calculator.ui.scrollable_frame import mousewheel_units as _impl
    return _impl(event)


class Iso16358Tab(ttk.Frame):
    """ISO 16358 tab with profile selector and metric/profile sections.

    ISO / ISEER 2-point is the default profile. Hong Kong keeps the
    CSPF/HSPF metric sub-tabs without exposing a duplicate region selector.
    """

    def __init__(self, parent: tk.Widget) -> None:
        super().__init__(parent)

        self._scrollable = ScrollableFrame(self)
        self._scrollable.pack(fill=tk.BOTH, expand=True)
        self._content = self._scrollable.content

        mode_row = ttk.Frame(self._content)
        mode_row.pack(side=tk.TOP, anchor="w", padx=4, pady=4)
        ttk.Label(mode_row, text="ISO 프로파일").pack(side=tk.LEFT, padx=(0, 4))
        self._mode_combo = ttk.Combobox(
            mode_row,
            values=list(calculation_mode_labels()),
            state="readonly",
            width=24,
        )
        self._mode_combo.set(MODE_ISO_ISEER_2POINT)
        self._mode_combo.pack(side=tk.LEFT)
        self._mode_combo.bind("<<ComboboxSelected>>", self._on_mode_changed)

        self._hong_kong_frame = ttk.Frame(self._content)
        self._two_point_frame = ttk.Frame(self._content)
        self._saso_t3_frame = ttk.Frame(self._content)
        self._two_point_section = None
        self._saso_t3_section = None

        self._region_row = ttk.Frame(self._hong_kong_frame)
        self._region_label = ttk.Label(self._region_row, text="지역")
        self._region_label.pack(side=tk.LEFT, padx=(0, 4))
        self._region_combo = ttk.Combobox(
            self._region_row,
            values=list(region_labels()),
            state="readonly",
            width=20,
        )
        initial_label = region_labels()[0]
        self._region_combo.set(initial_label)
        self._region_combo.pack(side=tk.LEFT)
        self._region_combo.bind("<<ComboboxSelected>>", self._on_region_changed)

        self._metric_notebook = ttk.Notebook(self._hong_kong_frame)
        self._metric_notebook.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=4, pady=4)
        self._metric_notebook.bind(
            "<<NotebookTabChanged>>", self._on_metric_tab_changed
        )
        self._lifecycle = ProfileVisibleContentLifecycleController(
            owner=self,
            content=self._content,
            scrollable=self._scrollable,
            nested_notebook=self._metric_notebook,
            nested_notebook_active=lambda: self._current_mode() == MODE_HONG_KONG,
        )
        self._measurement = self._lifecycle.measurement
        self._refit_scheduler = self._lifecycle.scheduler

        self.sections = {}
        # Compatibility alias for callers that only check panel availability.
        # The actual visible panels are owned and rendered by each section.
        self.result_panel = None
        self._rendered_mode_label: str | None = None
        self._rendered_hong_kong_region_label: str | None = None
        self._hong_kong_sections = {}
        self._hong_kong_result_panel = None

        self._render_mode(MODE_ISO_ISEER_2POINT)

    # -- ScrollableFrame compatibility aliases --------------------------------

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

    # -- Metric size helpers --------------------------------------------------

    def vertical_overflow_delta(self) -> int:
        return self._lifecycle.vertical_overflow_delta()

    def preferred_initial_size(self) -> tuple[int, int]:
        return self._lifecycle.preferred_initial_size()

    # -- Calculation mode handling -------------------------------------------

    def _current_mode(self) -> str:
        return self._mode_combo.get() or MODE_ISO_ISEER_2POINT

    def _on_mode_changed(self, _event=None) -> None:
        mode_label = self._current_mode()
        same_mode = mode_label == self._rendered_mode_label
        if not same_mode:
            self._render_mode(mode_label)
        self._request_visible_lifecycle_refit(
            settle_cycles=2 if mode_label == MODE_HONG_KONG and not same_mode else 1
        )

    def _request_visible_lifecycle_refit(self, *, settle_cycles: int = 1) -> None:
        """Run visible-surface settle -> snapshot measure -> shell fit later."""

        self._lifecycle.request_visible_lifecycle_refit(settle_cycles=settle_cycles)

    def _schedule_toplevel_refit(self, *, settle_cycles: int = 1) -> None:
        self._request_visible_lifecycle_refit(settle_cycles=settle_cycles)

    def fit_toplevel_to_current_content_once(self) -> None:
        self._lifecycle.fit_toplevel_to_current_content_once()

    def _on_trace_visibility_changed(self) -> None:
        self._lifecycle.on_detail_visibility_changed()

    def _on_metric_tab_changed(self, _event=None) -> None:
        self._lifecycle.on_nested_tab_changed()

    def _render_mode(self, mode_label: str) -> None:
        self._cancel_hong_kong_pending()
        self._hong_kong_frame.pack_forget()
        self._two_point_frame.pack_forget()
        self._saso_t3_frame.pack_forget()
        if self._two_point_section is not None:
            self._two_point_section.cancel_pending()
        if self._saso_t3_section is not None:
            self._saso_t3_section.cancel_pending()
        if mode_label not in (MODE_ISO_ISEER_2POINT, MODE_HONG_KONG, MODE_SASO_T3):
            mode_label = MODE_ISO_ISEER_2POINT
            self._mode_combo.set(mode_label)

        if mode_label == MODE_ISO_ISEER_2POINT:
            self.sections = {}
            if self._two_point_section is None:
                self._two_point_section = IsoIseer2PointSection(
                    self._two_point_frame,
                    on_trace_visibility_changed=self._on_trace_visibility_changed,
                )
                self._two_point_section.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
            self.result_panel = self._two_point_section.result_panel
            self._two_point_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
            self._rendered_mode_label = mode_label
            return

        if mode_label == MODE_SASO_T3:
            self.sections = {}
            if self._saso_t3_section is None:
                self._saso_t3_section = IsoSasoT3Section(
                    self._saso_t3_frame,
                    on_trace_visibility_changed=self._on_trace_visibility_changed,
                )
                self._saso_t3_section.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
            self.result_panel = self._saso_t3_section.result_panel
            self._saso_t3_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
            self._rendered_mode_label = mode_label
            return

        region_label = self._region_combo.get()
        if self._can_reuse_hong_kong_region(region_label):
            self.sections = self._hong_kong_sections
            self.result_panel = self._hong_kong_result_panel
        else:
            self._render_region(region_label)
        self._hong_kong_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self._rendered_mode_label = mode_label

    def _cancel_hong_kong_pending(self) -> None:
        for section in self._hong_kong_sections.values():
            auto_calc = getattr(section, "_auto_calc", None)
            if auto_calc is not None:
                auto_calc.cancel()

    # -- Region handling ------------------------------------------------------

    def _on_region_changed(self, _event=None) -> None:
        self._render_region(self._region_combo.get())
        self._request_visible_lifecycle_refit()

    def _can_reuse_hong_kong_region(self, region_label: str) -> bool:
        return (
            self._rendered_hong_kong_region_label == region_label
            and bool(self._hong_kong_sections)
            and bool(self._metric_notebook.tabs())
        )

    def _render_region(self, region_label: str) -> None:
        for tab_id in self._metric_notebook.tabs():
            widget = self._metric_notebook.nametowidget(tab_id)
            self._metric_notebook.forget(tab_id)
            widget.destroy()
        self.sections = {}
        self.result_panel = None
        self._hong_kong_sections = {}
        self._hong_kong_result_panel = None

        for metric in supported_metrics_for(region_label):
            factory = _SECTION_FACTORIES.get(metric)
            if factory is None:
                continue
            if factory in (HongKongCspfSection, HongKongHspfSection):
                section = factory(
                    self._metric_notebook,
                    region_label,
                    on_trace_visibility_changed=self._on_trace_visibility_changed,
                )
            else:
                section = factory(self._metric_notebook, region_label)
            self._metric_notebook.add(section._frame, text=metric)
            self.sections[metric] = section
            if self.result_panel is None:
                self.result_panel = section.result_panel
        self._hong_kong_sections = self.sections
        self._hong_kong_result_panel = self.result_panel
        self._rendered_hong_kong_region_label = region_label
