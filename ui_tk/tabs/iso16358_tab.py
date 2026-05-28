"""ISO 16358 standard tab — region selector + metric sections.

Composition only. Region/metric → profile_id is delegated to
``ui_tk.profile_resolver``; each metric section owns the result shown
immediately below its inputs.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from ui_tk.profile_resolver import (
    region_labels,
    supported_metrics_for,
)
from ui_tk.sections.iso_cspf_section import IsoCspfSection
from ui_tk.sections.iso_hspf_section import IsoHspfSection
from ui_tk.layout_constants import (
    APP_WINDOW_CONTENT_SAFETY_MARGIN_RATIO,
    APP_WINDOW_MIN_VISIBLE_HEIGHT,
    APP_WINDOW_MIN_VISIBLE_WIDTH,
)
from ui_tk.scrollable_frame import ScrollableFrame


_SECTION_FACTORIES = {
    "CSPF": IsoCspfSection,
    "HSPF": IsoHspfSection,
}


def mousewheel_units(event) -> int:
    from ui_tk.scrollable_frame import mousewheel_units as _impl
    return _impl(event)


class Iso16358Tab(ttk.Frame):
    """ISO 16358 tab with region selector and metric sub-tabs.

    The top-level selector chooses a supported region such as Hong Kong.
    Each region renders its supported metric sections in sub-tabs, and
    each metric section owns its input and result surfaces.
    """

    def __init__(self, parent: tk.Widget) -> None:
        super().__init__(parent)

        self._scrollable = ScrollableFrame(self)
        self._scrollable.pack(fill=tk.BOTH, expand=True)
        self._content = self._scrollable.content

        region_row = ttk.Frame(self._content)
        region_row.pack(side=tk.TOP, anchor="w", padx=4, pady=4)
        ttk.Label(region_row, text="지역").pack(side=tk.LEFT, padx=(0, 4))
        self._region_combo = ttk.Combobox(
            region_row,
            values=list(region_labels()),
            state="readonly",
            width=20,
        )
        initial_label = region_labels()[0]
        self._region_combo.set(initial_label)
        self._region_combo.pack(side=tk.LEFT)
        self._region_combo.bind("<<ComboboxSelected>>", self._on_region_changed)

        self._metric_notebook = ttk.Notebook(self._content)
        self._metric_notebook.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=4, pady=4)

        self.sections = {}
        # Compatibility alias for callers that only check panel availability.
        # The actual visible panels are owned and rendered by each section.
        self.result_panel = None

        self._render_region(initial_label)

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
        original_tab = self._metric_notebook.select()
        max_tab_width = 0
        max_tab_height = 0
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
        if self._metric_notebook.tabs():
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

    # -- Region handling ------------------------------------------------------

    def _on_region_changed(self, _event=None) -> None:
        self._render_region(self._region_combo.get())

    def _render_region(self, region_label: str) -> None:
        for tab_id in self._metric_notebook.tabs():
            self._metric_notebook.forget(tab_id)
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
