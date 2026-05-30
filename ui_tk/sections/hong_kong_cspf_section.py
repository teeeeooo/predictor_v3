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
from ui_tk import table_csv_export
from ui_tk.layout_constants import (
    ISO_SECTION_BLOCK_GAP,
    ISO_SECTION_PADX,
)
from ui_tk.metric_input_table import MetricInputTable
from ui_tk.profile_resolver import resolve_profile_id
from ui_tk.result_models import result_status
from ui_tk.result_panel import ResultPanel
from ui_tk.sections.bin_trace_table import BinTraceTable
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
        self._on_trace_visibility_changed = on_trace_visibility_changed
        self._trace_rows: list[dict] = []
        self._trace_status: str | None = "Trace data not available"
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
        self._trace_visible = tk.BooleanVar(master=self._frame, value=False)
        self._trace_controls = ttk.Frame(self._frame)
        self._trace_controls.grid(
            row=4,
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
        self.trace_toggle.surface_role = "hong_kong_cspf_bin_trace_toggle"
        self.trace_toggle.pack(side=tk.LEFT)
        self.trace_csv_button = ttk.Button(
            self._trace_controls,
            text="Trace CSV 내보내기",
            command=self._export_trace_csv,
        )
        self.trace_csv_button.surface_role = "hong_kong_cspf_trace_csv_export"
        self.trace_csv_button.pack(side=tk.LEFT, padx=(6, 0))
        self.trace_copy_button = ttk.Button(
            self._trace_controls,
            text="Trace 복사",
            command=self._copy_trace_table,
        )
        self.trace_copy_button.surface_role = "hong_kong_cspf_trace_copy"
        self.trace_copy_button.pack(side=tk.LEFT, padx=(6, 0))
        self.trace_table = BinTraceTable(self._frame)
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
        self._trace_status = None
        self._update_trace_table()
        self.result_panel.set_summaries((summarize_cspf_result(result),))

    def _on_trace_toggled(self) -> None:
        if self._trace_visible.get():
            self._update_trace_table()
            self.trace_table.grid(
                row=5,
                column=0,
                sticky="ew",
                padx=ISO_SECTION_PADX,
                pady=(0, ISO_SECTION_BLOCK_GAP),
            )
        else:
            self.trace_table.grid_remove()
        if self._on_trace_visibility_changed is not None:
            self._on_trace_visibility_changed()

    def _update_trace_table(self) -> None:
        if self._trace_status is not None:
            self.trace_table.set_status(self._trace_status)
            return
        self.trace_table.set_data(self._trace_rows)

    def _clear_trace(self, status: str) -> None:
        self._trace_rows = []
        self._trace_status = status
        self._update_trace_table()

    def _export_trace_csv(self) -> bool:
        self._update_trace_table()
        headers, rows = self.trace_table.table_export_data()
        return table_csv_export.export_table_to_csv(
            self._frame, "hong_kong_cspf_bin_trace.csv", headers, rows
        )

    def _copy_trace_table(self) -> bool:
        self._update_trace_table()
        return self.trace_table.copy_table()

    def _on_destroy(self, event: tk.Event) -> None:
        if event.widget is self._frame:
            self._auto_calc.dispose()


def _bin_details(result: Mapping[str, object]) -> list[dict]:
    raw = result.get("bin_details")
    if not isinstance(raw, list):
        return []
    return [dict(item) for item in raw if isinstance(item, Mapping)]
