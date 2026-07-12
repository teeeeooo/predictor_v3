"""SCOP section-local compact result surface widgets."""

from __future__ import annotations

import tkinter as tk

from apps.calculator.ui.en14825 import ScopResultSummary
from apps.calculator.ui.layout_constants import (
    RESULT_STATUS_FG,
    RESULT_VALUE_BG,
)
from apps.calculator.ui.sections.en14825_scop_result_formatter import (
    format_scop_compact_rows,
    format_scop_status,
)
from apps.calculator.ui.table.compact_result_grid import CompactResultGrid
from apps.calculator.ui.table.grid_primitives import (
    create_cell_container,
    create_text_label,
)
from apps.calculator.ui.table.visual_policy import AlignmentRole, SemanticTone


class ScopResultSurface:
    """Climate-local Declared/Tested result block for the SCOP section."""

    _COLUMNS = ("SCOP", "QH [kWh]", "Total [kWh]", "SCOP %")
    _ROW_LABELS = ("Declared", "Tested")

    def __init__(self, parent: tk.Widget) -> None:
        self._grid = CompactResultGrid(
            parent,
            headers=("구분", *self._COLUMNS),
            column_widths=(10, 10, 12, 12, 10),
            surface_role="en14825_scop_result_grid",
        )
        self._frame = self._grid.frame
        self._frame.surface_role = "summary_table"
        self._frame.layout_policy = "content_hug"
        self.layout_policy = "content_hug"
        self._grid.set_rows(self._empty_rows(), tones=self._row_tones())
        self._header_labels = {
            "row_label": self._grid.header_labels[0],
            **{
                key: self._grid.header_labels[column]
                for column, key in enumerate(self._COLUMNS, start=1)
            },
        }
        self._row_header_labels = {
            row_label: self._grid.value_labels[(row, 0)]
            for row, row_label in enumerate(self._ROW_LABELS)
        }
        self._value_labels = {
            (row_label, key): self._grid.value_labels[(row, column)]
            for row, row_label in enumerate(self._ROW_LABELS)
            for column, key in enumerate(self._COLUMNS, start=1)
        }
        status_cell = create_cell_container(
            self._frame,
            background=RESULT_VALUE_BG,
            row=3,
            column=0,
            surface_role="compact_status_cell",
        )
        status_cell.grid_configure(columnspan=len(self._COLUMNS) + 1)
        self._status_cell = status_cell
        self._status_label = create_text_label(
            status_cell,
            text="대기 중",
            width=None,
            alignment=AlignmentRole.STATUS_TEXT,
            tone=SemanticTone.PENDING,
        )
        self._status_label.configure(foreground=RESULT_STATUS_FG)
        self._set_status("대기 중", SemanticTone.PENDING)

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
        self._set_status(
            format_scop_status(summary), self._status_tone(summary.status_code)
        )
        self._set_row_values(format_scop_compact_rows(summary))

    def show_error(self, message: str) -> None:
        self.show()
        self._set_status(f"기류/설정 오류: {message}", SemanticTone.WARNING)
        self.clear_values()

    def show_invalid(self, message: str) -> None:
        self.show()
        self._set_status(message, SemanticTone.INVALID)
        self.clear_values()

    def clear(self) -> None:
        self._set_status("대기 중", SemanticTone.PENDING)
        self.clear_values()

    def clear_values(self) -> None:
        self._grid.set_rows(self._empty_rows(), tones=self._row_tones())

    def _set_row_values(
        self, rows: tuple[tuple[str, tuple[tuple[str, str], ...]], ...]
    ) -> None:
        fields_by_row = {row_label: dict(fields) for row_label, fields in rows}
        display_rows = tuple(
            (
                row_label,
                *(fields_by_row.get(row_label, {}).get(key, "-") for key in self._COLUMNS),
            )
            for row_label in self._ROW_LABELS
        )
        self._grid.set_rows(display_rows, tones=self._cell_tones(display_rows))

    def _empty_rows(self) -> tuple[tuple[str, ...], ...]:
        return tuple(
            (row_label, *("-" for _key in self._COLUMNS))
            for row_label in self._ROW_LABELS
        )

    def _row_tones(self) -> dict[tuple[int, int], SemanticTone]:
        return self._cell_tones(self._empty_rows())

    def _cell_tones(
        self, rows: tuple[tuple[str, ...], ...]
    ) -> dict[tuple[int, int], SemanticTone]:
        return {
            (row, column): (
                SemanticTone.DEFAULT
                if column == 0
                else SemanticTone.PENDING
                if value == "-"
                else SemanticTone.CALCULATED
            )
            for row, values in enumerate(rows)
            for column, value in enumerate(values)
        }

    def _set_status(self, text: str, tone: SemanticTone) -> None:
        background = self._grid.policy.background(tone)
        self._status_cell.configure(background=background)
        self._status_cell.semantic_background = background
        self._status_cell.semantic_tone = tone.value
        self._status_label.configure(text=text, background=background)
        self._status_label.semantic_tone = tone.value

    @staticmethod
    def _status_tone(status_code: str) -> SemanticTone:
        if status_code in {"idle", "input_incomplete"}:
            return SemanticTone.PENDING
        if status_code == "complete":
            return SemanticTone.DEFAULT
        if status_code in {
            "invalid_design_load",
            "invalid_t_design",
            "invalid_climate",
            "invalid_temp_override",
        }:
            return SemanticTone.INVALID
        return SemanticTone.WARNING
