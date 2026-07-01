"""KOREA midpoint guide table helper for calculator sections."""

from __future__ import annotations

import tkinter as tk

from apps.calculator.ui.metric_input_table import MetricInputTable
from apps.calculator.ui.table.controller import TkTableController


_GUIDE_ROWS = (
    ("current_tc", "현재 tc"),
    ("recommended_tc", "권장 tc"),
    ("recommended_mid_capacity", "권장 Mid capacity"),
)
_GUIDE_ADDRESSES = tuple((row_key, "value") for row_key, _label in _GUIDE_ROWS)


class KoreaMidpointGuideTable:
    """Read-only table presenter for KOREA midpoint guide fields."""

    def __init__(self, parent: tk.Misc) -> None:
        self.table = MetricInputTable(
            parent,
            columns=(("value", "값"),),
            rows=_GUIDE_ROWS,
            editable_cells={address: address[0] for address in _GUIDE_ADDRESSES},
            row_header_chars=20,
            data_column_chars=14,
        )
        self.table.set_readonly_addresses(_GUIDE_ADDRESSES)
        self.controller = TkTableController(self.table)

    def grid(self, **kwargs) -> None:
        self.table.grid(**kwargs)

    def set_values(self, fields: tuple[tuple[str, str], ...]) -> None:
        values = {key: value for key, value in fields}
        display_values = {
            (row_key, "value"): values.get(row_key, "-")
            for row_key, _label in _GUIDE_ROWS
        }
        self.table.set_values_batch(
            {row_key: values.get(row_key, "-") for row_key, _label in _GUIDE_ROWS}
        )
        self.table.set_readonly_addresses(
            _GUIDE_ADDRESSES,
            display_values=display_values,
        )

    def set_status(self, status: str) -> None:
        display_values = {
            ("current_tc", "value"): status,
            ("recommended_tc", "value"): "-",
            ("recommended_mid_capacity", "value"): "-",
        }
        self.table.set_values_batch(
            {
                "current_tc": status,
                "recommended_tc": "-",
                "recommended_mid_capacity": "-",
            }
        )
        self.table.set_readonly_addresses(
            _GUIDE_ADDRESSES,
            display_values=display_values,
        )
