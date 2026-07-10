"""EN14825 standard tab containing SEER and SCOP calculation sections."""

from __future__ import annotations

from collections.abc import Mapping
import tkinter as tk
from tkinter import ttk

from apps.calculator.ui.metric_input_table import MetricInputTable
from apps.calculator.ui.lifecycle import ProfileVisibleContentLifecycleController
from apps.calculator.ui.sections.en14825_seer_section import En14825SeerSection
from apps.calculator.ui.sections.en14825_scop_section import En14825ScopSection
from apps.calculator.ui.scrollable_frame import ScrollableFrame
from apps.calculator.ui.table.controller import TkTableController


class En14825Tab(ttk.Frame):
    """Tab container for EN14825 SEER and SCOP calculator UI."""

    def __init__(self, parent: tk.Widget) -> None:
        super().__init__(parent)

        self._scrollable = ScrollableFrame(self)
        self._scrollable.pack(fill=tk.BOTH, expand=True)
        self._content = self._scrollable.content

        self._p_to_var = tk.StringVar(master=self, value="0")
        self._p_sb_var = tk.StringVar(master=self, value="0")
        self._p_ck_var = tk.StringVar(master=self, value="0")
        self._p_off_var = tk.StringVar(master=self, value="0")
        self._common_input_tables: list[MetricInputTable] = []
        self._common_input_controllers: list[TkTableController] = []
        self._syncing_common_inputs = False

        self._standard_notebook = ttk.Notebook(self._content)
        self._standard_notebook.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        self._standard_notebook.bind(
            "<<NotebookTabChanged>>", self._on_standard_tab_changed
        )
        self._lifecycle = ProfileVisibleContentLifecycleController(
            owner=self,
            content=self._content,
            scrollable=self._scrollable,
            nested_notebook=self._standard_notebook,
            nested_notebook_active=lambda: True,
            parent_selected_settle_cycles=2,
        )
        # Temporary private compatibility aliases for focused diagnostics.
        self._measurement = self._lifecycle.measurement
        self._refit_scheduler = self._lifecycle.scheduler

        self._seer_frame = ttk.Frame(self._standard_notebook)
        self._scop_frame = ttk.Frame(self._standard_notebook)
        self._standard_notebook.add(self._seer_frame, text="SEER")
        self._standard_notebook.add(self._scop_frame, text="SCOP")

        self._create_common_input_panel(self._seer_frame)
        self.seer_section = En14825SeerSection(
            self._seer_frame,
            on_trace_visibility_changed=self._request_visible_lifecycle_refit,
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
        ):
            var.trace_add("write", lambda *args: self._on_common_numeric_var_changed())

        # Alias for result panel validation compatibility.
        self.result_panel = self.seer_section.result_panel

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
        return self._lifecycle.vertical_overflow_delta()

    def preferred_initial_size(self) -> tuple[int, int]:
        return self._lifecycle.preferred_initial_size()

    def fit_toplevel_to_current_content_once(self) -> None:
        self._lifecycle.fit_toplevel_to_current_content_once()

    def on_parent_tab_selected(self) -> None:
        """Refit again after the top-level profile switch has settled."""
        self._lifecycle.on_parent_tab_selected()

    def _request_visible_lifecycle_refit(self, *, settle_cycles: int = 1) -> None:
        self._lifecycle.request_visible_lifecycle_refit(settle_cycles=settle_cycles)

    def _on_standard_tab_changed(self, _event=None) -> None:
        self._lifecycle.on_nested_tab_changed()

    def _common_input_values(self) -> dict[str, str]:
        return {
            "p_to": self._p_to_var.get(),
            "p_sb": self._p_sb_var.get(),
            "p_ck": self._p_ck_var.get(),
            "p_off": self._p_off_var.get(),
        }

    def _common_numeric_values(self) -> dict[str, str]:
        return {
            "p_to": self._p_to_var.get(),
            "p_sb": self._p_sb_var.get(),
            "p_ck": self._p_ck_var.get(),
            "p_off": self._p_off_var.get(),
        }

    def _on_common_input_changed(self) -> None:
        self.seer_section.schedule_recalculate()
        self.scop_section.schedule_recalculate()

    def _on_common_numeric_var_changed(self) -> None:
        if self._syncing_common_inputs:
            return
        self._sync_common_input_tables(self._common_numeric_values())
        self._on_common_input_changed()

    def _on_common_table_values_changed(self, table: MetricInputTable) -> None:
        if self._syncing_common_inputs:
            return
        values = table.get_text_values()
        self._syncing_common_inputs = True
        try:
            self._set_common_numeric_vars(values)
            self._sync_common_input_tables(values, source=table)
        finally:
            self._syncing_common_inputs = False
        self._on_common_input_changed()

    def _set_common_numeric_vars(self, values: Mapping[str, str]) -> None:
        var_by_key = {
            "p_to": self._p_to_var,
            "p_sb": self._p_sb_var,
            "p_ck": self._p_ck_var,
            "p_off": self._p_off_var,
        }
        for key, var in var_by_key.items():
            value = values.get(key, var.get())
            if var.get() != value:
                var.set(value)

    def _sync_common_input_tables(
        self,
        values: Mapping[str, str],
        *,
        source: MetricInputTable | None = None,
    ) -> None:
        self._syncing_common_inputs = True
        try:
            for table in self._common_input_tables:
                if table is not source:
                    table.set_values_batch(values)
        finally:
            self._syncing_common_inputs = False

    def _create_common_input_panel(self, parent: tk.Widget) -> ttk.LabelFrame:
        common_frame = ttk.LabelFrame(parent, text="공통 입력")
        common_frame.pack(fill=tk.X, padx=4, pady=(4, 0))
        common_frame.columnconfigure(0, weight=0)
        table = MetricInputTable(
            common_frame,
            columns=(
                ("p_to", "Pto [W]"),
                ("p_sb", "Psb [W]"),
                ("p_ck", "Pck [W]"),
                ("p_off", "Poff [W]"),
            ),
            rows=(("common", "입력값"),),
            editable_cells={
                ("common", "p_to"): "p_to",
                ("common", "p_sb"): "p_sb",
                ("common", "p_ck"): "p_ck",
                ("common", "p_off"): "p_off",
            },
            row_header_chars=8,
            data_column_chars=8,
            layout_policy="content_hug",
        )
        table.grid(row=0, column=0, sticky="w", padx=6, pady=6)
        table.set_values(self._common_numeric_values())
        table.set_values_changed_callback(
            lambda table=table: self._on_common_table_values_changed(table)
        )
        self._common_input_tables.append(table)
        self._common_input_controllers.append(TkTableController(table))

        return common_frame
