"""KOREA midpoint guide table helper for calculator sections."""

from __future__ import annotations

import tkinter as tk

from apps.calculator.ui.table.compact_result_grid import CompactResultGrid
from apps.calculator.ui.table.visual_policy import SemanticTone


_GUIDE_ROWS = (
    ("current_tc", "현재 tc"),
    ("recommended_tc", "권장 tc"),
    ("recommended_mid_capacity", "권장 Mid capacity"),
)
_GUIDE_ROW_INDEX = {row_key: index for index, (row_key, _label) in enumerate(_GUIDE_ROWS)}


class _KoreaMidpointGrid(CompactResultGrid):
    """Compact grid with the section's existing address-based read seam."""

    def text_at_address(self, address: tuple[str, str]) -> str:
        row_key, column_key = address
        if column_key != "value" or row_key not in _GUIDE_ROW_INDEX:
            raise KeyError(address)
        return self.rows[_GUIDE_ROW_INDEX[row_key]][1]


class KoreaMidpointGuideTable:
    """Read-only table presenter for KOREA midpoint guide fields."""

    def __init__(self, parent: tk.Misc) -> None:
        self.table = _KoreaMidpointGrid(
            parent,
            headers=("항목", "값"),
            column_widths=(20, 14),
            surface_role="korea_midpoint_guide_grid",
        )
        self._render({row_key: "-" for row_key, _label in _GUIDE_ROWS})

    def grid(self, **kwargs) -> None:
        self.table.frame.grid(**kwargs)

    def set_values(self, fields: tuple[tuple[str, str], ...]) -> None:
        values = {key: value for key, value in fields}
        self._render(values)

    def set_status(self, status: str, *, tone: SemanticTone) -> None:
        self._render(
            {
                "current_tc": status,
                "recommended_tc": "-",
                "recommended_mid_capacity": "-",
            },
            value_tones={"current_tc": tone},
        )

    def _render(
        self,
        values: dict[str, str],
        *,
        value_tones: dict[str, SemanticTone] | None = None,
    ) -> None:
        value_tones = value_tones or {}
        rows = tuple(
            (label, values.get(row_key, "-"))
            for row_key, label in _GUIDE_ROWS
        )
        self.table.set_rows(
            rows,
            tones={
                (row_index, 1): (
                    value_tones.get(
                        _GUIDE_ROWS[row_index][0],
                        SemanticTone.PENDING
                        if value == "-"
                        else SemanticTone.CALCULATED,
                    )
                )
                for row_index, (_label, value) in enumerate(rows)
            },
        )
