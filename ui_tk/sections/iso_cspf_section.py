"""ISO 16358-1 CSPF table input section for the Tkinter calculator.

Defaults mirror the feasibility MVP so Hong Kong CSPF = 4.939 is preserved.
"""

from __future__ import annotations

from typing import Callable, Mapping, Tuple

import tkinter as tk
from tkinter import ttk

from core.calculator_dispatcher import create_calculator_for_profile
from ui_tk.auto_calc import DebouncedAutoCalc
from ui_tk.profile_resolver import resolve_profile_id
from ui_tk.sections.iso16358_helpers import build_cspf_input, format_cspf_result
from ui_tk.table_grid import TableGrid
from ui_tk.table_grid_model import GridColumn, GridRow


class IsoCspfSection:
    """Hong Kong CSPF table input with debounced automatic calculation."""

    def __init__(
        self,
        parent: tk.Widget,
        region_label: str,
        result_callback: Callable[[str], None],
    ) -> None:
        self._region_label = region_label
        self._result_callback = result_callback
        self._frame = ttk.LabelFrame(parent, text=f"CSPF ({region_label})")

        self.declared_grid = TableGrid(
            self._frame,
            rows=(GridRow("declared", "정격"),),
            columns=(GridColumn("capacity_w", "능력 [W]"),),
        )
        self.declared_grid.grid(row=0, column=0, sticky="w", padx=4, pady=2)
        self.points_grid = TableGrid(
            self._frame,
            rows=(GridRow("35_full", "35_full"), GridRow("35_half", "35_half")),
            columns=(
                GridColumn("capacity_w", "능력 [W]"),
                GridColumn("power_w", "전력 [W]"),
            ),
        )
        self.points_grid.grid(row=1, column=0, sticky="w", padx=4, pady=2)

        self.declared_grid.set_cell("declared", "capacity_w", "3500")
        self.points_grid.set_cells(
            {
                ("35_full", "capacity_w"): "3600",
                ("35_full", "power_w"): "900",
                ("35_half", "capacity_w"): "1700",
                ("35_half", "power_w"): "380",
            }
        )
        self._auto_calc = DebouncedAutoCalc(self._frame, self.recalculate_now)
        self.declared_grid.set_values_changed_callback(self._auto_calc.schedule)
        self.points_grid.set_values_changed_callback(self._auto_calc.schedule)
        self._frame.bind("<Destroy>", self._on_destroy, add="+")
        self._auto_calc.schedule()

    def pack(self, **kwargs) -> None:
        self._frame.pack(**kwargs)

    def _read_inputs(self) -> Tuple[Mapping[str, Mapping[str, float]], float]:
        declared = self.declared_grid.get_numeric_table()
        points = self.points_grid.get_numeric_table()
        return build_cspf_input(
            full_capacity=points["35_full"]["capacity_w"],
            full_power=points["35_full"]["power_w"],
            half_capacity=points["35_half"]["capacity_w"],
            half_power=points["35_half"]["power_w"],
            declared_capacity=declared["declared"]["capacity_w"],
        )

    def recalculate_now(self) -> None:
        try:
            measured, declared = self._read_inputs()
        except ValueError:
            self._result_callback("[CSPF 입력 오류] 숫자 입력을 확인하세요.")
            return
        try:
            profile_id = resolve_profile_id(self._region_label, "CSPF")
            calc = create_calculator_for_profile(profile_id=profile_id)
            result = calc.calculate_cspf(measured, declared_capacity=declared)
        except Exception as exc:
            self._result_callback(f"[CSPF 오류] {type(exc).__name__}: {exc}")
            return
        self._result_callback(format_cspf_result(result))

    def _on_destroy(self, event: tk.Event) -> None:
        if event.widget is self._frame:
            self._auto_calc.dispose()
