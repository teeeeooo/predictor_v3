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
    APP_WINDOW_MIN_VISIBLE_HEIGHT,
    APP_WINDOW_MIN_VISIBLE_WIDTH,
)


_SECTION_FACTORIES = {
    "CSPF": IsoCspfSection,
    "HSPF": IsoHspfSection,
}


def mousewheel_units(event) -> int:
    if getattr(event, "num", None) == 4:
        return -1
    if getattr(event, "num", None) == 5:
        return 1
    delta = getattr(event, "delta", 0)
    if delta > 0:
        return -1
    if delta < 0:
        return 1
    return 0


class Iso16358Tab(ttk.Frame):
    """ISO 16358 tab — top-level region selector + metric section stack.

    For the MVP only Hong Kong is wired. Selecting Hong Kong renders
    both CSPF and HSPF sections in the same screen.
    """

    def __init__(self, parent: tk.Widget) -> None:
        super().__init__(parent)

        self._canvas = tk.Canvas(self, highlightthickness=0, borderwidth=0)
        self._scrollbar = ttk.Scrollbar(
            self, orient=tk.VERTICAL, command=self._canvas.yview
        )
        self._canvas.configure(yscrollcommand=self._scrollbar.set)
        self._scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self._canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._content = ttk.Frame(self._canvas)
        self._content_window = self._canvas.create_window(
            (0, 0), window=self._content, anchor="nw"
        )
        self._content.bind("<Configure>", self._on_content_configured)
        self._canvas.bind("<Configure>", self._on_canvas_configured)
        self.bind("<Configure>", self._sync_content_width)
        self.winfo_toplevel().bind("<Configure>", self._sync_content_width, add="+")
        self.bind_all("<MouseWheel>", self._on_mousewheel, add="+")
        self.bind_all("<Button-4>", self._on_mousewheel, add="+")
        self.bind_all("<Button-5>", self._on_mousewheel, add="+")
        self.bind("<Destroy>", self._unbind_mousewheel, add="+")

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

    def _on_content_configured(self, _event=None) -> None:
        self._canvas.configure(scrollregion=self._canvas.bbox("all"))

    def preferred_initial_size(self) -> tuple[int, int]:
        width = max(
            (child.winfo_reqwidth() for child in self._content.winfo_children()),
            default=APP_WINDOW_MIN_VISIBLE_WIDTH,
        )
        height = sum(child.winfo_reqheight() for child in self._content.winfo_children())
        return (
            width + self._scrollbar.winfo_reqwidth(),
            max(APP_WINDOW_MIN_VISIBLE_HEIGHT, height),
        )

    def _on_canvas_configured(self, event) -> None:
        self._canvas.itemconfigure(self._content_window, width=event.width)

    def _sync_content_width(self, _event=None) -> None:
        width = self._canvas.winfo_width()
        if _event is not None and getattr(_event, "width", 0) > width:
            width = _event.width - self._scrollbar.winfo_reqwidth()
        width = max(1, width)
        self._canvas.itemconfigure(self._content_window, width=width)
        if int(self._content.cget("width") or 0) != width:
            self._content.configure(width=width)

    def _unbind_mousewheel(self, _event=None) -> None:
        self.unbind_all("<MouseWheel>")
        self.unbind_all("<Button-4>")
        self.unbind_all("<Button-5>")

    def _contains_widget(self, widget) -> bool:
        while widget is not None:
            if widget is self:
                return True
            widget = getattr(widget, "master", None)
        return False

    def _on_mousewheel(self, event) -> str:
        if not self._contains_widget(getattr(event, "widget", None)):
            return ""
        units = mousewheel_units(event)
        if units:
            self._canvas.yview_scroll(units, "units")
        return "break"

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
