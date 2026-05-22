"""ISO 16358-2 HSPF input section (Tkinter MVP).

Inputs and defaults mirror the 116 prototype so the Hong Kong HSPF =
3.643 smoke (golden case 1) is preserved.
"""

from __future__ import annotations

from typing import Callable, Mapping

import tkinter as tk
from tkinter import ttk

from core.calculator_dispatcher import create_calculator_for_profile
from ui_tk.input_widgets import NumericEntryRow
from ui_tk.profile_resolver import resolve_profile_id
from ui_tk.sections.iso16358_helpers import build_hspf_input, format_hspf_result


class IsoHspfSection:
    """Hong Kong HSPF — rated heating capacity + 7_full / 7_half."""

    def __init__(
        self,
        parent: tk.Widget,
        region_label: str,
        result_callback: Callable[[str], None],
    ) -> None:
        self._region_label = region_label
        self._result_callback = result_callback
        self._frame = ttk.LabelFrame(parent, text=f"HSPF ({region_label})")

        self._rated = NumericEntryRow(self._frame, "정격 난방 능력 [W]")
        self._rated.set_value("6300")
        self._rated.grid(row=0, column=0, columnspan=2, sticky="w", padx=4, pady=2)

        self._full_cap = NumericEntryRow(self._frame, "7_full 능력 [W]")
        self._full_cap.set_value("6300")
        self._full_cap.grid(row=1, column=0, sticky="w", padx=4, pady=2)
        self._full_pow = NumericEntryRow(self._frame, "7_full 전력 [W]")
        self._full_pow.set_value("1500")
        self._full_pow.grid(row=1, column=1, sticky="w", padx=4, pady=2)

        self._half_cap = NumericEntryRow(self._frame, "7_half 능력 [W]")
        self._half_cap.set_value("3200")
        self._half_cap.grid(row=2, column=0, sticky="w", padx=4, pady=2)
        self._half_pow = NumericEntryRow(self._frame, "7_half 전력 [W]")
        self._half_pow.set_value("800")
        self._half_pow.grid(row=2, column=1, sticky="w", padx=4, pady=2)

        ttk.Button(self._frame, text="HSPF 계산", command=self._on_calculate).grid(
            row=3, column=0, sticky="w", padx=4, pady=4
        )

    def pack(self, **kwargs) -> None:
        self._frame.pack(**kwargs)

    def _read_inputs(self) -> Mapping[str, object]:
        return build_hspf_input(
            rated_heating_capacity=self._rated.get_value(),
            full_capacity=self._full_cap.get_value(),
            full_power=self._full_pow.get_value(),
            half_capacity=self._half_cap.get_value(),
            half_power=self._half_pow.get_value(),
        )

    def _on_calculate(self) -> None:
        try:
            measured = self._read_inputs()
            profile_id = resolve_profile_id(self._region_label, "HSPF")
            calc = create_calculator_for_profile(profile_id=profile_id)
            result = calc.calculate_hspf(measured)
        except Exception as exc:
            self._result_callback(f"[HSPF 오류] {type(exc).__name__}: {exc}")
            return
        self._result_callback(format_hspf_result(result))
