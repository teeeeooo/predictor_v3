"""ISO 16358-2 HSPF table input section for the Tkinter calculator.

Defaults mirror the feasibility MVP so Hong Kong HSPF = 3.643 is preserved.
"""

from __future__ import annotations

from typing import Callable, Mapping

import tkinter as tk
from tkinter import ttk

from core.calculator_dispatcher import create_calculator_for_profile
from ui_tk.auto_calc import DebouncedAutoCalc
from ui_tk.profile_resolver import resolve_profile_id
from ui_tk.sections.iso16358_helpers import build_hspf_input, format_hspf_result
from ui_tk.table_grid import TableGrid
from ui_tk.table_grid_model import GridColumn, GridRow


class IsoHspfSection:
    """Hong Kong HSPF table input with debounced automatic calculation."""

    def __init__(
        self,
        parent: tk.Widget,
        region_label: str,
        result_callback: Callable[[str], None],
    ) -> None:
        self._region_label = region_label
        self._result_callback = result_callback
        self._frame = ttk.LabelFrame(parent, text=f"HSPF ({region_label})")

        self.rated_grid = TableGrid(
            self._frame,
            rows=(GridRow("rated", "정격 난방"),),
            columns=(GridColumn("capacity_w", "능력 [W]"),),
        )
        self.rated_grid.grid(row=0, column=0, sticky="w", padx=4, pady=2)
        self.points_grid = TableGrid(
            self._frame,
            rows=(GridRow("7_full", "7_full"), GridRow("7_half", "7_half")),
            columns=(
                GridColumn("capacity_w", "능력 [W]"),
                GridColumn("power_w", "전력 [W]"),
            ),
        )
        self.points_grid.grid(row=1, column=0, sticky="w", padx=4, pady=2)

        self.rated_grid.set_cell("rated", "capacity_w", "6300")
        self.points_grid.set_cells(
            {
                ("7_full", "capacity_w"): "6300",
                ("7_full", "power_w"): "1500",
                ("7_half", "capacity_w"): "3200",
                ("7_half", "power_w"): "800",
            }
        )
        self._auto_calc = DebouncedAutoCalc(self._frame, self.recalculate_now)
        self.rated_grid.set_values_changed_callback(self._auto_calc.schedule)
        self.points_grid.set_values_changed_callback(self._auto_calc.schedule)
        self._frame.bind("<Destroy>", self._on_destroy, add="+")
        self._auto_calc.schedule()

    def pack(self, **kwargs) -> None:
        self._frame.pack(**kwargs)

    def _read_inputs(self) -> Mapping[str, object]:
        rated = self.rated_grid.get_numeric_table()
        points = self.points_grid.get_numeric_table()
        return build_hspf_input(
            rated_heating_capacity=rated["rated"]["capacity_w"],
            full_capacity=points["7_full"]["capacity_w"],
            full_power=points["7_full"]["power_w"],
            half_capacity=points["7_half"]["capacity_w"],
            half_power=points["7_half"]["power_w"],
        )

    def recalculate_now(self) -> None:
        try:
            measured = self._read_inputs()
        except ValueError:
            self._result_callback("[HSPF 입력 오류] 숫자 입력을 확인하세요.")
            return
        try:
            profile_id = resolve_profile_id(self._region_label, "HSPF")
            calc = create_calculator_for_profile(profile_id=profile_id)
            result = calc.calculate_hspf(measured)
        except Exception as exc:
            self._result_callback(f"[HSPF 오류] {type(exc).__name__}: {exc}")
            return
        self._result_callback(format_hspf_result(result))

    def _on_destroy(self, event: tk.Event) -> None:
        if event.widget is self._frame:
            self._auto_calc.dispose()
