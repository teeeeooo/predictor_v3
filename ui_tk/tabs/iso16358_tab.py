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
        self._canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._scrollbar_visible = False
        self._update_scrollbar_visibility()

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

    def _update_scrollbar_visibility(self, _event=None) -> None:
        """Show scrollbar only when content exceeds canvas viewport."""
        bbox = self._canvas.bbox("all")
        if bbox is None:
            content_height = 0
        else:
            content_height = bbox[3] - bbox[1]
        canvas_height = self._canvas.winfo_height()
        needed = content_height > canvas_height
        if needed and not self._scrollbar_visible:
            self._scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            self._scrollbar_visible = True
            self._sync_content_width()
        elif not needed and self._scrollbar_visible:
            self._scrollbar.pack_forget()
            self._scrollbar_visible = False
            self._sync_content_width()

    def vertical_overflow_delta(self) -> int:
        """Return measured vertical overflow in pixels, or 0 if none."""
        bbox = self._canvas.bbox("all")
        if bbox is None:
            return 0
        content_height = bbox[3] - bbox[1]
        canvas_height = self._canvas.winfo_height()
        return max(0, content_height - canvas_height)

    def _on_content_configured(self, _event=None) -> None:
        self._canvas.configure(scrollregion=self._canvas.bbox("all"))
        self._update_scrollbar_visibility()

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
