"""Cell-rendered foundation for small fixed read-only Calculator results."""

from __future__ import annotations

from collections.abc import Mapping
import tkinter as tk

from apps.calculator.ui.table.grid_primitives import (
    create_cell_container,
    create_grid_surface,
    create_text_label,
)
from apps.calculator.ui.table.visual_policy import (
    AlignmentRole,
    DEFAULT_TABLE_VISUAL_POLICY,
    SemanticTone,
    TkTableVisualPolicy,
)

CellPosition = tuple[int, int]


class CompactResultGrid:
    """Read-only logical grid with whole-table copy and presentation metadata."""

    def __init__(
        self,
        parent: tk.Misc,
        *,
        headers: tuple[str, ...],
        column_widths: tuple[int, ...] | None = None,
        identity_columns: frozenset[int] = frozenset({0}),
        policy: TkTableVisualPolicy = DEFAULT_TABLE_VISUAL_POLICY,
        surface_role: str = "compact_result_grid",
    ) -> None:
        if not headers:
            raise ValueError("compact result grid requires at least one header")
        if column_widths is not None and len(column_widths) != len(headers):
            raise ValueError("column widths must match compact result headers")
        self.headers = headers
        self.rows: tuple[tuple[str, ...], ...] = ()
        self.policy = policy
        self.identity_columns = identity_columns
        self.column_widths = column_widths or tuple(12 for _ in headers)
        self.surface_role = surface_role
        self.frame = create_grid_surface(
            parent,
            name="compact_result_grid",
            focusable=True,
            policy=policy,
        )
        self.frame.surface_role = surface_role
        self.header_cells: dict[int, tk.Frame] = {}
        self.header_labels: dict[int, tk.Label] = {}
        self.value_cells: dict[CellPosition, tk.Frame] = {}
        self.value_labels: dict[CellPosition, tk.Label] = {}
        self._tones: dict[CellPosition, SemanticTone] = {}
        self._build_headers()
        self.frame.bind("<Control-c>", self.copy)
        self.frame.bind("<Command-c>", self.copy)

    def pack(self, **kwargs: object) -> None:
        self.frame.pack(**kwargs)

    def pack_forget(self) -> None:
        self.frame.pack_forget()

    def winfo_manager(self) -> str:
        return self.frame.winfo_manager()

    def set_rows(
        self,
        rows: tuple[tuple[str, ...], ...],
        *,
        tones: Mapping[CellPosition, SemanticTone] | None = None,
    ) -> None:
        self._validate_rows(rows)
        tones = dict(tones or {})
        if len(rows) == len(self.rows) and self.value_labels:
            self.rows = rows
            self._tones = tones
            self._update_values()
            return
        self._clear_body()
        self.rows = rows
        self._tones = tones
        for row_index, row in enumerate(rows):
            self._build_row(row_index, row)

    def clear(self) -> None:
        self._clear_body()
        self.rows = ()
        self._tones = {}

    def logical_data(self) -> tuple[tuple[str, ...], tuple[tuple[str, ...], ...]]:
        return self.headers, self.rows

    def as_tsv(self) -> str:
        lines = ["\t".join(self.headers)]
        lines.extend("\t".join(row) for row in self.rows)
        return "\n".join(lines)

    def copy(self, _event: tk.Event | None = None) -> str:
        self.frame.clipboard_clear()
        self.frame.clipboard_append(self.as_tsv())
        return "break"

    def _build_headers(self) -> None:
        for column, text in enumerate(self.headers):
            self.frame.columnconfigure(column, weight=0)
            cell = create_cell_container(
                self.frame,
                row=0,
                column=column,
                background=self.policy.header_background,
                surface_role="compact_header_cell",
                policy=self.policy,
            )
            alignment = (
                AlignmentRole.HEADER_IDENTITY
                if column in self.identity_columns
                else AlignmentRole.HEADER_VALUE
            )
            label = create_text_label(
                cell,
                text=text,
                width=self.column_widths[column],
                alignment=alignment,
                header=True,
                policy=self.policy,
            )
            self.header_cells[column] = cell
            self.header_labels[column] = label

    def _build_row(self, row_index: int, row: tuple[str, ...]) -> None:
        for column, value in enumerate(row):
            position = (row_index, column)
            tone = self._tones.get(position, SemanticTone.DEFAULT)
            background = self.policy.background(tone)
            cell = create_cell_container(
                self.frame,
                row=row_index + 1,
                column=column,
                background=background,
                surface_role="compact_result_cell",
                policy=self.policy,
            )
            alignment = (
                AlignmentRole.IDENTITY_TEXT
                if column in self.identity_columns
                else AlignmentRole.NUMERIC_RESULT
            )
            label = create_text_label(
                cell,
                text=value,
                width=self.column_widths[column],
                alignment=alignment,
                tone=tone,
                policy=self.policy,
            )
            self.value_cells[position] = cell
            self.value_labels[position] = label

    def _update_values(self) -> None:
        for row_index, row in enumerate(self.rows):
            for column, value in enumerate(row):
                position = (row_index, column)
                tone = self._tones.get(position, SemanticTone.DEFAULT)
                background = self.policy.background(tone)
                self.value_cells[position].configure(background=background)
                self.value_cells[position].semantic_background = background
                self.value_labels[position].configure(text=value, background=background)
                self.value_labels[position].semantic_tone = tone.value

    def _clear_body(self) -> None:
        for cell in self.value_cells.values():
            cell.destroy()
        self.value_cells.clear()
        self.value_labels.clear()

    def _validate_rows(self, rows: tuple[tuple[str, ...], ...]) -> None:
        for row in rows:
            if len(row) != len(self.headers):
                raise ValueError("compact result row width must match headers")
