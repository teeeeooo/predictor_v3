"""Tk surface for AHRI 210/240 Appendix M SEER."""

from __future__ import annotations

from collections.abc import Callable
import tkinter as tk
from tkinter import ttk

from apps.calculator.application.ahri_m import (
    AHRI_M_SEER_POINT_ORDER, AHRI_M_SEER_TEMPERATURES_C,
    AhriSeerAdapter, AhriSeerInputError,
)
from apps.calculator.ui.auto_calc import DebouncedAutoCalc
from apps.calculator.ui.layout_constants import ISO_SECTION_BLOCK_GAP, ISO_SECTION_PADX, METRIC_TABLE_DESCRIPTIVE_ROW_HEADER_CHARS, METRIC_TABLE_HEATING_DATA_COLUMN_CHARS
from apps.calculator.ui.metric_input_table import MetricInputTable
from apps.calculator.ui.result_actions import add_result_actions
from apps.calculator.ui.result_models import ResultSummary
from apps.calculator.ui.result_panel import ResultPanel
from apps.calculator.ui.sections.bin_detail_panel import BinDetailPanel, BinDetailSource
from apps.calculator.ui.sections.detail_visibility import DetailPanelVisibility
from .detail_schema import AHRI_M_SEER_DETAIL_SCHEMA


class AhriMSeerSection:
    def __init__(self, parent: tk.Widget, *, adapter: AhriSeerAdapter | None = None, on_trace_visibility_changed: Callable[[], None] | None = None) -> None:
        self.adapter = adapter or AhriSeerAdapter()
        self._on_detail_visibility_changed = on_trace_visibility_changed
        self._frame = ttk.LabelFrame(parent, text="SEER")
        self._frame.columnconfigure(0, weight=1)
        self.numeric_table = MetricInputTable(
            self._frame, columns=(("cd", "CDc"),), rows=(("value", "Value"),),
            editable_cells={("value", "cd"): "cd"}, visual_style="shared",
        )
        self.numeric_table.grid(row=0, column=0, sticky="w", padx=ISO_SECTION_PADX, pady=(ISO_SECTION_BLOCK_GAP, 6))
        self.input_table = MetricInputTable(
            self._frame,
            columns=tuple((point, point) for point in AHRI_M_SEER_POINT_ORDER),
            rows=(("condition_temp", "Condition / Temp"), ("capacity", "Capacity [Btu/h]"), ("power", "Power [W]"), ("eer", "EER")),
            editable_cells={(kind, point): f"{kind}_{point}" for point in AHRI_M_SEER_POINT_ORDER for kind in ("capacity", "power")},
            row_header_chars=METRIC_TABLE_DESCRIPTIVE_ROW_HEADER_CHARS,
            data_column_chars=METRIC_TABLE_HEATING_DATA_COLUMN_CHARS,
            visual_style="shared",
        )
        self.input_table.grid(row=1, column=0, sticky="w", padx=ISO_SECTION_PADX, pady=(0, ISO_SECTION_BLOCK_GAP))
        self.numeric_table.set_values_batch({"cd": "0.25"})
        for point in AHRI_M_SEER_POINT_ORDER:
            self.input_table.static_cell_labels[("condition_temp", point)].configure(text=f"{AHRI_M_SEER_TEMPERATURES_C[point]:.1f} °C")
            self.input_table.static_cell_labels[("eer", point)].configure(text="")
        self.result_panel = ResultPanel(self._frame, title="AHRI 210/240 M SEER 결과")
        self.result_panel.grid(row=2, column=0, sticky="w", padx=ISO_SECTION_PADX, pady=(0, ISO_SECTION_BLOCK_GAP))
        action_row = ttk.Frame(self._frame)
        action_row.grid(row=3, column=0, sticky="w", padx=ISO_SECTION_PADX, pady=(0, ISO_SECTION_BLOCK_GAP))
        self.detail_toggle = ttk.Button(action_row, text="상세 보기 ↓", command=self._toggle_detail)
        self.detail_toggle.pack(side=tk.LEFT)
        self.result_actions = add_result_actions(action_row, parent=self._frame, result_owner=self.result_panel, csv_filename="ahri_m_seer_result.csv", surface_prefix="ahri_m_seer_result")
        self.copy_button = self.result_actions.copy_button
        self.export_button = self.result_actions.export_button
        self.detail_panel = BinDetailPanel(self._frame, source_labels=("SEER",), default_source="SEER", csv_filename="ahri_m_seer_bin_detail.csv", show_source_selector=False, schema=AHRI_M_SEER_DETAIL_SCHEMA)
        self._detail_visibility = DetailPanelVisibility(panel=self.detail_panel, button=self.detail_toggle, grid_options={"row": 4, "column": 0, "sticky": "ew", "padx": 0, "pady": (0, ISO_SECTION_BLOCK_GAP)}, on_change=self._on_detail_visibility_changed)
        self._auto_calc = DebouncedAutoCalc(self._frame, self.recalculate_now)
        self.numeric_table.set_values_changed_callback(self._on_input_changed)
        self.input_table.set_values_changed_callback(self._on_input_changed)
        self._frame.bind("<Destroy>", self._on_destroy, add="+")
        self._show_placeholder("입력 대기")

    def pack(self, **kwargs): self._frame.pack(**kwargs)
    def _toggle_detail(self): self._detail_visibility.toggle()
    def _on_input_changed(self):
        self.detail_panel.set_status("입력 대기")
        self._auto_calc.schedule()

    def recalculate_now(self) -> None:
        values = {**self.numeric_table.get_text_values(), **self.input_table.get_text_values()}
        try:
            summary = self.adapter.calculate(values)
        except AhriSeerInputError as exc:
            self._apply_errors(exc.field_errors)
            self._show_placeholder("입력 확인 필요")
            self.detail_panel.set_status("입력 확인 필요")
            return
        if summary is None:
            self._clear_errors()
            self._show_placeholder("입력 대기")
            self.detail_panel.set_status("입력 대기")
            return
        self._clear_errors()
        for point, eer in summary.eer_by_point.items():
            self.input_table.static_cell_labels[("eer", point)].configure(text=f"{eer:.2f}")
        self.result_panel.set_summaries((ResultSummary(
            title="SEER",
            fields=(("Raw SEER", f"{summary.raw_seer:.5f}"), ("Published SEER", f"{summary.published_seer:.2f}"), ("기간냉방능력비율 [Btu/h]", f"{summary.seasonal_cooling_numerator:.1f}"), ("기간냉방입력비율 [W]", f"{summary.seasonal_energy_denominator:.1f}")),
            status="자동 계산 완료",
        ),))
        self.detail_panel.set_sources({"SEER": BinDetailSource(rows=summary.bin_details, summary=(("Raw", f"{summary.raw_seer:.5f}"), ("Published", f"{summary.published_seer:.2f}")))})

    def _show_placeholder(self, status):
        self.result_panel.show_placeholder(title="SEER", field_labels=("Raw SEER", "Published SEER", "기간냉방능력비율 [Btu/h]", "기간냉방입력비율 [W]"), status=status)

    def _apply_errors(self, errors):
        self._clear_errors()
        for table in (self.numeric_table, self.input_table):
            own = {key: value for key, value in errors.items() if key in table.field_order}
            if own: table.set_invalid_fields(own)

    def _clear_errors(self):
        self.numeric_table.clear_invalid_fields(); self.input_table.clear_invalid_fields()

    def _on_destroy(self, event):
        if event.widget is self._frame: self._auto_calc.dispose()
