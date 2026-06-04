"""Hong Kong CSPF table input section for the Tkinter calculator.

Defaults mirror the feasibility MVP so Hong Kong CSPF = 4.939 is preserved.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Tuple

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
from ui_tk.profile_resolver import resolve_profile_id
from ui_tk.result_models import result_status
from ui_tk.result_panel import ResultPanel
from ui_tk.sections.bin_detail_panel import BinDetailPanel, BinDetailSource
from ui_tk.sections.hong_kong_cspf_batch_section import HongKongCspfBatchDialog
from ui_tk.sections.iso16358_helpers import build_cspf_input
from ui_tk.sections.result_formatting import summarize_cspf_result


class HongKongCspfSection:
    """Hong Kong CSPF table input with debounced automatic calculation."""

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
        self._batch_dialog: HongKongCspfBatchDialog | None = None
        self._frame = ttk.LabelFrame(parent, text=f"CSPF 입력 ({region_label})")
        self._frame.columnconfigure(0, weight=1)

        self.rated_table = MetricInputTable(
            self._frame,
            columns=(("capacity", "능력 [W]"),),
            rows=(("rated", "정격 표기치"),),
            editable_cells={("rated", "capacity"): "declared_capacity"},
        )
        self.rated_table.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=ISO_SECTION_PADX,
            pady=(ISO_SECTION_BLOCK_GAP, 6),
        )
        ttk.Label(self._frame, text="시험 입력").grid(
            row=1, column=0, sticky="w", padx=ISO_SECTION_PADX, pady=(0, 4)
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
            row=2,
            column=0,
            sticky="ew",
            padx=ISO_SECTION_PADX,
            pady=(0, ISO_SECTION_BLOCK_GAP),
        )
        self.result_panel = ResultPanel(self._frame, title="CSPF 결과")
        self.result_panel.grid(
            row=3,
            column=0,
            sticky="ew",
            padx=ISO_SECTION_PADX,
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
        self.batch_button.surface_role = "hong_kong_cspf_batch_open"
        self.batch_button.pack(side=tk.LEFT)
        self.detail_toggle = ttk.Button(
            self.action_row,
            text="상세 보기 ↓",
            command=self._toggle_detail,
        )
        self.detail_toggle.surface_role = "hong_kong_cspf_detail_toggle"
        self.detail_toggle.pack(side=tk.LEFT, padx=(6, 0))
        self._detail_visible = False
        self.detail_panel = BinDetailPanel(
            self._frame,
            source_labels=("Hong Kong CSPF",),
            default_source="Hong Kong CSPF",
            csv_filename="hong_kong_cspf_bin_detail.csv",
            show_source_selector=False,
        )
        self.trace_table = self.detail_panel.table
        self.rated_table.set_values({"declared_capacity": "3500"})
        self.input_table.set_values(
            {
                "full_capacity": "3600",
                "full_power": "900",
                "half_capacity": "1700",
                "half_power": "380",
            }
        )
        self.rated_controller = ExcelLikeTableController(self.rated_table)
        self.input_controller = ExcelLikeTableController(self.input_table)
        self._auto_calc = DebouncedAutoCalc(self._frame, self.recalculate_now)
        self.rated_table.set_values_changed_callback(self._auto_calc.schedule)
        self.input_table.set_values_changed_callback(self._auto_calc.schedule)
        self._frame.bind("<Destroy>", self._on_destroy, add="+")
        self._auto_calc.flush_now()

    def pack(self, **kwargs) -> None:
        self._frame.pack(**kwargs)

    def _open_batch_dialog(self) -> None:
        if self._batch_dialog is not None and self._batch_dialog.window.winfo_exists():
            self._batch_dialog.focus()
            return
        self._batch_dialog = HongKongCspfBatchDialog(
            self._frame.winfo_toplevel(),
            self._region_label,
            on_close=self._clear_batch_dialog,
        )

    def _clear_batch_dialog(self) -> None:
        self._batch_dialog = None

    def _read_inputs(self) -> Tuple[Mapping[str, Mapping[str, float]], float]:
        values = self.input_table.get_numeric_values()
        rated_values = self.rated_table.get_numeric_values()
        return build_cspf_input(
            full_capacity=values["full_capacity"],
            full_power=values["full_power"],
            half_capacity=values["half_capacity"],
            half_power=values["half_power"],
            declared_capacity=rated_values["declared_capacity"],
        )

    def recalculate_now(self) -> None:
        try:
            measured, declared = self._read_inputs()
        except ValueError:
            self._clear_trace("입력 오류: 숫자 입력을 확인하세요.")
            self.result_panel.set_summaries(
                (result_status("CSPF", "입력 오류: 숫자 입력을 확인하세요."),)
            )
            return
        try:
            profile_id = resolve_profile_id(self._region_label, "CSPF")
            calc = create_calculator_for_profile(profile_id=profile_id)
            result = calc.calculate_cspf(measured, declared_capacity=declared)
        except Exception as exc:
            self._clear_trace("계산 오류")
            self.result_panel.set_summaries(
                (result_status("CSPF", f"오류: {type(exc).__name__}: {exc}"),)
            )
            return
        self._trace_rows = _bin_details(result)
        self._detail_summary = _summary_from_result(result)
        self._trace_status = None
        self._update_detail_panel()
        self.result_panel.set_summaries((summarize_cspf_result(result),))

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
        self.detail_panel.set_sources(
            {
                "Hong Kong CSPF": BinDetailSource(
                    rows=tuple(self._trace_rows),
                    summary=self._detail_summary,
                )
            },
            source_order=("Hong Kong CSPF",),
            panel_status="상세 데이터 없음",
        )

    def _clear_trace(self, status: str) -> None:
        self._trace_rows = []
        self._detail_summary = ()
        self._trace_status = status
        self._update_detail_panel()

    def _on_destroy(self, event: tk.Event) -> None:
        if event.widget is self._frame:
            self._auto_calc.dispose()
            if self._batch_dialog is not None:
                self._batch_dialog.close()
                self._batch_dialog = None


def _bin_details(result: Mapping[str, object]) -> list[dict]:
    raw = result.get("bin_details")
    if not isinstance(raw, list):
        return []
    return [dict(item) for item in raw if isinstance(item, Mapping)]


def _summary_from_result(result: Mapping[str, object]) -> tuple[tuple[str, str], ...]:
    return (
        ("CSPF", _number_text(result.get("cspf"), 3)),
        ("CSTL [kWh]", _number_text(_first_value(result, ("annual_cooling_kwh",)), 1)),
        ("CSEC [kWh]", _number_text(_first_value(result, ("annual_power_kwh",)), 1)),
    )


def _first_value(result: Mapping[str, object], keys: tuple[str, ...]) -> object:
    for key in keys:
        value = result.get(key)
        if value is not None:
            return value
    return None


def _number_text(value: object, decimals: int) -> str:
    if value is None:
        return "-"
    try:
        return f"{float(value):.{decimals}f}"
    except (TypeError, ValueError):
        return str(value)
