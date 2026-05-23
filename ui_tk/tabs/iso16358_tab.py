"""ISO 16358 standard tab — region selector + metric sections.

Composition only. Region/metric → profile_id is delegated to
``ui_tk.profile_resolver``; result display is delegated to a
``ResultPanel`` owned by the tab.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from ui_tk.profile_resolver import (
    region_labels,
    supported_metrics_for,
)
from ui_tk.result_panel import ResultPanel
from ui_tk.result_models import ResultSummary
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

        self.result_panel = ResultPanel(self)
        self.result_panel.pack(
            side=tk.TOP, fill=tk.BOTH, expand=True, padx=4, pady=4
        )
        self.sections = {}
        self._metric_results: dict[str, ResultSummary] = {}

        self._render_region(initial_label)

    def _on_region_changed(self, _event=None) -> None:
        self._render_region(self._region_combo.get())

    def _render_region(self, region_label: str) -> None:
        for child in self._sections_holder.winfo_children():
            child.destroy()
        self.sections = {}
        self._metric_results = {}
        self.result_panel.clear()

        for metric in supported_metrics_for(region_label):
            factory = _SECTION_FACTORIES.get(metric)
            if factory is None:
                continue
            section = factory(
                self._sections_holder,
                region_label,
                lambda text, metric=metric: self._set_metric_result(metric, text),
            )
            section.pack(side=tk.TOP, fill=tk.X, padx=4, pady=4)
            self.sections[metric] = section

    def _set_metric_result(self, metric: str, summary: ResultSummary) -> None:
        self._metric_results[metric] = summary
        ordered_results = [
            self._metric_results[key]
            for key in supported_metrics_for(self._region_combo.get())
            if key in self._metric_results
        ]
        self.result_panel.set_summaries(ordered_results)
