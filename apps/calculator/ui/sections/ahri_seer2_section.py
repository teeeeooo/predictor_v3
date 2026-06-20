"""AHRI 210/240 SEER2 main calculation section for Tkinter."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from apps.calculator.ui.ahri import (
    AHRI_SEER2_POINT_ORDER,
    AHRI_SEER2_TEMPERATURES_C,
    AhriSeer2Adapter,
    AhriSeer2InputError,
)
from apps.calculator.ui.auto_calc import DebouncedAutoCalc
from apps.calculator.ui.layout_constants import ISO_SECTION_BLOCK_GAP, ISO_SECTION_PADX
from apps.calculator.ui.metric_input_table import MetricInputTable
from apps.calculator.ui.result_models import ResultSummary
from apps.calculator.ui.result_panel import ResultPanel
from apps.calculator.ui.table.controller import TkTableController


class AhriSeer2Section:
    """Type option, five-point matrix, and compact SEER2 result surface."""

    def __init__(
        self,
        parent: tk.Widget,
        *,
        adapter: AhriSeer2Adapter | None = None,
    ) -> None:
        self.adapter = adapter or AhriSeer2Adapter()
        self._frame = ttk.LabelFrame(parent, text="SEER2")
        self._frame.columnconfigure(0, weight=1)

        option_frame = ttk.LabelFrame(self._frame, text="Options")
        option_frame.grid(
            row=0,
            column=0,
            sticky="w",
            padx=ISO_SECTION_PADX,
            pady=(8, ISO_SECTION_BLOCK_GAP),
        )
        ttk.Label(option_frame, text="Type").pack(side=tk.LEFT, padx=(6, 4), pady=6)
        self.type_var = tk.StringVar(value="HP")
        self.type_selector = ttk.Combobox(
            option_frame,
            textvariable=self.type_var,
            values=("HP", "AC"),
            state="readonly",
            width=6,
        )
        self.type_selector.pack(side=tk.LEFT, padx=(0, 6), pady=6)

        editable_cells = {
            (row, point): f"{row}_{point}"
            for point in AHRI_SEER2_POINT_ORDER
            for row in ("capacity", "power")
        }
        self.input_table = MetricInputTable(
            self._frame,
            columns=tuple((point, point) for point in AHRI_SEER2_POINT_ORDER),
            rows=(
                ("condition_temp", "Condition / Temp"),
                ("capacity", "Capacity [Btu/h]"),
                ("power", "Power [W]"),
                ("eer2", "EER2"),
            ),
            editable_cells=editable_cells,
            row_header_chars=18,
            data_column_chars=14,
            layout_policy="content_hug",
            values_changed_callback=self.schedule_recalculate,
        )
        self.input_table.grid(
            row=1,
            column=0,
            sticky="w",
            padx=ISO_SECTION_PADX,
            pady=(0, ISO_SECTION_BLOCK_GAP),
        )
        self.input_controller = TkTableController(self.input_table)
        for point in AHRI_SEER2_POINT_ORDER:
            self._set_static_cell(
                ("condition_temp", point),
                f"Cooling / {AHRI_SEER2_TEMPERATURES_C[point]:.1f} °C",
            )
            self._set_static_cell(("eer2", point), "")

        self.result_panel = ResultPanel(self._frame, title="AHRI 210/240 SEER2 결과")
        self.result_panel.grid(
            row=2,
            column=0,
            sticky="w",
            padx=ISO_SECTION_PADX,
            pady=(0, ISO_SECTION_BLOCK_GAP),
        )

        self._auto_calc = DebouncedAutoCalc(self._frame, self.recalculate_now)
        self.input_table.set_values_changed_callback(self.schedule_recalculate)
        self.type_var.trace_add("write", lambda *_args: self.schedule_recalculate())
        self._frame.bind("<Destroy>", self._on_destroy, add="+")
        self.recalculate_now()

    def pack(self, **kwargs: object) -> None:
        self._frame.pack(**kwargs)

    def schedule_recalculate(self) -> None:
        self._auto_calc.schedule()

    def recalculate_now(self) -> None:
        try:
            summary = self.adapter.calculate(
                self.input_table.get_text_values(),
                system_type=self.type_var.get(),
            )
        except AhriSeer2InputError as exc:
            self.input_table.set_invalid_fields(exc.field_errors)
            self._clear_results()
            return
        except (KeyError, TypeError, ValueError, ZeroDivisionError):
            self._clear_results()
            return

        self.input_table.clear_invalid_fields()
        if summary is None:
            self._clear_results()
            return
        for point, eer2 in summary.eer2_by_point.items():
            self._set_static_cell(("eer2", point), f"{eer2:.2f}")
        self.result_panel.set_summaries(
            (
                ResultSummary(
                    title="SEER2",
                    fields=(("SEER2", f"{summary.seer2:.3f}"),),
                    status="",
                ),
            )
        )

    def _clear_results(self) -> None:
        for point in AHRI_SEER2_POINT_ORDER:
            self._set_static_cell(("eer2", point), "")
        self.result_panel.clear()

    def _set_static_cell(self, address: tuple[str, str], value: str) -> None:
        label = self.input_table.static_cell_labels.get(address)
        if label is not None:
            label.configure(text=value)

    def _on_destroy(self, event: tk.Event) -> None:
        if event.widget is self._frame:
            self._auto_calc.dispose()
