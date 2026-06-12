"""EN14825 standard tab containing SEER and SCOP calculation sections."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from apps.calculator.ui.sections.en14825_seer_section import En14825SeerSection
from apps.calculator.ui.sections.en14825_scop_section import En14825ScopSection
from apps.calculator.ui.scrollable_frame import ScrollableFrame
from apps.calculator.ui.window_measurement import TkVisibleContentMeasurement
from apps.calculator.ui.window_refit import DynamicContentRefitScheduler
from apps.calculator.ui.window_shell import TkContentHuggingShell


class En14825Tab(ttk.Frame):
    """Tab container for EN14825 SEER and SCOP calculator UI."""

    def __init__(self, parent: tk.Widget) -> None:
        super().__init__(parent)

        self._scrollable = ScrollableFrame(self)
        self._scrollable.pack(fill=tk.BOTH, expand=True)
        self._content = self._scrollable.content

        self._refit_scheduler = DynamicContentRefitScheduler(
            self,
            self._fit_toplevel_to_current_content,
        )

        self._p_to_var = tk.StringVar(value="0")
        self._p_sb_var = tk.StringVar(value="0")
        self._p_ck_var = tk.StringVar(value="0")
        self._p_off_var = tk.StringVar(value="0")
        self._appliance_type_var = tk.StringVar(value="reversible")

        self._standard_notebook = ttk.Notebook(self._content)
        self._standard_notebook.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        self._standard_notebook.bind(
            "<<NotebookTabChanged>>", self._on_standard_tab_changed
        )

        self._seer_frame = ttk.Frame(self._standard_notebook)
        self._scop_frame = ttk.Frame(self._standard_notebook)
        self._standard_notebook.add(self._seer_frame, text="SEER")
        self._standard_notebook.add(self._scop_frame, text="SCOP")

        self._create_common_input_panel(self._seer_frame)
        self.seer_section = En14825SeerSection(
            self._seer_frame,
            common_input_values=self._common_input_values,
        )
        self.seer_section.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        self._create_common_input_panel(self._scop_frame)
        self.scop_section = En14825ScopSection(
            self._scop_frame,
            on_trace_visibility_changed=self._request_visible_lifecycle_refit,
            common_input_values=self._common_input_values,
        )
        self.scop_section.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        for var in (
            self._p_to_var,
            self._p_sb_var,
            self._p_ck_var,
            self._p_off_var,
            self._appliance_type_var,
        ):
            var.trace_add("write", lambda *args: self._on_common_input_changed())

        # Alias for result panel validation compatibility.
        self.result_panel = self.seer_section.result_panel

        self._measurement = TkVisibleContentMeasurement(
            content=self._content,
            scrollbar=self._scrollbar,
            overflow_source=self._scrollable,
            nested_notebook=self._standard_notebook,
            nested_notebook_active=lambda: True,
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

    def _request_visible_lifecycle_refit(self, *, settle_cycles: int = 1) -> None:
        self._refit_scheduler.request_refit(settle_cycles=settle_cycles)

    def _on_standard_tab_changed(self, _event=None) -> None:
        self._request_visible_lifecycle_refit()

    def _common_input_values(self) -> dict[str, str]:
        return {
            "p_to": self._p_to_var.get(),
            "p_sb": self._p_sb_var.get(),
            "p_ck": self._p_ck_var.get(),
            "p_off": self._p_off_var.get(),
            "appliance_type": self._appliance_type_var.get(),
        }

    def _on_common_input_changed(self) -> None:
        self.seer_section.schedule_recalculate()
        self.scop_section.schedule_recalculate()

    def _create_common_input_panel(self, parent: tk.Widget) -> ttk.LabelFrame:
        common_frame = ttk.LabelFrame(parent, text="공통 입력")
        common_frame.pack(fill=tk.X, padx=4, pady=(4, 0))
        ttk.Label(common_frame, text="Pto [W]").grid(row=0, column=0, sticky="w", padx=(6, 4), pady=6)
        ttk.Entry(common_frame, textvariable=self._p_to_var, width=6).grid(row=0, column=1, sticky="w", padx=(0, 10), pady=6)
        ttk.Label(common_frame, text="Psb [W]").grid(row=0, column=2, sticky="w", padx=(6, 4), pady=6)
        ttk.Entry(common_frame, textvariable=self._p_sb_var, width=6).grid(row=0, column=3, sticky="w", padx=(0, 10), pady=6)
        ttk.Label(common_frame, text="Pck [W]").grid(row=0, column=4, sticky="w", padx=(6, 4), pady=6)
        ttk.Entry(common_frame, textvariable=self._p_ck_var, width=6).grid(row=0, column=5, sticky="w", padx=(0, 10), pady=6)
        ttk.Label(common_frame, text="Poff [W]").grid(row=0, column=6, sticky="w", padx=(6, 4), pady=6)
        ttk.Entry(common_frame, textvariable=self._p_off_var, width=6).grid(row=0, column=7, sticky="w", padx=(0, 10), pady=6)
        ttk.Label(common_frame, text="기기 유형").grid(row=0, column=8, sticky="w", padx=(6, 4), pady=6)
        ttk.Combobox(
            common_frame,
            textvariable=self._appliance_type_var,
            values=("reversible", "heating_only"),
            width=12,
            state="readonly",
        ).grid(row=0, column=9, sticky="w", padx=(0, 6), pady=6)
        return common_frame
