"""ISO 16358 standard tab — region selector + metric sections.

Composition only. Region/metric → profile_id is delegated to
``ui_tk.profile_resolver``; each metric section owns the result shown
immediately below its inputs.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from ui_tk.profile_resolver import (
    MODE_HONG_KONG,
    MODE_ISO_ISEER_2POINT,
    MODE_SASO_T3,
    calculation_mode_labels,
    region_labels,
    supported_metrics_for,
)
from ui_tk.sections.iso_cspf_section import IsoCspfSection
from ui_tk.sections.iso_hspf_section import IsoHspfSection
from ui_tk.sections.iso_iseer_2point_section import IsoIseer2PointSection
from ui_tk.sections.iso_saso_t3_section import IsoSasoT3Section
from ui_tk.layout_constants import (
    APP_WINDOW_CONTENT_SAFETY_MARGIN_RATIO,
    APP_WINDOW_MIN_VISIBLE_HEIGHT,
    APP_WINDOW_MIN_VISIBLE_WIDTH,
)
from ui_tk.scrollable_frame import ScrollableFrame
from ui_tk.window_geometry import (
    fit_window_to_preferred_content,
    grow_window_by_vertical_delta,
)


_SECTION_FACTORIES = {
    "CSPF": IsoCspfSection,
    "HSPF": IsoHspfSection,
}


def mousewheel_units(event) -> int:
    from ui_tk.scrollable_frame import mousewheel_units as _impl
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

        self.sections = {}
        # Compatibility alias for callers that only check panel availability.
        # The actual visible panels are owned and rendered by each section.
        self.result_panel = None

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
        return self._scrollable.vertical_overflow_delta()

    def preferred_initial_size(self) -> tuple[int, int]:
        self.update_idletasks()

        # Measure every metric tab so hidden tabs are not undersized.
        max_tab_width = 0
        max_tab_height = 0
        if self._current_mode() == MODE_HONG_KONG:
            original_tab = self._metric_notebook.select()
            for tab_id in self._metric_notebook.tabs():
                self._metric_notebook.select(tab_id)
                self.update_idletasks()
                widget = self._metric_notebook.nametowidget(tab_id)
                max_tab_width = max(max_tab_width, widget.winfo_reqwidth())
                max_tab_height = max(max_tab_height, widget.winfo_reqheight())
            if original_tab:
                self._metric_notebook.select(original_tab)
                self.update_idletasks()

        # Base content size on the natural size of the outer frame,
        # but ensure the largest metric tab is accounted for.
        content_width = max(
            self._content.winfo_reqwidth(),
            max_tab_width,
        )
        content_height = self._content.winfo_reqheight()
        if self._current_mode() == MODE_HONG_KONG and self._metric_notebook.tabs():
            current_tab_widget = self._metric_notebook.nametowidget(
                self._metric_notebook.select()
            )
            content_height = (
                content_height
                - current_tab_widget.winfo_reqheight()
                + max_tab_height
            )

        # Apply content-based safety margin.
        margin = APP_WINDOW_CONTENT_SAFETY_MARGIN_RATIO
        return (
            int(content_width * (1 + margin)) + self._scrollbar.winfo_reqwidth(),
            int(content_height * (1 + margin)),
        )

    # -- Calculation mode handling -------------------------------------------

    def _current_mode(self) -> str:
        return self._mode_combo.get() or MODE_ISO_ISEER_2POINT

    def _on_mode_changed(self, _event=None) -> None:
        self._render_mode(self._current_mode())
        self.after_idle(self._fit_toplevel_to_current_content)

    def _fit_toplevel_to_current_content(self) -> None:
        root = self.winfo_toplevel()
        self.update_idletasks()
        fit_window_to_preferred_content(root, self.preferred_initial_size())
        self.update_idletasks()
        grow_window_by_vertical_delta(root, self.vertical_overflow_delta())
        self.update_idletasks()
        self._scrollable.reset_scroll_position()

    def _on_trace_visibility_changed(self) -> None:
        self.after_idle(self._fit_toplevel_to_current_content)

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
            return

        self._render_region(self._region_combo.get())
        self._hong_kong_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def _cancel_hong_kong_pending(self) -> None:
        for section in self.sections.values():
            auto_calc = getattr(section, "_auto_calc", None)
            if auto_calc is not None:
                auto_calc.cancel()

    # -- Region handling ------------------------------------------------------

    def _on_region_changed(self, _event=None) -> None:
        self._render_region(self._region_combo.get())

    def _render_region(self, region_label: str) -> None:
        for tab_id in self._metric_notebook.tabs():
            widget = self._metric_notebook.nametowidget(tab_id)
            self._metric_notebook.forget(tab_id)
            widget.destroy()
        self.sections = {}
        self.result_panel = None

        for metric in supported_metrics_for(region_label):
            factory = _SECTION_FACTORIES.get(metric)
            if factory is None:
                continue
            section = factory(self._metric_notebook, region_label)
            self._metric_notebook.add(section._frame, text=metric)
            self.sections[metric] = section
            if self.result_panel is None:
                self.result_panel = section.result_panel
