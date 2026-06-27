"""ISO/ISEER 2-point single calculation section for Tkinter."""

from __future__ import annotations

from collections.abc import Callable, Mapping

import tkinter as tk
from tkinter import ttk

from core.calculators.dispatcher import create_calculator_for_profile
from apps.calculator.ui.auto_calc import DebouncedAutoCalc
from apps.calculator.ui.table.controller import TkTableController
from apps.calculator.ui.layout_constants import (
    BATCH_INPUT_BUTTON_TEXT,
    ISO_SECTION_BLOCK_GAP,
    ISO_SECTION_PADX,
)
from apps.calculator.ui.metric_input_table import MetricInputTable
from apps.calculator.ui.profile_resolver import (
    resolve_two_point_profile_id,
    two_point_profile_labels,
)
from apps.calculator.ui.sections.bin_detail_panel import BinDetailPanel, BinDetailSource
from apps.calculator.ui.sections.detail_visibility import DetailPanelVisibility
from apps.calculator.ui.sections.result_formatting import bin_details, metric_value, kwh_value
from apps.calculator.ui.sections.iso_iseer_2point_result_table import (
    IsoIseer2PointResultTable,
)
from apps.calculator.ui.batch_dialogs.dialog_handle import BatchDialogHandle
from apps.calculator.ui.batch_dialogs.profiles.iso_iseer_2point import IsoIseer2PointBatchDialog


class IsoIseer2PointSection:
    """ISO 16358-1 and India ISEER 2-point input with auto-calc."""

    def __init__(
        self,
        parent: tk.Widget,
        *,
        on_trace_visibility_changed: Callable[[], None] | None = None,
    ) -> None:
        self._on_detail_visibility_changed = on_trace_visibility_changed
        self._trace_results: dict[str, list[dict]] = {}
        self._detail_summaries: dict[str, tuple[tuple[str, str], ...]] = {}
        self._trace_status: str | None = "상세 데이터 없음"
        self._batch_handle: BatchDialogHandle[
            list[dict[str, str]], IsoIseer2PointBatchDialog
        ] = BatchDialogHandle()
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
            sticky="w",
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
            sticky="w",
            padx=ISO_SECTION_PADX,
            pady=(0, ISO_SECTION_BLOCK_GAP),
        )
        self.action_row = ttk.Frame(self._frame)
        self.action_row.grid(
            row=3,
            column=0,
            sticky="w",
            padx=ISO_SECTION_PADX,
            pady=(0, ISO_SECTION_BLOCK_GAP),
        )
        self.batch_button = ttk.Button(
            self.action_row,
            text=BATCH_INPUT_BUTTON_TEXT,
            command=self._open_batch_dialog,
        )
        self.batch_button.surface_role = "iso_iseer_2point_batch_open"
        self.batch_button.pack(side=tk.LEFT)
        self.detail_toggle = ttk.Button(
            self.action_row,
            text="상세 보기 ↓",
            command=self._toggle_detail,
        )
        self.detail_toggle.surface_role = "two_point_detail_toggle"
        self.detail_toggle.pack(side=tk.LEFT, padx=(6, 0))
        self.detail_panel = BinDetailPanel(
            self._frame,
            source_labels=tuple(two_point_profile_labels()),
            default_source=two_point_profile_labels()[0],
            csv_filename="iso_iseer_bin_detail.csv",
        )
        self._detail_visibility = DetailPanelVisibility(
            panel=self.detail_panel,
            button=self.detail_toggle,
            grid_options={
                "row": 4,
                "column": 0,
                "sticky": "ew",
                "padx": 0,
                "pady": (0, ISO_SECTION_BLOCK_GAP),
            },
            before_show=self._update_detail_panel,
            on_change=lambda: self._on_detail_visibility_changed()
            if self._on_detail_visibility_changed is not None
            else None,
        )
        self.trace_table = self.detail_panel.table
        self.trace_profile_combo = self.detail_panel.source_combo
        self.input_controller = TkTableController(self.input_table)
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
        if not any(
            value.strip() for value in self.input_table.get_text_values().values()
        ):
            self._clear_trace("\uc785\ub825 \ub300\uae30")
            self.result_table.set_rows((), status="\uc785\ub825 \ub300\uae30")
            return
        try:
            measured = self._read_inputs()
        except ValueError:
            self._clear_trace("입력 오류: 숫자 입력을 확인하세요.")
            self.result_table.set_status("입력 오류: 숫자 입력을 확인하세요.")
            return

        rows = []
        trace_results = {}
        detail_summaries = {}
        errors = []
        for profile_label in two_point_profile_labels():
            try:
                profile_id = resolve_two_point_profile_id(profile_label)
                calc = create_calculator_for_profile(profile_id=profile_id)
                result = calc.calculate_cspf(measured)
                row = _two_point_result_row(profile_label, measured, result)
                rows.append(row)
                trace_results[profile_label] = bin_details(result)
                detail_summaries[profile_label] = _summary_from_row(row)
            except Exception as exc:
                errors.append(f"{profile_label}: {type(exc).__name__}: {exc}")
        if errors:
            self._clear_trace("계산 오류")
            self.result_table.set_status("오류: " + " / ".join(errors))
            return
        self._trace_results = trace_results
        self._detail_summaries = detail_summaries
        self._trace_status = None
        if self.detail_panel.selected_source() not in self._trace_results:
            self.trace_profile_combo.set(two_point_profile_labels()[0])
        self._update_detail_panel()
        self.result_table.set_rows(tuple(rows), status="자동 계산 완료")

    def _open_batch_dialog(self) -> None:
        self._batch_handle.open_or_focus(
            lambda: IsoIseer2PointBatchDialog(
                self._frame.winfo_toplevel(),
                initial_snapshot=self._batch_handle.snapshot,
                on_close=self._clear_batch_dialog,
            )
        )

    def _clear_batch_dialog(self, snapshot: list[dict[str, str]] | None = None) -> None:
        self._batch_handle.clear(snapshot)

    @property
    def _batch_dialog(self) -> IsoIseer2PointBatchDialog | None:
        return self._batch_handle.dialog

    @_batch_dialog.setter
    def _batch_dialog(self, dialog: IsoIseer2PointBatchDialog | None) -> None:
        self._batch_handle.dialog = dialog

    @property
    def _batch_snapshot(self) -> list[dict[str, str]] | None:
        return self._batch_handle.snapshot

    @_batch_snapshot.setter
    def _batch_snapshot(self, snapshot: list[dict[str, str]] | None) -> None:
        self._batch_handle.snapshot = snapshot

    def _toggle_detail(self) -> None:
        self._detail_visibility.toggle()

    def _update_detail_panel(self) -> None:
        if self._trace_status is not None:
            self.detail_panel.set_status(self._trace_status)
            return
        sources = {
            label: BinDetailSource(
                rows=tuple(rows),
                summary=self._detail_summaries.get(label, ()),
            )
            for label, rows in self._trace_results.items()
        }
        self.detail_panel.set_sources(
            sources,
            source_order=tuple(two_point_profile_labels()),
            panel_status="상세 데이터 없음",
        )

    def _clear_trace(self, status: str) -> None:
        self._trace_results = {}
        self._detail_summaries = {}
        self._trace_status = status
        self._update_detail_panel()

    def _copy_result_table(self) -> bool:
        return self.result_table.copy_table()

    def _on_destroy(self, event: tk.Event) -> None:
        if event.widget is self._frame:
            self._auto_calc.dispose()
            self._batch_handle.dispose()


def _two_point_result_row(
    title: str,
    measured: Mapping[str, Mapping[str, float]],
    result: Mapping[str, object],
) -> tuple[str, ...]:
    return (
        title,
        _eer_value(measured, "35_full"),
        _eer_value(measured, "35_half"),
        metric_value(result, "cspf"),
        kwh_value(result, ("annual_cooling_kwh", "cstl_kwh", "cstl")),
        kwh_value(result, ("annual_power_kwh", "csec_kwh", "csec")),
    )


def _summary_from_row(row: tuple[str, ...]) -> tuple[tuple[str, str], ...]:
    return (
        ("CSPF/ISEER", row[3]),
        ("CSTL [kWh]", row[4]),
        ("CSEC [kWh]", row[5]),
    )


def _eer_value(measured: Mapping[str, Mapping[str, float]], point_key: str) -> str:
    point = measured.get(point_key, {})
    capacity = point.get("capacity")
    power = point.get("power")
    if capacity is None or power is None or power <= 0:
        return "-"
    return f"{capacity / power:.2f}"
