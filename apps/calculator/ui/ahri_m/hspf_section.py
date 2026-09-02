"""Tk surface for AHRI 210/240-2017 Appendix M HSPF."""

from __future__ import annotations

from collections.abc import Callable
import tkinter as tk
from tkinter import ttk

from apps.calculator.application.ahri_m import (
    AHRI_M_HSPF_POINT_ORDER, AHRI_M_HSPF_TEMPERATURES_C,
    AhriHspfAdapter, AhriHspfInputError, AhriHspfOptions,
)
from apps.calculator.ui.ahri_m.batch_dialog import AhriMBatchAccess
from apps.calculator.ui.ahri_m.points import ahri_m_hspf_ui_point_label
from apps.calculator.ui.auto_calc import DebouncedAutoCalc
from apps.calculator.ui.layout_constants import CONTROL_COMPACT_GAP, CONTROL_GROUP_GAP, CONTROL_ROW_PADY, ISO_SECTION_BLOCK_GAP, ISO_SECTION_PADX, METRIC_TABLE_DESCRIPTIVE_ROW_HEADER_CHARS, METRIC_TABLE_HEATING_DATA_COLUMN_CHARS, METRIC_TABLE_POINT_DATA_COLUMN_CHARS
from apps.calculator.ui.metric_input_table import MetricInputTable
from apps.calculator.ui.result_actions import add_result_actions
from apps.calculator.ui.result_models import ResultSummary
from apps.calculator.ui.result_panel import ResultPanel
from apps.calculator.ui.sections.bin_detail_panel import BinDetailPanel, BinDetailSource
from apps.calculator.ui.sections.detail_visibility import DetailPanelVisibility
from .detail_schema import AHRI_M_HSPF_DETAIL_SCHEMA


class AhriMHspfSection:
    def __init__(self, parent: tk.Widget, *, adapter: AhriHspfAdapter | None = None, on_trace_visibility_changed: Callable[[], None] | None = None) -> None:
        self.adapter = adapter or AhriHspfAdapter()
        self._on_detail_visibility_changed = on_trace_visibility_changed
        self._frame = ttk.LabelFrame(parent, text="HSPF")
        self._frame.columnconfigure(0, weight=1)
        self._build_options()
        self.numeric_table = MetricInputTable(
            self._frame,
            columns=(("cd", "CDh"), ("defrost_credit", "Defrost Credit"), ("defrost_test_minutes", "Defrost Test [min]"), ("defrost_max_minutes", "Defrost Max [min]"), ("cut_out_c", "Cut Out [°C]"), ("cut_in_c", "Cut In [°C]")),
            rows=(("value", "Value"),),
            editable_cells={("value", key): key for key in ("cd", "defrost_test_minutes", "defrost_max_minutes", "cut_out_c", "cut_in_c")},
            data_column_chars=METRIC_TABLE_POINT_DATA_COLUMN_CHARS, visual_style="shared",
        )
        self.numeric_table.grid(row=1, column=0, sticky="w", padx=ISO_SECTION_PADX, pady=(0, 6))
        self.heating_table = MetricInputTable(
            self._frame,
            columns=tuple((point, ahri_m_hspf_ui_point_label(point)) for point in AHRI_M_HSPF_POINT_ORDER),
            rows=(("condition_temp", "Condition / Temp"), ("capacity", "Capacity [Btu/h]"), ("power", "Power [W]"), ("cop", "COP")),
            editable_cells={(kind, point): f"{kind}_{point}" for point in AHRI_M_HSPF_POINT_ORDER for kind in ("capacity", "power")},
            row_header_chars=METRIC_TABLE_DESCRIPTIVE_ROW_HEADER_CHARS, data_column_chars=METRIC_TABLE_HEATING_DATA_COLUMN_CHARS, visual_style="shared",
        )
        self.heating_table.grid(row=2, column=0, sticky="w", padx=ISO_SECTION_PADX, pady=(0, ISO_SECTION_BLOCK_GAP))
        self.numeric_table.set_values_batch({"cd": "0.25", "defrost_test_minutes": "90", "defrost_max_minutes": "720", "cut_out_c": "-17.8", "cut_in_c": "-15.0"})
        self.numeric_table.static_cell_labels[("value", "defrost_credit")].configure(text="1.000")
        for point in AHRI_M_HSPF_POINT_ORDER:
            self.heating_table.static_cell_labels[("condition_temp", point)].configure(text=f"{AHRI_M_HSPF_TEMPERATURES_C[point]:.1f} °C")
            self.heating_table.static_cell_labels[("cop", point)].configure(text="")
        self.result_panel = ResultPanel(self._frame, title="AHRI 210/240 M HSPF 결과")
        self.result_panel.grid(row=3, column=0, sticky="w", padx=ISO_SECTION_PADX, pady=(0, ISO_SECTION_BLOCK_GAP))
        action_row = ttk.Frame(self._frame)
        action_row.grid(row=4, column=0, sticky="w", padx=ISO_SECTION_PADX, pady=(0, ISO_SECTION_BLOCK_GAP))
        self._batch_access = AhriMBatchAccess(action_row, metric="HSPF", shell_parent=self._frame)
        self.batch_button = self._batch_access.button
        self.detail_toggle = ttk.Button(action_row, text="상세 보기 ↓", command=self._toggle_detail)
        self.detail_toggle.pack(side=tk.LEFT)
        self.result_actions = add_result_actions(action_row, parent=self._frame, result_owner=self.result_panel, csv_filename="ahri_m_hspf_result.csv", surface_prefix="ahri_m_hspf_result")
        self.copy_button = self.result_actions.copy_button
        self.export_button = self.result_actions.export_button
        self.detail_panel = BinDetailPanel(self._frame, source_labels=("HSPF",), default_source="HSPF", csv_filename="ahri_m_hspf_bin_detail.csv", show_source_selector=False, schema=AHRI_M_HSPF_DETAIL_SCHEMA)
        self._detail_visibility = DetailPanelVisibility(panel=self.detail_panel, button=self.detail_toggle, grid_options={"row": 5, "column": 0, "sticky": "ew", "padx": 0, "pady": (0, ISO_SECTION_BLOCK_GAP)}, on_change=self._on_detail_visibility_changed)
        self._auto_calc = DebouncedAutoCalc(self._frame, self.recalculate_now)
        self.numeric_table.set_values_changed_callback(self._on_input_changed)
        self.heating_table.set_values_changed_callback(self._on_input_changed)
        for var in (self.h12_var, self.h22_var, self.h1n_same_speed_var, self.cutout_var, self.demand_defrost_var):
            var.trace_add("write", lambda *_args: self._on_option_changed())
        self._apply_option_state()
        self._frame.bind("<Destroy>", self._on_destroy, add="+")
        self._show_placeholder("입력 대기")

    def _build_options(self):
        frame = ttk.LabelFrame(self._frame, text="Options")
        frame.grid(row=0, column=0, sticky="w", padx=ISO_SECTION_PADX, pady=(ISO_SECTION_BLOCK_GAP, CONTROL_ROW_PADY))
        ttk.Label(frame, text="Region: IV").pack(side=tk.LEFT, padx=(CONTROL_ROW_PADY, CONTROL_GROUP_GAP), pady=CONTROL_ROW_PADY)
        self.h12_var = tk.BooleanVar(master=self._frame, value=False)
        self.h22_var = tk.BooleanVar(master=self._frame, value=False)
        self.h1n_same_speed_var = tk.BooleanVar(master=self._frame, value=False)
        self.cutout_var = tk.BooleanVar(master=self._frame, value=True)
        self.demand_defrost_var = tk.BooleanVar(master=self._frame, value=False)
        ttk.Label(frame, text="Measured:").pack(side=tk.LEFT, padx=(0, CONTROL_COMPACT_GAP))
        ttk.Checkbutton(frame, text="H12", variable=self.h12_var).pack(side=tk.LEFT)
        ttk.Checkbutton(frame, text="H22", variable=self.h22_var).pack(side=tk.LEFT)
        ttk.Label(frame, text="Flags:").pack(side=tk.LEFT, padx=(CONTROL_GROUP_GAP, CONTROL_COMPACT_GAP))
        ttk.Checkbutton(frame, text="H1N=H32 Hz", variable=self.h1n_same_speed_var).pack(side=tk.LEFT)
        ttk.Checkbutton(frame, text="Demand Defrost", variable=self.demand_defrost_var).pack(side=tk.LEFT, padx=(CONTROL_GROUP_GAP, 0))
        ttk.Checkbutton(frame, text="Automatic Cutout", variable=self.cutout_var).pack(side=tk.LEFT, padx=(CONTROL_GROUP_GAP, CONTROL_ROW_PADY))

    def pack(self, **kwargs): self._frame.pack(**kwargs)
    def _toggle_detail(self): self._detail_visibility.toggle()
    def _on_input_changed(self):
        self.detail_panel.set_status("입력 대기"); self._auto_calc.schedule()
    def _on_option_changed(self):
        self._apply_option_state(); self._on_input_changed()

    @property
    def options(self):
        return AhriHspfOptions(
            measured_h12=self.h12_var.get(),
            measured_h22=self.h22_var.get(),
            h1n_same_speed_as_h32=self.h1n_same_speed_var.get(),
            automatic_cutout=self.cutout_var.get(),
            demand_defrost=self.demand_defrost_var.get(),
        )

    def _apply_option_state(self):
        readonly = []
        for point, enabled in (("H12", self.h12_var.get()), ("H22", self.h22_var.get())):
            if not enabled:
                readonly.extend((("capacity", point), ("power", point)))
        self.heating_table.set_readonly_addresses(readonly, display_values={address: "" for address in readonly})
        numeric_readonly = []
        display_values = {}
        if not self.demand_defrost_var.get():
            for address in (("value", "defrost_test_minutes"), ("value", "defrost_max_minutes")):
                numeric_readonly.append(address)
                display_values[address] = "N/A"
        if not self.cutout_var.get():
            for address in (("value", "cut_out_c"), ("value", "cut_in_c")):
                numeric_readonly.append(address)
                display_values[address] = "No cutout"
        self.numeric_table.set_readonly_addresses(
            numeric_readonly,
            display_values=display_values,
        )
        self.numeric_table.static_cell_labels[("value", "defrost_credit")].configure(
            text="계산 대기" if self.demand_defrost_var.get() else "1.000"
        )

    def recalculate_now(self) -> None:
        values = {**self.numeric_table.get_text_values(), **self.heating_table.get_text_values()}
        try:
            summary = self.adapter.calculate(values, options=self.options)
        except AhriHspfInputError as exc:
            self._apply_errors(exc.field_errors); self._show_placeholder("입력 확인 필요"); self.detail_panel.set_status("입력 확인 필요"); return
        self._update_cops(values)
        if summary is None:
            self._clear_errors(); self._show_placeholder("입력 대기"); self.detail_panel.set_status("입력 대기"); return
        self._clear_errors()
        self.numeric_table.static_cell_labels[("value", "defrost_credit")].configure(
            text=f"{summary.defrost_credit:.3f}"
        )
        self.result_panel.set_summaries((ResultSummary(
            title="HSPF",
            fields=(("Raw HSPF", f"{summary.raw_hspf:.5f}"), ("Published HSPF", f"{summary.published_hspf:.2f}"), ("DHRmin [Btu/h]", f"{summary.dhr_min_standardized:.0f}"), ("Heating Load [Btu/h]", f"{summary.heating_load_aggregate:.1f}"), ("Compressor Input [W]", f"{summary.compressor_energy_aggregate:.1f}"), ("Auxiliary Input [W]", f"{summary.resistance_energy_aggregate:.1f}")),
            status=f"자동 계산 완료 · H12 {summary.h12_source} · H22 {summary.h22_source}",
        ),))
        self.detail_panel.set_sources({"HSPF": BinDetailSource(rows=summary.bin_details, summary=(("Raw", f"{summary.raw_hspf:.5f}"), ("Published", f"{summary.published_hspf:.2f}"), ("DHRmin", f"{summary.dhr_min_standardized:.0f}")))})

    def _update_cops(self, values):
        cops = self.adapter.compute_display_cops(values, options=self.options)
        for point in AHRI_M_HSPF_POINT_ORDER:
            self.heating_table.static_cell_labels[("cop", point)].configure(text=f"{cops[point]:.2f}" if point in cops else "")

    def _show_placeholder(self, status):
        self.result_panel.show_placeholder(title="HSPF", field_labels=("Raw HSPF", "Published HSPF", "DHRmin [Btu/h]", "Heating Load [Btu/h]", "Compressor Input [W]", "Auxiliary Input [W]"), status=status)

    def _apply_errors(self, errors):
        self._clear_errors()
        for table in (self.numeric_table, self.heating_table):
            own = {key: value for key, value in errors.items() if key in table.field_order}
            if own: table.set_invalid_fields(own)
    def _clear_errors(self): self.numeric_table.clear_invalid_fields(); self.heating_table.clear_invalid_fields()
    def _on_destroy(self, event):
        if event.widget is self._frame:
            self._auto_calc.dispose()
            self._batch_access.dispose()
