"""ISO/ISEER 2-point single calculation section for Tkinter."""

from __future__ import annotations

from collections.abc import Callable, Mapping

import tkinter as tk
from tkinter import ttk

from core.calculator_dispatcher import create_calculator_for_profile
from ui_tk.auto_calc import DebouncedAutoCalc
from ui_tk.excel_like_table_controller import ExcelLikeTableController
from ui_tk.layout_constants import (
    ISO_SECTION_BLOCK_GAP,
    ISO_SECTION_PADX,
)
from ui_tk.metric_input_table import MetricInputTable
from ui_tk.profile_resolver import (
    resolve_two_point_profile_id,
    two_point_profile_labels,
)
from ui_tk.sections.bin_trace_table import BinTraceTable
from ui_tk.sections.iso_iseer_2point_result_table import (
    IsoIseer2PointResultTable,
)


class IsoIseer2PointSection:
    """ISO 16358-1 and India ISEER 2-point input with auto-calc."""

    def __init__(
        self,
        parent: tk.Widget,
        *,
        on_trace_visibility_changed: Callable[[], None] | None = None,
    ) -> None:
        self._on_trace_visibility_changed = on_trace_visibility_changed
        self._trace_results: dict[str, list[dict]] = {}
        self._trace_status: str | None = "Trace data not available"
        self._frame = ttk.LabelFrame(parent, text="ISO / ISEER 2-point 입력")
        self._frame.columnconfigure(0, weight=1)

        ttk.Label(self._frame, text="시험 입력").grid(
            row=0,
            column=0,
            sticky="w",
            padx=ISO_SECTION_PADX,
            pady=(ISO_SECTION_BLOCK_GAP, 4),
        )
        self.input_table = MetricInputTable(
            self._frame,
            columns=(
                ("full", "35 Full"),
                ("half", "35 Half"),
            ),
            rows=(("capacity", "능력 [W]"), ("power", "전력 [W]")),
            editable_cells={
                ("capacity", "full"): "full_capacity",
                ("power", "full"): "full_power",
                ("capacity", "half"): "half_capacity",
                ("power", "half"): "half_power",
            },
        )
        self.input_table.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=ISO_SECTION_PADX,
            pady=(0, ISO_SECTION_BLOCK_GAP),
        )
        self.result_table = IsoIseer2PointResultTable(
            self._frame, title="ISO / ISEER 결과"
        )
        self.result_panel = self.result_table
        self.result_table.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=ISO_SECTION_PADX,
            pady=(0, ISO_SECTION_BLOCK_GAP),
        )
        self._trace_visible = tk.BooleanVar(master=self._frame, value=False)
        self._trace_controls = ttk.Frame(self._frame)
        self._trace_controls.grid(
            row=3,
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
        self.trace_toggle.surface_role = "two_point_bin_trace_toggle"
        self.trace_toggle.pack(side=tk.LEFT)
        self.trace_profile_combo = ttk.Combobox(
            self._trace_controls,
            values=list(two_point_profile_labels()),
            state="readonly",
        )
        self.trace_profile_combo.set(two_point_profile_labels()[0])
        self.trace_profile_combo.pack(side=tk.LEFT, padx=(6, 0))
        self.trace_profile_combo.bind(
            "<<ComboboxSelected>>", self._on_trace_profile_changed
        )
        self.trace_table = BinTraceTable(self._frame)
        self.input_table.set_values(
            {
                "full_capacity": "3600",
                "full_power": "900",
                "half_capacity": "1700",
                "half_power": "380",
            }
        )
        self.input_controller = ExcelLikeTableController(self.input_table)
        self._auto_calc = DebouncedAutoCalc(self._frame, self.recalculate_now)
        self.input_table.set_values_changed_callback(self._auto_calc.schedule)
        self._frame.bind("<Destroy>", self._on_destroy, add="+")
        self._auto_calc.flush_now()

    def pack(self, **kwargs) -> None:
        self._frame.pack(**kwargs)

    def cancel_pending(self) -> None:
        self._auto_calc.cancel()

    def _read_inputs(self) -> Mapping[str, Mapping[str, float]]:
        values = self.input_table.get_numeric_values()
        return {
            "35_full": {
                "capacity": values["full_capacity"],
                "power": values["full_power"],
            },
            "35_half": {
                "capacity": values["half_capacity"],
                "power": values["half_power"],
            },
        }

    def recalculate_now(self) -> None:
        try:
            measured = self._read_inputs()
        except ValueError:
            self._clear_trace("입력 오류: 숫자 입력을 확인하세요.")
            self.result_table.set_status("입력 오류: 숫자 입력을 확인하세요.")
            return

        rows = []
        trace_results = {}
        errors = []
        for profile_label in two_point_profile_labels():
            try:
                profile_id = resolve_two_point_profile_id(profile_label)
                calc = create_calculator_for_profile(profile_id=profile_id)
                result = calc.calculate_cspf(measured)
                rows.append(_two_point_result_row(profile_label, measured, result))
                trace_results[profile_label] = _bin_details(result)
            except Exception as exc:
                errors.append(f"{profile_label}: {type(exc).__name__}: {exc}")
        if errors:
            self._clear_trace("계산 오류")
            self.result_table.set_status("오류: " + " / ".join(errors))
            return
        self._trace_results = trace_results
        self._trace_status = None
        if self.trace_profile_combo.get() not in self._trace_results:
            self.trace_profile_combo.set(two_point_profile_labels()[0])
        self._update_trace_table()
        self.result_table.set_rows(tuple(rows), status="자동 계산 완료")

    def _on_trace_toggled(self) -> None:
        if self._trace_visible.get():
            self._update_trace_table()
            self.trace_table.grid(
                row=4,
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
        selected = self.trace_profile_combo.get() or two_point_profile_labels()[0]
        self.trace_table.set_data(self._trace_results.get(selected, ()))

    def _clear_trace(self, status: str) -> None:
        self._trace_results = {}
        self._trace_status = status
        self._update_trace_table()

    def _on_destroy(self, event: tk.Event) -> None:
        if event.widget is self._frame:
            self._auto_calc.dispose()


def _two_point_result_row(
    title: str,
    measured: Mapping[str, Mapping[str, float]],
    result: Mapping[str, object],
) -> tuple[str, ...]:
    return (
        title,
        _eer_value(measured, "35_full"),
        _eer_value(measured, "35_half"),
        _metric_value(result, "cspf"),
        _kwh_value(result, ("annual_cooling_kwh", "cstl_kwh", "cstl")),
        _kwh_value(result, ("annual_power_kwh", "csec_kwh", "csec")),
    )


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
