"""ISO 16358-2 HSPF table input section for the Tkinter calculator.

Defaults mirror the feasibility MVP so Hong Kong HSPF = 3.643 is preserved.
"""

from __future__ import annotations

from typing import Callable, Mapping

import tkinter as tk
from tkinter import ttk

from core.calculator_dispatcher import create_calculator_for_profile
from ui_tk.auto_calc import DebouncedAutoCalc
from ui_tk.metric_input_table import MetricInputTable
from ui_tk.profile_resolver import resolve_profile_id
from ui_tk.result_models import ResultSummary, result_status
from ui_tk.sections.iso16358_helpers import build_hspf_input
from ui_tk.sections.result_formatting import summarize_hspf_result


class IsoHspfSection:
    """Hong Kong HSPF table input with debounced automatic calculation."""

    def __init__(
        self,
        parent: tk.Widget,
        region_label: str,
        result_callback: Callable[[ResultSummary], None],
    ) -> None:
        self._region_label = region_label
        self._result_callback = result_callback
        self._frame = ttk.LabelFrame(parent, text=f"HSPF ({region_label})")

        self.input_table = MetricInputTable(
            self._frame,
            columns=(
                ("rated", "정격 난방"),
                ("full", "7 Full"),
                ("half", "7 Half"),
            ),
            rows=(("capacity", "능력 [W]"), ("power", "전력 [W]")),
            editable_cells={
                ("capacity", "rated"): "rated_heating_capacity",
                ("capacity", "full"): "full_capacity",
                ("power", "full"): "full_power",
                ("capacity", "half"): "half_capacity",
                ("power", "half"): "half_power",
            },
        )
        self.input_table.grid(row=0, column=0, sticky="w", padx=10, pady=8)
        self.input_table.set_values(
            {
                "rated_heating_capacity": "6300",
                "full_capacity": "6300",
                "full_power": "1500",
                "half_capacity": "3200",
                "half_power": "800",
            }
        )
        self._auto_calc = DebouncedAutoCalc(self._frame, self.recalculate_now)
        self.input_table.set_values_changed_callback(self._auto_calc.schedule)
        self._frame.bind("<Destroy>", self._on_destroy, add="+")
        self._auto_calc.schedule()

    def pack(self, **kwargs) -> None:
        self._frame.pack(**kwargs)

    def _read_inputs(self) -> Mapping[str, object]:
        values = self.input_table.get_numeric_values()
        return build_hspf_input(
            rated_heating_capacity=values["rated_heating_capacity"],
            full_capacity=values["full_capacity"],
            full_power=values["full_power"],
            half_capacity=values["half_capacity"],
            half_power=values["half_power"],
        )

    def recalculate_now(self) -> None:
        try:
            measured = self._read_inputs()
        except ValueError:
            self._result_callback(result_status("HSPF", "입력 오류: 숫자 입력을 확인하세요."))
            return
        try:
            profile_id = resolve_profile_id(self._region_label, "HSPF")
            calc = create_calculator_for_profile(profile_id=profile_id)
            result = calc.calculate_hspf(measured)
        except Exception as exc:
            self._result_callback(
                result_status("HSPF", f"오류: {type(exc).__name__}: {exc}")
            )
            return
        self._result_callback(summarize_hspf_result(result))

    def _on_destroy(self, event: tk.Event) -> None:
        if event.widget is self._frame:
            self._auto_calc.dispose()
