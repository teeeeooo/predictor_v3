"""AHRI 210/240 HSPF2 main calculation section for Tkinter."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from apps.calculator.ui.ahri.hspf2_adapter import (
    AHRI_HSPF2_POINT_ORDER,
    AHRI_HSPF2_TEMPERATURES_C,
    AhriHspf2Adapter,
    AhriHspf2InputError,
    AhriHspf2Options,
)
from apps.calculator.ui.ahri.hspf2_mock_data import HSPF2_DEV_SAMPLE_VALUES
from apps.calculator.ui.auto_calc import DebouncedAutoCalc
from apps.calculator.ui.layout_constants import ISO_SECTION_BLOCK_GAP, ISO_SECTION_PADX
from apps.calculator.ui.metric_input_table import MetricInputTable
from apps.calculator.ui.result_models import ResultSummary
from apps.calculator.ui.result_panel import ResultPanel
from apps.calculator.ui.table.controller import TkTableController


class AhriHspf2Section:
    """Compose HSPF2 options, anchor, heating points, and result."""

    def __init__(
        self, parent: tk.Widget, *, adapter: AhriHspf2Adapter | None = None
    ) -> None:
        self.adapter = adapter or AhriHspf2Adapter()
        self._frame = ttk.LabelFrame(parent, text="HSPF2")
        self._frame.columnconfigure(0, weight=1)
        self._build_option_bar()
        self.numeric_table = self._build_numeric_table()
        self.a2_table = self._build_a2_table()
        self.heating_table = self._build_heating_table()
        self._tables = (self.numeric_table, self.a2_table, self.heating_table)
        self._populate_initial_values()
        self._controllers = tuple(TkTableController(table) for table in self._tables)

        self.result_panel = ResultPanel(self._frame, title="AHRI 210/240 HSPF2 결과")
        self.result_panel.grid(
            row=4, column=0, sticky="w", padx=ISO_SECTION_PADX,
            pady=(0, ISO_SECTION_BLOCK_GAP)
        )
        self._auto_calc = DebouncedAutoCalc(self._frame, self.recalculate_now)
        for table in self._tables:
            table.set_values_changed_callback(self.schedule_recalculate)
        for variable in (
            self.region_var,
            self.h1n_same_speed_var,
            self.minimum_speed_var,
        ):
            variable.trace_add("write", lambda *_args: self.schedule_recalculate())
        for variable in self._optional_vars().values():
            variable.trace_add("write", lambda *_args: self._on_optional_changed())
        self._apply_optional_state()
        self._frame.bind("<Destroy>", self._on_destroy, add="+")
        self.recalculate_now()

    def _build_option_bar(self) -> None:
        frame = ttk.LabelFrame(self._frame, text="Options")
        frame.grid(row=0, column=0, sticky="w", padx=ISO_SECTION_PADX, pady=(8, 6))
        self.region_var = tk.StringVar(value="IV")
        self.h42_var = tk.BooleanVar(value=True)
        self.h12_var = tk.BooleanVar(value=False)
        self.h22_var = tk.BooleanVar(value=False)
        self.h1n_same_speed_var = tk.BooleanVar(value=False)
        self.minimum_speed_var = tk.BooleanVar(value=True)
        ttk.Label(frame, text="Region:").pack(side=tk.LEFT, padx=(6, 3), pady=6)
        ttk.Combobox(
            frame, textvariable=self.region_var, values=("IV",), state="readonly", width=4
        ).pack(side=tk.LEFT, padx=(0, 10), pady=6)
        ttk.Label(frame, text="Measured:").pack(side=tk.LEFT, padx=(0, 3))
        for label, variable in (
            ("H42", self.h42_var),
            ("H12", self.h12_var),
            ("H22", self.h22_var),
        ):
            ttk.Checkbutton(frame, text=label, variable=variable).pack(side=tk.LEFT)
        ttk.Label(frame, text="Flags:").pack(side=tk.LEFT, padx=(10, 3))
        ttk.Checkbutton(
            frame, text="H1N=H32 Hz", variable=self.h1n_same_speed_var
        ).pack(side=tk.LEFT)
        ttk.Checkbutton(frame, text="MinSpd", variable=self.minimum_speed_var).pack(
            side=tk.LEFT, padx=(0, 6)
        )

    def _build_numeric_table(self) -> MetricInputTable:
        table = MetricInputTable(
            self._frame,
            columns=(
                ("cd", "Cd"),
                ("defrost_credit", "Defrost Credit"),
                ("cut_out_c", "Cut Out [°C]"),
                ("cut_in_c", "Cut In [°C]"),
            ),
            rows=(("value", "Value"),),
            editable_cells={
                ("value", key): key
                for key in ("cd", "defrost_credit", "cut_out_c", "cut_in_c")
            },
            row_header_chars=8,
            data_column_chars=14,
        )
        table.grid(row=1, column=0, sticky="w", padx=ISO_SECTION_PADX, pady=(0, 6))
        return table

    def _build_a2_table(self) -> MetricInputTable:
        table = MetricInputTable(
            self._frame,
            columns=(("A2", "A2"),),
            rows=(
                ("capacity", "Capacity [Btu/h]"),
                ("power", "Power [W]"),
                ("cop", "COP"),
            ),
            editable_cells={
                ("capacity", "A2"): "a2_capacity",
                ("power", "A2"): "a2_power",
            },
            row_header_chars=18,
            data_column_chars=18,
        )
        table.grid(row=2, column=0, sticky="w", padx=ISO_SECTION_PADX, pady=(0, 6))
        return table

    def _build_heating_table(self) -> MetricInputTable:
        editable = {
            (row, point): f"{row}_{point}"
            for point in AHRI_HSPF2_POINT_ORDER
            for row in ("capacity", "power")
        }
        table = MetricInputTable(
            self._frame,
            columns=tuple((point, point) for point in AHRI_HSPF2_POINT_ORDER),
            rows=(
                ("condition_temp", "Condition / Temp"),
                ("capacity", "Capacity [Btu/h]"),
                ("power", "Power [W]"),
                ("cop", "COP"),
            ),
            editable_cells=editable,
            row_header_chars=18,
            data_column_chars=12,
        )
        table.grid(row=3, column=0, sticky="w", padx=ISO_SECTION_PADX, pady=(0, 8))
        for point in AHRI_HSPF2_POINT_ORDER:
            table.static_cell_labels[("condition_temp", point)].configure(
                text=f"Heating / {AHRI_HSPF2_TEMPERATURES_C[point]:.1f} °C"
            )
        return table

    def _populate_initial_values(self) -> None:
        self.numeric_table.set_values(
            {"cd": "0.25", "defrost_credit": "1.0", "cut_out_c": "-40.0", "cut_in_c": "-40.0"}
        )
        for table in (self.a2_table, self.heating_table):
            table.set_values(
                {
                    key: HSPF2_DEV_SAMPLE_VALUES[key]
                    for key in table.field_order
                    if key in HSPF2_DEV_SAMPLE_VALUES
                }
            )

    def pack(self, **kwargs: object) -> None:
        self._frame.pack(**kwargs)

    def schedule_recalculate(self) -> None:
        self._auto_calc.schedule()

    def _optional_vars(self) -> dict[str, tk.BooleanVar]:
        return {"H42": self.h42_var, "H12": self.h12_var, "H22": self.h22_var}

    def _on_optional_changed(self) -> None:
        self._apply_optional_state()
        self.schedule_recalculate()

    def _apply_optional_state(self) -> None:
        readonly = {
            (row, point)
            for point, variable in self._optional_vars().items()
            if not variable.get()
            for row in ("capacity", "power")
        }
        self.heating_table.set_readonly_addresses(
            readonly, display_values={address: "" for address in readonly}
        )
        if hasattr(self, "_controllers"):
            self._controllers[2].refresh()

    def _options(self) -> AhriHspf2Options:
        return AhriHspf2Options(
            region=self.region_var.get(),
            measured_h42=self.h42_var.get(),
            measured_h12=self.h12_var.get(),
            measured_h22=self.h22_var.get(),
            h1n_same_speed_as_h32=self.h1n_same_speed_var.get(),
            minimum_speed_limited=self.minimum_speed_var.get(),
        )

    def recalculate_now(self) -> None:
        values = {}
        for table in self._tables:
            values.update(table.get_text_values())
            table.clear_invalid_fields()
        options = self._options()
        self._update_cop_rows(
            self.adapter.compute_display_cops(values, options=options)
        )
        try:
            summary = self.adapter.calculate(values, options=options)
        except AhriHspf2InputError as exc:
            for table in self._tables:
                errors = {key: value for key, value in exc.field_errors.items() if key in table.field_order}
                if errors:
                    table.set_invalid_fields(errors)
            self.result_panel.clear()
            return
        except (KeyError, TypeError, ValueError, ZeroDivisionError):
            self.result_panel.clear()
            return
        if summary is None:
            self.result_panel.clear()
            return
        fields = (
            ("HSPF2", f"{summary.hspf2:.3f}"),
            ("Total Heating [kBtu]", f"{summary.total_heating_kbtu:.3f}"),
            ("Total Energy [kWh]", f"{summary.total_energy_kwh:.3f}"),
        )
        self.result_panel.set_summaries(
            (ResultSummary("HSPF2", fields, "자동 계산 완료"),)
        )

    def _update_cop_rows(self, cops: dict[str, float]) -> None:
        self.a2_table.static_cell_labels[("cop", "A2")].configure(
            text=f"{cops['A2']:.2f}" if "A2" in cops else ""
        )
        for point in AHRI_HSPF2_POINT_ORDER:
            self.heating_table.static_cell_labels[("cop", point)].configure(
                text=f"{cops[point]:.2f}" if point in cops else ""
            )

    def _on_destroy(self, event: tk.Event) -> None:
        if event.widget is self._frame:
            self._auto_calc.dispose()
