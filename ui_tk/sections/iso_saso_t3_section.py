"""SASO T3 calculation section for Tkinter."""

from __future__ import annotations

from collections.abc import Callable, Mapping

import tkinter as tk
from tkinter import ttk

from core.calculator_dispatcher import create_calculator_for_profile
from ui_tk.auto_calc import DebouncedAutoCalc
from ui_tk.excel_like_table_controller import ExcelLikeTableController
from ui_tk.layout_constants import ISO_SECTION_BLOCK_GAP, ISO_SECTION_PADX
from ui_tk.metric_input_table import MetricInputTable
from ui_tk.profile_resolver import MODE_SASO_T3, resolve_calculation_mode_profile_id
from ui_tk import table_csv_export
from ui_tk.sections.bin_trace_table import BinTraceTable
from ui_tk.sections.iso_saso_t3_result_table import IsoSasoT3ResultTable
from ui_tk.table_grid_model import parse_numeric_cell

_REQUIRED_TRACE_LABEL = "Required only (3-point)"
_OPTIONAL_TRACE_LABEL = "With 35 Min (4-point)"

_POINTS: tuple[tuple[str, str, str], ...] = (
    ("46_full", "full_46", "46 Full"),
    ("35_full", "full_35", "35 Full"),
    ("35_half", "half_35", "35 Half"),
    ("35_min", "min_35", "35 Min"),
)

_DEFAULT_VALUES: Mapping[str, str] = {
    "full_46_capacity": "5000",
    "full_46_power": "1500",
    "full_35_capacity": "6000",
    "full_35_power": "1500",
    "half_35_capacity": "3000",
    "half_35_power": "680",
    "min_35_capacity": "1200",
    "min_35_power": "300",
}


class IsoSasoT3Section:
    """SASO T3 input, optional 35 Min toggle, and scenario comparison."""

    def __init__(
        self,
        parent: tk.Widget,
        *,
        on_trace_visibility_changed: Callable[[], None] | None = None,
    ) -> None:
        self._on_trace_visibility_changed = on_trace_visibility_changed
        self._trace_results: dict[str, list[dict]] = {}
        self._trace_status: str | None = "Trace data not available"
        self._frame = ttk.LabelFrame(parent, text="SASO T3 입력")
        self._frame.columnconfigure(0, weight=1)

        ttk.Label(self._frame, text="시험 입력").grid(
            row=0, column=0, sticky="w", padx=ISO_SECTION_PADX,
            pady=(ISO_SECTION_BLOCK_GAP, 4),
        )
        self.input_table = MetricInputTable(
            self._frame,
            columns=tuple((column_key, label) for _, column_key, label in _POINTS),
            rows=(("capacity", "능력 [W]"), ("power", "전력 [W]")),
            editable_cells={
                ("capacity", "full_46"): "full_46_capacity",
                ("power", "full_46"): "full_46_power",
                ("capacity", "full_35"): "full_35_capacity",
                ("power", "full_35"): "full_35_power",
                ("capacity", "half_35"): "half_35_capacity",
                ("power", "half_35"): "half_35_power",
                ("capacity", "min_35"): "min_35_capacity",
                ("power", "min_35"): "min_35_power",
            },
        )
        self.input_table.grid(
            row=1, column=0, sticky="ew", padx=ISO_SECTION_PADX, pady=(0, 6),
        )

        self.optional_min_enabled = tk.BooleanVar(master=self._frame, value=False)
        self.optional_min_toggle = ttk.Checkbutton(
            self._frame,
            text="35 Min optional test 사용",
            variable=self.optional_min_enabled,
            command=self._on_optional_min_toggled,
        )
        self.optional_min_toggle.grid(
            row=2, column=0, sticky="w", padx=ISO_SECTION_PADX,
            pady=(0, ISO_SECTION_BLOCK_GAP),
        )

        self.result_table = IsoSasoT3ResultTable(self._frame)
        self.result_panel = self.result_table
        self.result_table.grid(
            row=3, column=0, sticky="ew", padx=ISO_SECTION_PADX,
            pady=(0, ISO_SECTION_BLOCK_GAP),
        )
        self._export_controls = ttk.Frame(self._frame)
        self._export_controls.grid(
            row=4,
            column=0,
            sticky="w",
            padx=ISO_SECTION_PADX,
            pady=(0, ISO_SECTION_BLOCK_GAP),
        )
        self.result_copy_button = ttk.Button(
            self._export_controls,
            text="결과 복사",
            command=self._copy_result_table,
        )
        self.result_copy_button.surface_role = "saso_t3_result_copy"
        self.result_copy_button.pack(side=tk.LEFT)
        self.trace_copy_button = ttk.Button(
            self._export_controls,
            text="Trace 복사",
            command=self._copy_trace_table,
        )
        self.trace_copy_button.surface_role = "saso_t3_trace_copy"
        self.trace_copy_button.pack(side=tk.LEFT, padx=(6, 0))
        self.trace_csv_button = ttk.Button(
            self._export_controls,
            text="Trace CSV 내보내기",
            command=self._export_trace_csv,
        )
        self.trace_csv_button.surface_role = "saso_t3_trace_csv_export"
        self.trace_csv_button.pack(side=tk.LEFT, padx=(6, 0))
        self._trace_visible = tk.BooleanVar(master=self._frame, value=False)
        self._trace_controls = ttk.Frame(self._frame)
        self._trace_controls.grid(
            row=5,
            column=0,
            sticky="w",
            padx=ISO_SECTION_PADX,
            pady=(0, ISO_SECTION_BLOCK_GAP),
        )
        self.trace_toggle = ttk.Checkbutton(
            self._trace_controls,
            text="Bin trace",
            variable=self._trace_visible,
            command=self._on_trace_toggled,
        )
        self.trace_toggle.surface_role = "saso_t3_bin_trace_toggle"
        self.trace_toggle.pack(side=tk.LEFT)
        self.trace_profile_combo = ttk.Combobox(
            self._trace_controls,
            values=(_REQUIRED_TRACE_LABEL, _OPTIONAL_TRACE_LABEL),
            state="readonly",
        )
        self.trace_profile_combo.set(_REQUIRED_TRACE_LABEL)
        self.trace_profile_combo.pack(side=tk.LEFT, padx=(6, 0))
        self.trace_profile_combo.bind(
            "<<ComboboxSelected>>", self._on_trace_profile_changed
        )
        self.trace_table = BinTraceTable(self._frame)

        self.input_table.set_values(_DEFAULT_VALUES)
        self.input_controller = ExcelLikeTableController(self.input_table)
        self._auto_calc = DebouncedAutoCalc(self._frame, self.recalculate_now)
        self.input_table.set_values_changed_callback(self._auto_calc.schedule)
        self._frame.bind("<Destroy>", self._on_destroy, add="+")
        self._sync_optional_min_state()
        self._auto_calc.flush_now()

    def pack(self, **kwargs) -> None:
        self._frame.pack(**kwargs)

    def cancel_pending(self) -> None:
        self._auto_calc.cancel()

    def recalculate_now(self) -> None:
        required_measured, required_error = self._read_required_inputs()
        if required_error is not None:
            self._clear_trace(required_error)
            self.result_table.set_status(required_error)
            return

        required_row, required_trace, required_error = self._calculate_required_row(
            required_measured
        )
        if required_error is not None:
            self._clear_trace(required_error)
            self.result_table.set_status(required_error)
            return

        rows = [required_row]
        trace_results = {_REQUIRED_TRACE_LABEL: required_trace}
        status = "자동 계산 완료"
        if self.optional_min_enabled.get():
            optional_measured, optional_error = self._read_optional_inputs(required_measured)
            if optional_error is None:
                optional_row, optional_trace, optional_error = self._calculate_optional_row(
                    optional_measured
                )
            else:
                optional_row = ()
                optional_trace = []
            if optional_error is not None:
                rows.append(_optional_error_row(optional_error))
                status = "4-point 입력 오류: 35 Min 숫자 입력을 확인하세요."
            else:
                rows.append(optional_row)
                trace_results[_OPTIONAL_TRACE_LABEL] = optional_trace
        self._trace_results = trace_results
        self._trace_status = None
        self._update_trace_table()
        self.result_table.set_rows(tuple(rows), status=status)

    def _read_required_inputs(
        self,
    ) -> tuple[dict[str, dict[str, float]], str | None]:
        try:
            return {
                "46_full": self._point_values("full_46"),
                "35_full": self._point_values("full_35"),
                "35_half": self._point_values("half_35"),
            }, None
        except ValueError:
            return {}, "입력 오류: 필수 시험점 숫자 입력을 확인하세요."

    def _read_optional_inputs(
        self,
        required_measured: Mapping[str, Mapping[str, float]],
    ) -> tuple[dict[str, dict[str, float]], str | None]:
        try:
            measured = {key: dict(value) for key, value in required_measured.items()}
            measured["35_min"] = self._point_values("min_35")
            return measured, None
        except ValueError:
            return {}, "입력 오류"

    def _point_values(self, column_key: str) -> dict[str, float]:
        text_values = self.input_table.get_text_values()
        capacity = _parse_positive(text_values[f"{column_key}_capacity"])
        power = _parse_positive(text_values[f"{column_key}_power"])
        return {"capacity": capacity, "power": power}

    def _calculate_required_row(
        self, measured: Mapping[str, Mapping[str, float]]
    ) -> tuple[tuple[str, ...], list[dict], str | None]:
        try:
            calc = create_calculator_for_profile(
                profile_id=resolve_calculation_mode_profile_id(MODE_SASO_T3)
            )
            calc.config["cspf_test_profile"]["test_selection"] = "required_only"
            result = calc.calculate_cspf(measured)
            return _saso_result_row(
                "Required only (3-point)", measured, result, include_min=False
            ), _bin_details(result), None
        except Exception:
            return (), [], "계산 오류: SASO T3 required-only 결과를 계산할 수 없습니다."

    def _calculate_optional_row(
        self, measured: Mapping[str, Mapping[str, float]]
    ) -> tuple[tuple[str, ...], list[dict], str | None]:
        try:
            calc = create_calculator_for_profile(
                profile_id=resolve_calculation_mode_profile_id(MODE_SASO_T3)
            )
            calc.config["cspf_test_profile"]["test_selection"] = "with_optional_test"
            result = calc.calculate_cspf(measured)
            return _saso_result_row(
                "With 35 Min (4-point)", measured, result, include_min=True
            ), _bin_details(result), None
        except Exception:
            return (), [], "계산 오류"

    def _on_optional_min_toggled(self) -> None:
        self._sync_optional_min_state()
        self._sync_optional_trace_state()
        self._auto_calc.schedule()

    def _sync_optional_min_state(self) -> None:
        state = tk.NORMAL if self.optional_min_enabled.get() else tk.DISABLED
        for field_key in ("min_35_capacity", "min_35_power"):
            self.input_table.editable_entries[field_key].configure(state=state)

    def _sync_optional_trace_state(self) -> None:
        if not self.optional_min_enabled.get():
            self._trace_results.pop(_OPTIONAL_TRACE_LABEL, None)
            self._update_trace_table()

    def _on_trace_toggled(self) -> None:
        if self._trace_visible.get():
            self._update_trace_table()
            self.trace_table.grid(
                row=6,
                column=0,
                sticky="ew",
                padx=ISO_SECTION_PADX,
                pady=(0, ISO_SECTION_BLOCK_GAP),
            )
        else:
            self.trace_table.grid_remove()
        if self._on_trace_visibility_changed is not None:
            self._on_trace_visibility_changed()

    def _on_trace_profile_changed(self, _event=None) -> None:
        self._update_trace_table()

    def _update_trace_table(self) -> None:
        if self._trace_status is not None:
            self.trace_table.set_status(self._trace_status)
            return
        selected = self.trace_profile_combo.get() or _REQUIRED_TRACE_LABEL
        trace_rows = self._trace_results.get(selected)
        if trace_rows:
            self.trace_table.set_data(trace_rows)
            return
        if selected == _OPTIONAL_TRACE_LABEL:
            self.trace_table.set_status("Trace data not available for With 35 Min (4-point)")
            return
        self.trace_table.set_status("Trace data not available")

    def _clear_trace(self, status: str) -> None:
        self._trace_results = {}
        self._trace_status = status
        self._update_trace_table()

    def _copy_result_table(self) -> bool:
        return self.result_table.copy_table()

    def _copy_trace_table(self) -> bool:
        self._update_trace_table()
        return self.trace_table.copy_table()

    def _export_trace_csv(self) -> bool:
        self._update_trace_table()
        headers, rows = self.trace_table.table_export_data()
        return table_csv_export.export_table_to_csv(
            self._frame, "saso_t3_bin_trace.csv", headers, rows
        )

    def _on_destroy(self, event: tk.Event) -> None:
        if event.widget is self._frame:
            self._auto_calc.dispose()


def _parse_positive(text: str) -> float:
    value = parse_numeric_cell(text)
    if value <= 0:
        raise ValueError("numeric cell must be positive")
    return value


def _saso_result_row(
    title: str,
    measured: Mapping[str, Mapping[str, float]],
    result: Mapping[str, object],
    *,
    include_min: bool,
) -> tuple[str, ...]:
    return (
        title,
        _eer_value(measured, "46_full"),
        _eer_value(measured, "35_full"),
        _eer_value(measured, "35_half"),
        _eer_value(measured, "35_min") if include_min else "-",
        _metric_value(result, "cspf"),
        _kwh_value(result, ("annual_cooling_kwh", "cstl_kwh", "cstl")),
        _kwh_value(result, ("annual_power_kwh", "csec_kwh", "csec")),
    )


def _optional_error_row(message: str) -> tuple[str, ...]:
    return ("With 35 Min (4-point)", "-", "-", "-", message, "-", "-", "-")


def _bin_details(result: Mapping[str, object]) -> list[dict]:
    raw = result.get("bin_details")
    if not isinstance(raw, list):
        return []
    return [dict(item) for item in raw if isinstance(item, Mapping)]


def _eer_value(measured: Mapping[str, Mapping[str, float]], point_key: str) -> str:
    point = measured.get(point_key, {})
    capacity = point.get("capacity")
    power = point.get("power")
    if capacity is None or power is None or power <= 0:
        return "-"
    return f"{capacity / power:.2f}"


def _metric_value(result: Mapping[str, object], key: str) -> str:
    value = result.get(key)
    return "-" if value is None else f"{float(value):.3f}"


def _kwh_value(result: Mapping[str, object], aliases: tuple[str, ...]) -> str:
    for key in aliases:
        value = result.get(key)
        if value is not None:
            return f"{float(value):.1f}"
    return "-"
