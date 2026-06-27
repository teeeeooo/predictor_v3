"""Hong Kong HSPF table input section for the Tkinter calculator.

Defaults mirror the feasibility MVP so Hong Kong HSPF = 3.643 is preserved.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Mapping

import tkinter as tk
from tkinter import ttk

from core.calculator_dispatcher import create_calculator_for_profile
from apps.calculator.ui.auto_calc import DebouncedAutoCalc
from apps.calculator.ui.batch_dialogs.dialog_handle import BatchDialogHandle
from apps.calculator.ui.batch_dialogs.profiles.hong_kong_hspf import (
    HongKongHspfBatchDialog,
)
from apps.calculator.ui.table.controller import TkTableController
from apps.calculator.ui.layout_constants import (
    BATCH_INPUT_BUTTON_TEXT,
    ISO_SECTION_BLOCK_GAP,
    ISO_SECTION_PADX,
)
from apps.calculator.ui.metric_input_table import MetricInputTable
from apps.calculator.ui.profile_resolver import resolve_profile_id
from apps.calculator.ui.result_models import result_status
from apps.calculator.ui.result_panel import ResultPanel
from apps.calculator.ui.sections.bin_detail_panel import BinDetailPanel, BinDetailSource
from apps.calculator.ui.sections.bin_detail_schema import HEATING_HSPF_BIN_DETAIL_SCHEMA
from apps.calculator.ui.sections.detail_visibility import DetailPanelVisibility
from apps.calculator.ui.sections.iso16358_helpers import build_hspf_input
from apps.calculator.ui.sections.result_formatting import summarize_hspf_result


class HongKongHspfSection:
    """Hong Kong HSPF table input with debounced automatic calculation."""

    def __init__(
        self,
        parent: tk.Widget,
        region_label: str,
        *,
        on_trace_visibility_changed: Callable[[], None] | None = None,
    ) -> None:
        self._region_label = region_label
        self._on_detail_visibility_changed = on_trace_visibility_changed
        self._trace_rows: list[dict] = []
        self._detail_summary: tuple[tuple[str, str], ...] = ()
        self._trace_status: str | None = "상세 데이터 없음"
        self._batch_handle: BatchDialogHandle[
            list[dict[str, str]], HongKongHspfBatchDialog
        ] = BatchDialogHandle()
        self._frame = ttk.LabelFrame(parent, text=f"HSPF 입력 ({region_label})")
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
                ("full", "7 Full"),
                ("half", "7 Half"),
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
        self.result_panel = ResultPanel(self._frame, title="HSPF 결과")
        self.result_panel.grid(
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
        self.batch_button.surface_role = "hong_kong_hspf_batch_open"
        self.batch_button.pack(side=tk.LEFT)
        self.detail_toggle = ttk.Button(
            self.action_row,
            text="상세 보기 ↓",
            command=self._toggle_detail,
        )
        self.detail_toggle.surface_role = "hong_kong_hspf_detail_toggle"
        self.detail_toggle.pack(side=tk.LEFT, padx=(6, 0))
        self.detail_panel = BinDetailPanel(
            self._frame,
            source_labels=("Hong Kong HSPF",),
            default_source="Hong Kong HSPF",
            csv_filename="hong_kong_hspf_bin_detail.csv",
            show_source_selector=False,
            schema=HEATING_HSPF_BIN_DETAIL_SCHEMA,
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
        self.input_controller = TkTableController(self.input_table)
        self._auto_calc = DebouncedAutoCalc(self._frame, self.recalculate_now)
        self.input_table.set_values_changed_callback(self._auto_calc.schedule)
        self._frame.bind("<Destroy>", self._on_destroy, add="+")
        self._auto_calc.flush_now()

    def pack(self, **kwargs) -> None:
        self._frame.pack(**kwargs)

    @property
    def _batch_dialog(self) -> HongKongHspfBatchDialog | None:
        return self._batch_handle.dialog

    @_batch_dialog.setter
    def _batch_dialog(self, dialog: HongKongHspfBatchDialog | None) -> None:
        self._batch_handle.dialog = dialog

    @property
    def _batch_snapshot(self) -> list[dict[str, str]] | None:
        return self._batch_handle.snapshot

    @_batch_snapshot.setter
    def _batch_snapshot(self, snapshot: list[dict[str, str]] | None) -> None:
        self._batch_handle.snapshot = snapshot

    def _open_batch_dialog(self) -> None:
        self._batch_handle.open_or_focus(
            lambda: HongKongHspfBatchDialog(
                self._frame.winfo_toplevel(),
                self._region_label,
                initial_snapshot=self._batch_handle.snapshot,
                on_close=self._clear_batch_dialog,
            )
        )

    def _clear_batch_dialog(self, snapshot: list[dict[str, str]] | None = None) -> None:
        self._batch_handle.clear(snapshot)

    def _read_inputs(self) -> Mapping[str, object]:
        values = self.input_table.get_numeric_values()
        return build_hspf_input(
            full_capacity=values["full_capacity"],
            full_power=values["full_power"],
            half_capacity=values["half_capacity"],
            half_power=values["half_power"],
        )

    def recalculate_now(self) -> None:
        if not any(
            value.strip() for value in self.input_table.get_text_values().values()
        ):
            self._clear_trace("\uc785\ub825 \ub300\uae30")
            self.result_panel.set_summaries(
                (result_status("HSPF", "\uc785\ub825 \ub300\uae30"),)
            )
            return
        try:
            measured = self._read_inputs()
        except ValueError:
            self._clear_trace("입력 오류: 숫자 입력을 확인하세요.")
            self.result_panel.set_summaries(
                (result_status("HSPF", "입력 오류: 숫자 입력을 확인하세요."),)
            )
            return
        try:
            profile_id = resolve_profile_id(self._region_label, "HSPF")
            calc = create_calculator_for_profile(profile_id=profile_id)
            result = calc.calculate_hspf(measured)
        except Exception as exc:
            self._clear_trace("계산 오류")
            self.result_panel.set_summaries(
                (result_status("HSPF", f"오류: {type(exc).__name__}: {exc}"),)
            )
            return
        self._trace_rows = _hspf_bin_details(result)
        self._detail_summary = _hspf_summary_from_result(result)
        self._trace_status = None
        self._update_detail_panel()
        self.result_panel.set_summaries((summarize_hspf_result(result),))

    def _toggle_detail(self) -> None:
        self._detail_visibility.toggle()

    def _update_detail_panel(self) -> None:
        if self._trace_status is not None:
            self.detail_panel.set_status(self._trace_status)
            return
        self.detail_panel.set_sources(
            {
                "Hong Kong HSPF": BinDetailSource(
                    rows=tuple(self._trace_rows),
                    summary=self._detail_summary,
                )
            },
            source_order=("Hong Kong HSPF",),
            panel_status="상세 데이터 없음",
        )

    def _clear_trace(self, status: str) -> None:
        self._trace_rows = []
        self._detail_summary = ()
        self._trace_status = status
        self._update_detail_panel()

    def _on_destroy(self, event: tk.Event) -> None:
        if event.widget is self._frame:
            self._batch_handle.dispose()
            self._auto_calc.dispose()


def _hspf_bin_details(result: Mapping[str, object]) -> list[dict]:
    raw = result.get("bin_details")
    if not isinstance(raw, list):
        return []
    return [dict(item) for item in raw if isinstance(item, Mapping)]


def _hspf_summary_from_result(result: Mapping[str, object]) -> tuple[tuple[str, str], ...]:
    hspf = result.get("hspf")
    hspf_text = "-" if hspf is None else f"{float(hspf):.3f}"
    hstl = result.get("hstl_wh", result.get("hstl"))
    hstl_text = "-"
    if hstl is not None:
        try:
            hstl_text = f"{float(hstl) / 1000.0:.1f}"
        except (TypeError, ValueError):
            hstl_text = str(hstl)
    hsec = result.get("hsec_wh", result.get("hsec"))
    hsec_text = "-"
    if hsec is not None:
        try:
            hsec_text = f"{float(hsec) / 1000.0:.1f}"
        except (TypeError, ValueError):
            hsec_text = str(hsec)
    return (
        ("HSPF", hspf_text),
        ("HSTL [kWh]", hstl_text),
        ("HSEC [kWh]", hsec_text),
    )
