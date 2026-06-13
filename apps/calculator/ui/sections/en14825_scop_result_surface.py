"""SCOP section-local compact result surface widgets."""

from __future__ import annotations

import tkinter as tk

from apps.calculator.ui.en14825 import ScopResultSummary
from apps.calculator.ui.layout_constants import (
    RESULT_HEADER_BG,
    RESULT_STATUS_FG,
    RESULT_VALUE_BG,
    TABLE_PASS_BG,
    TABLE_BODY_FONT,
    TABLE_CELL_PADX,
    TABLE_CELL_PADY,
    TABLE_GRID_COLOR,
    TABLE_HEADER_FONT,
    TABLE_HEADER_PADY,
)
from apps.calculator.ui.sections.en14825_scop_result_formatter import (
    format_scop_compact_rows,
    format_scop_status,
)


class ScopResultSurface:
    """Climate-local Declared/Tested result block for the SCOP section."""

    _COLUMNS = ("SCOP", "QH [kWh]", "Total [kWh]", "SCOP %")

    def __init__(self, parent: tk.Widget) -> None:
        self._frame = tk.Frame(
            parent,
            background=TABLE_GRID_COLOR,
            borderwidth=1,
            relief=tk.SOLID,
        )
        self._frame.surface_role = "summary_table"
        self._header_labels: dict[str, tk.Label] = {}
        self._row_header_labels: dict[str, tk.Label] = {}
        self._status_label = tk.Label(
            self._frame,
            text="대기 중",
            anchor="w",
            background=RESULT_VALUE_BG,
            foreground=RESULT_STATUS_FG,
            font=TABLE_BODY_FONT,
            padx=TABLE_CELL_PADX,
            pady=TABLE_CELL_PADY,
        )
        self._value_labels: dict[tuple[str, str], tk.Label] = {}
        self._build()

    @property
    def frame(self) -> tk.Frame:
        return self._frame

    @property
    def value_labels(self) -> dict[tuple[str, str], tk.Label]:
        return self._value_labels

    @property
    def header_labels(self) -> dict[str, tk.Label]:
        return self._header_labels

    @property
    def row_header_labels(self) -> dict[str, tk.Label]:
        return self._row_header_labels

    def grid(self, **kwargs) -> None:
        self._frame.grid(**kwargs)

    def show(self) -> None:
        self._frame.grid()

    def hide(self) -> None:
        self._frame.grid_remove()

    def manager(self) -> str:
        return self._frame.winfo_manager()

    def update(self, summary: ScopResultSummary) -> None:
        self.show()
        self._status_label.configure(text=format_scop_status(summary))
        self._set_row_values(format_scop_compact_rows(summary))

    def show_error(self, message: str) -> None:
        self.show()
        self._status_label.configure(text=f"기류/설정 오류: {message}")
        self.clear_values()

    def clear(self) -> None:
        self._status_label.configure(text="대기 중")
        self.clear_values()

    def clear_values(self) -> None:
        for label in self._value_labels.values():
            label.configure(text="-")

    def _build(self) -> None:
        self._frame.columnconfigure(0, weight=0)
        for column in range(1, len(self._COLUMNS) + 1):
            self._frame.columnconfigure(column, weight=1)

        self._header_labels["row_label"] = self._make_cell(
            row=0, column=0, text="구분", header=True
        )
        for column, key in enumerate(self._COLUMNS, start=1):
            self._header_labels[key] = self._make_cell(
                row=0, column=column, text=key, header=True
            )

        for row_index, row_label in enumerate(("Declared", "Tested"), start=1):
            highlight = row_label == "Tested"
            self._row_header_labels[row_label] = self._make_cell(
                row=row_index,
                column=0,
                text=row_label,
                header=True,
                background=TABLE_PASS_BG if highlight else None,
            )
            for column, key in enumerate(self._COLUMNS, start=1):
                self._value_labels[(row_label, key)] = self._make_cell(
                    row=row_index,
                    column=column,
                    text="-",
                    anchor="e",
                    background=TABLE_PASS_BG if highlight else None,
                )
        self._status_label.grid(
            row=3,
            column=0,
            columnspan=len(self._COLUMNS) + 1,
            sticky="ew",
            padx=(0, 1),
            pady=(0, 1),
        )

    def _make_cell(
        self,
        *,
        row: int,
        column: int,
        text: str,
        header: bool = False,
        anchor: str = "center",
        background: str | None = None,
    ) -> tk.Label:
        background = background or (RESULT_HEADER_BG if header else RESULT_VALUE_BG)
        font = TABLE_HEADER_FONT if header else TABLE_BODY_FONT
        label = tk.Label(
            self._frame,
            text=text,
            anchor=anchor,
            background=background,
            font=font,
            padx=TABLE_CELL_PADX,
            pady=TABLE_HEADER_PADY if header else TABLE_CELL_PADY,
        )
        label.grid(row=row, column=column, sticky="nsew", padx=(0, 1), pady=(0, 1))
        return label

    def _set_row_values(
        self, rows: tuple[tuple[str, tuple[tuple[str, str], ...]], ...]
    ) -> None:
        for row_label, fields in rows:
            field_map = dict(fields)
            for key in self._COLUMNS:
                self._value_labels[(row_label, key)].configure(
                    text=field_map.get(key, "-")
                )
