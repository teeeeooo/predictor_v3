"""ISO 16358-1 CSPF input section (Tkinter MVP).

Inputs and defaults mirror the 116 prototype so the Hong Kong CSPF =
4.939 smoke result is preserved.
"""

from __future__ import annotations

from typing import Callable, Mapping, Tuple

import tkinter as tk
from tkinter import ttk

from core.calculator_dispatcher import create_calculator_for_profile
from ui_tk.input_widgets import NumericEntryRow
from ui_tk.profile_resolver import resolve_profile_id
from ui_tk.sections.iso16358_helpers import build_cspf_input, format_cspf_result


class IsoCspfSection:
    """Hong Kong CSPF — 35_full / 35_half capacity + power + declared.

    Matches the ``"measure"`` points declared in
    ``data/region_configs/hong_kong.json``.
    """

    def __init__(
        self,
        parent: tk.Widget,
        region_label: str,
        result_callback: Callable[[str], None],
    ) -> None:
        self._region_label = region_label
        self._result_callback = result_callback
        self._frame = ttk.LabelFrame(parent, text=f"CSPF ({region_label})")

        self._declared = NumericEntryRow(self._frame, "정격 능력 [W]")
        self._declared.set_value("3500")
        self._declared.grid(row=0, column=0, columnspan=2, sticky="w", padx=4, pady=2)

        self._full_cap = NumericEntryRow(self._frame, "35_full 능력 [W]")
        self._full_cap.set_value("3600")
        self._full_cap.grid(row=1, column=0, sticky="w", padx=4, pady=2)
        self._full_pow = NumericEntryRow(self._frame, "35_full 전력 [W]")
        self._full_pow.set_value("900")
        self._full_pow.grid(row=1, column=1, sticky="w", padx=4, pady=2)

        self._half_cap = NumericEntryRow(self._frame, "35_half 능력 [W]")
        self._half_cap.set_value("1700")
        self._half_cap.grid(row=2, column=0, sticky="w", padx=4, pady=2)
        self._half_pow = NumericEntryRow(self._frame, "35_half 전력 [W]")
        self._half_pow.set_value("380")
        self._half_pow.grid(row=2, column=1, sticky="w", padx=4, pady=2)

        ttk.Button(self._frame, text="CSPF 계산", command=self._on_calculate).grid(
            row=3, column=0, sticky="w", padx=4, pady=4
        )

    def pack(self, **kwargs) -> None:
        self._frame.pack(**kwargs)

    def _read_inputs(self) -> Tuple[Mapping[str, Mapping[str, float]], float]:
        return build_cspf_input(
            full_capacity=self._full_cap.get_value(),
            full_power=self._full_pow.get_value(),
            half_capacity=self._half_cap.get_value(),
            half_power=self._half_pow.get_value(),
            declared_capacity=self._declared.get_value(),
        )

    def _on_calculate(self) -> None:
        try:
            measured, declared = self._read_inputs()
            profile_id = resolve_profile_id(self._region_label, "CSPF")
            calc = create_calculator_for_profile(profile_id=profile_id)
            result = calc.calculate_cspf(measured, declared_capacity=declared)
        except Exception as exc:
            self._result_callback(f"[CSPF 오류] {type(exc).__name__}: {exc}")
            return
        self._result_callback(format_cspf_result(result))
