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


_SECTION_FACTORIES = {
    "CSPF": IsoCspfSection,
    "HSPF": IsoHspfSection,
}


class Iso16358Tab(ttk.Frame):
    """ISO 16358 tab — top-level region selector + metric section stack.

    For the MVP only Hong Kong is wired. Selecting Hong Kong renders
    both CSPF and HSPF sections in the same screen.
    """

    def __init__(self, parent: tk.Widget) -> None:
        super().__init__(parent)

        region_row = ttk.Frame(self)
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

        self._sections_holder = ttk.Frame(self)
        self._sections_holder.pack(side=tk.TOP, fill=tk.X, padx=4, pady=4)

        self.sections = {}
        # Compatibility alias for callers that only check panel availability.
        # The actual visible panels are owned and rendered by each section.
        self.result_panel = None

        self._render_region(initial_label)

    def _on_region_changed(self, _event=None) -> None:
        self._render_region(self._region_combo.get())

    def _render_region(self, region_label: str) -> None:
        for child in self._sections_holder.winfo_children():
            child.destroy()
        self.sections = {}
        self.result_panel = None

        for metric in supported_metrics_for(region_label):
            factory = _SECTION_FACTORIES.get(metric)
            if factory is None:
                continue
            section = factory(self._sections_holder, region_label)
            section.pack(side=tk.TOP, fill=tk.X, padx=4, pady=4)
            self.sections[metric] = section
            if self.result_panel is None:
                self.result_panel = section.result_panel
