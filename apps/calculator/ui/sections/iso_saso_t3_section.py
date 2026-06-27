"""SASO T3 calculation section for Tkinter."""

from __future__ import annotations

from collections.abc import Callable, Mapping

import tkinter as tk
from tkinter import ttk

from core.calculator_dispatcher import create_calculator_for_profile
from apps.calculator.ui.auto_calc import DebouncedAutoCalc
from apps.calculator.ui.table.controller import TkTableController
from apps.calculator.ui.layout_constants import ISO_SECTION_BLOCK_GAP, ISO_SECTION_PADX
from apps.calculator.ui.metric_input_table import MetricInputTable
from apps.calculator.ui.profile_resolver import MODE_SASO_T3, resolve_calculation_mode_profile_id
from apps.calculator.ui.sections.bin_detail_panel import BinDetailPanel, BinDetailSource
from apps.calculator.ui.sections.result_formatting import bin_details, metric_value, kwh_value
from apps.calculator.ui.sections.iso_saso_t3_result_table import IsoSasoT3ResultTable
from apps.calculator.ui.batch_dialogs.dialog_handle import BatchDialogHandle
from apps.calculator.ui.batch_dialogs.profiles.saso_t3 import SasoT3BatchDialog

_REQUIRED_TRACE_LABEL = "Required only (3-point)"
_OPTIONAL_TRACE_LABEL = "With 35 Min (4-point)"

_REQUIRED_FIELDS = (
    "full_46_capacity",
    "full_46_power",
    "full_35_capacity",
    "full_35_power",
    "half_35_capacity",
    "half_35_power",
)
_OPTIONAL_FIELDS = (
    "min_35_capacity",
    "min_35_power",
)

_POINTS: tuple[tuple[str, str, str], ...] = (
    ("46_full", "full_46", "46 Full"),
    ("35_full", "full_35", "35 Full"),
    ("35_half", "half_35", "35 Half"),
    ("35_min", "min_35", "35 Min"),
)

class IsoSasoT3Section:
    """SASO T3 input, optional 35 Min toggle, and scenario comparison."""

    def __init__(
        self,
        parent: tk.Widget,
        *,
        on_trace_visibility_changed: Callable[[], None] | None = None,
    ) -> None:
        self._on_detail_visibility_changed = on_trace_visibility_changed
        self._trace_results: dict[str, list[dict]] = {}
        self._detail_summaries: dict[str, tuple[tuple[str, str], ...]] = {}
        self._detail_statuses: dict[str, str] = {}
        self._trace_status: str | None = "상세 데이터 없음"
        self._batch_handle: BatchDialogHandle[
            list[dict[str, str]], SasoT3BatchDialog
        ] = BatchDialogHandle()
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
            row=1, column=0, sticky="w", padx=ISO_SECTION_PADX, pady=(0, 6),
        )

        self.optional_min_enabled = tk.BooleanVar(master=self._frame, value=True)
        self.optional_min_toggle = ttk.Checkbutton(
            self._frame,
            text="",
            variable=self.optional_min_enabled,
            command=self._on_optional_min_toggled,
        )

        self.result_table = IsoSasoT3ResultTable(self._frame)
        self.result_panel = self.result_table
        self.result_table.grid(
            row=3, column=0, sticky="w", padx=ISO_SECTION_PADX,
            pady=(0, ISO_SECTION_BLOCK_GAP),
        )
        self.action_row = ttk.Frame(self._frame)
        self.action_row.grid(
            row=4,
            column=0,
            sticky="w",
            padx=ISO_SECTION_PADX,
            pady=(0, ISO_SECTION_BLOCK_GAP),
        )
        self.batch_button = ttk.Button(
            self.action_row,
            text="Multi 입력",
            command=self._open_batch_dialog,
        )
        self.batch_button.surface_role = "saso_t3_batch_open"
        self.batch_button.pack(side=tk.LEFT)
        self.detail_toggle = ttk.Button(
            self.action_row,
            text="상세 보기 ↓",
            command=self._toggle_detail,
        )
        self.detail_toggle.surface_role = "saso_t3_detail_toggle"
        self.detail_toggle.pack(side=tk.LEFT, padx=(6, 0))
        self._detail_visible = False
        self.detail_panel = BinDetailPanel(
            self._frame,
            source_labels=(_REQUIRED_TRACE_LABEL, _OPTIONAL_TRACE_LABEL),
            default_source=_OPTIONAL_TRACE_LABEL,
            csv_filename="saso_t3_bin_detail.csv",
        )
        self.trace_table = self.detail_panel.table
        self.trace_profile_combo = self.detail_panel.source_combo

        self.input_controller = TkTableController(self.input_table)
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
        required_values = self.input_table.get_text_values()
        if not any(required_values[field].strip() for field in _REQUIRED_FIELDS):
            self._clear_trace("\uc785\ub825 \ub300\uae30")
            self.result_table.set_rows((), status="\uc785\ub825 \ub300\uae30")
            return
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

        trace_results = {_REQUIRED_TRACE_LABEL: required_trace}
        detail_summaries = {_REQUIRED_TRACE_LABEL: _summary_from_row(required_row)}
        detail_statuses: dict[str, str] = {}
        status = "자동 계산 완료"
        optional_measured, optional_error = self._read_optional_inputs(required_measured)
        if optional_error is None:
            optional_row, optional_trace, optional_error = self._calculate_optional_row(
                optional_measured
            )
        else:
            optional_row = ()
            optional_trace = []
        if optional_error is not None:
            rows = [_optional_error_row(optional_error), required_row]
            detail_statuses[_OPTIONAL_TRACE_LABEL] = (
                "상세 데이터 없음: 35 Min 숫자 입력을 확인하세요."
            )
            status = "4-point 입력 오류: 35 Min 숫자 입력을 확인하세요."
        else:
            rows = [optional_row, required_row]
            trace_results[_OPTIONAL_TRACE_LABEL] = optional_trace
            detail_summaries[_OPTIONAL_TRACE_LABEL] = _summary_from_row(optional_row)
        self._trace_results = trace_results
        self._detail_summaries = detail_summaries
        self._detail_statuses = detail_statuses
        self._trace_status = None
        self._update_detail_panel()
        self.result_table.set_rows(tuple(rows), status=status)

    def _read_required_inputs(
        self,
    ) -> tuple[dict[str, dict[str, float]], str | None]:
        try:
            numeric = self.input_table.get_numeric_values(_REQUIRED_FIELDS)
            invalid: dict[str, str] = {}
            for field in _REQUIRED_FIELDS:
                if numeric[field] <= 0:
                    invalid[field] = "양수 입력 필요"
            if invalid:
                current_invalid = self.input_table.invalid_fields()
                current_invalid.update(invalid)
                self.input_table.set_invalid_fields(current_invalid)
                raise ValueError("positivity check failed")
            return {
                "46_full": {
                    "capacity": numeric["full_46_capacity"],
                    "power": numeric["full_46_power"],
                },
                "35_full": {
                    "capacity": numeric["full_35_capacity"],
                    "power": numeric["full_35_power"],
                },
                "35_half": {
                    "capacity": numeric["half_35_capacity"],
                    "power": numeric["half_35_power"],
                },
            }, None
        except ValueError:
            return {}, "입력 오류: 숫자 입력을 확인하세요."

    def _read_optional_inputs(
        self,
        required_measured: Mapping[str, Mapping[str, float]],
    ) -> tuple[dict[str, dict[str, float]], str | None]:
        try:
            numeric = self.input_table.get_numeric_values(_OPTIONAL_FIELDS)
            invalid: dict[str, str] = {}
            for field in _OPTIONAL_FIELDS:
                if numeric[field] <= 0:
                    invalid[field] = "양수 입력 필요"
            if invalid:
                current_invalid = self.input_table.invalid_fields()
                current_invalid.update(invalid)
                self.input_table.set_invalid_fields(current_invalid)
                raise ValueError("positivity check failed")
            measured = {key: dict(value) for key, value in required_measured.items()}
            measured["35_min"] = {
                "capacity": numeric["min_35_capacity"],
                "power": numeric["min_35_power"],
            }
            return measured, None
        except ValueError:
            return {}, "입력 오류"

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
            ), bin_details(result), None
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
            ), bin_details(result), None
        except Exception:
            return (), [], "계산 오류"

    def _on_optional_min_toggled(self) -> None:
        self._sync_optional_min_state()
        self._sync_optional_trace_state()
        self._auto_calc.schedule()

    def _sync_optional_min_state(self) -> None:
        for field_key in ("min_35_capacity", "min_35_power"):
            self.input_table.editable_entries[field_key].configure(state=tk.NORMAL)

    def _sync_optional_trace_state(self) -> None:
        self.optional_min_enabled.set(True)
        self._sync_optional_min_state()

    def _open_batch_dialog(self) -> None:
        self._batch_handle.open_or_focus(
            lambda: SasoT3BatchDialog(
                self._frame.winfo_toplevel(),
                initial_snapshot=self._batch_handle.snapshot,
                on_close=self._clear_batch_dialog,
            )
        )

    def _clear_batch_dialog(self, snapshot: list[dict[str, str]] | None = None) -> None:
        self._batch_handle.clear(snapshot)

    @property
    def _batch_dialog(self) -> SasoT3BatchDialog | None:
        return self._batch_handle.dialog

    @_batch_dialog.setter
    def _batch_dialog(self, dialog: SasoT3BatchDialog | None) -> None:
        self._batch_handle.dialog = dialog

    @property
    def _batch_snapshot(self) -> list[dict[str, str]] | None:
        return self._batch_handle.snapshot

    @_batch_snapshot.setter
    def _batch_snapshot(self, snapshot: list[dict[str, str]] | None) -> None:
        self._batch_handle.snapshot = snapshot

    def _toggle_detail(self) -> None:
        self._detail_visible = not self._detail_visible
        if self._detail_visible:
            self._update_detail_panel()
            self.detail_panel.grid(
                row=5,
                column=0,
                sticky="ew",
                padx=0,
                pady=(0, ISO_SECTION_BLOCK_GAP),
            )
            self.detail_toggle.configure(text="상세 닫기 ↑")
        else:
            self.detail_panel.grid_remove()
            self.detail_toggle.configure(text="상세 보기 ↓")
        if self._on_detail_visibility_changed is not None:
            self._on_detail_visibility_changed()

    def _update_detail_panel(self) -> None:
        if self._trace_status is not None:
            self.detail_panel.set_status(self._trace_status)
            return
        sources = {}
        for label in (_OPTIONAL_TRACE_LABEL, _REQUIRED_TRACE_LABEL):
            if label in self._trace_results:
                sources[label] = BinDetailSource(
                    rows=tuple(self._trace_results[label]),
                    summary=self._detail_summaries.get(label, ()),
                )
            elif label in self._detail_statuses:
                sources[label] = BinDetailSource(status=self._detail_statuses[label])
        self.detail_panel.set_sources(
            sources,
            source_order=(_OPTIONAL_TRACE_LABEL, _REQUIRED_TRACE_LABEL),
            panel_status="상세 데이터 없음",
        )

    def _clear_trace(self, status: str) -> None:
        self._trace_results = {}
        self._detail_summaries = {}
        self._detail_statuses = {}
        self._trace_status = status
        self._update_detail_panel()

    def _copy_result_table(self) -> bool:
        return self.result_table.copy_table()

    def _on_destroy(self, event: tk.Event) -> None:
        if event.widget is self._frame:
            self._auto_calc.dispose()
            self._batch_handle.dispose()



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
        metric_value(result, "cspf"),
        kwh_value(result, ("annual_cooling_kwh", "cstl_kwh", "cstl")),
        kwh_value(result, ("annual_power_kwh", "csec_kwh", "csec")),
    )


def _optional_error_row(message: str) -> tuple[str, ...]:
    return ("With 35 Min (4-point)", "-", "-", "-", message, "-", "-", "-")


def _summary_from_row(row: tuple[str, ...]) -> tuple[tuple[str, str], ...]:
    return (
        ("CSPF", row[5]),
        ("CSTL [kWh]", row[6]),
        ("CSEC [kWh]", row[7]),
    )


def _eer_value(measured: Mapping[str, Mapping[str, float]], point_key: str) -> str:
    point = measured.get(point_key, {})
    capacity = point.get("capacity")
    power = point.get("power")
    if capacity is None or power is None or power <= 0:
        return "-"
    return f"{capacity / power:.2f}"
