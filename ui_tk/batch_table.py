"""Shared contracts and helpers for Tkinter batch table surfaces."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Protocol

from ui_tk.batch_models import BatchColumnRole
from ui_tk.excel_like_table_controller import (
    ClipboardMatrix,
    resolve_selection_bounds,
)

GridAddress = tuple[int, int]
SelectionBounds = tuple[int, int, int, int]


class BatchTableSurface(Protocol):
    def row_count(self) -> int: ...
    def column_count(self) -> int: ...
    def column_roles(self) -> tuple[BatchColumnRole, ...]: ...
    def ensure_row_count(self, count: int) -> None: ...
    def text_at_position(self, position: GridAddress) -> str: ...
    def set_positions_batch(self, values: Mapping[GridAddress, str]) -> bool: ...
    def get_text_rows(self) -> list[dict[str, str]]: ...
    def set_text_rows(self, rows: Iterable[Mapping[str, str]]) -> None: ...
    def cell_frame(self, position: GridAddress): ...
    def cell_widget(self, position: GridAddress): ...
    def focus_widget(self, position: GridAddress): ...
    def default_cell_background(self, position: GridAddress) -> str: ...
    def clipboard_clear(self) -> None: ...
    def clipboard_append(self, text: str) -> None: ...
    def clipboard_get(self) -> str: ...
    def winfo_containing(self, root_x: int, root_y: int): ...


def positions_in_bounds(
    bounds: SelectionBounds, row_count: int, column_count: int
) -> tuple[GridAddress, ...]:
    top, bottom, left, right = bounds
    return tuple(
        (row, column)
        for row in range(max(top, 0), min(bottom, row_count - 1) + 1)
        for column in range(max(left, 0), min(right, column_count - 1) + 1)
    )


def editable_paste_targets(
    matrix: ClipboardMatrix,
    bounds: SelectionBounds,
    column_roles: tuple[BatchColumnRole, ...],
) -> dict[GridAddress, str]:
    top, bottom, left, right = bounds
    if len(matrix) == 1 and len(matrix[0]) == 1:
        raw_targets = (
            ((row, column), matrix[0][0])
            for row in range(top, bottom + 1)
            for column in range(left, right + 1)
        )
    else:
        raw_targets = (
            ((top + row_offset, left + column_offset), value)
            for row_offset, row in enumerate(matrix)
            for column_offset, value in enumerate(row)
        )
    return {
        position: value
        for position, value in raw_targets
        if 0 <= position[1] < len(column_roles)
        and column_roles[position[1]] is BatchColumnRole.INPUT
    }


def editable_clear_targets(
    positions: Iterable[GridAddress],
    column_roles: tuple[BatchColumnRole, ...],
) -> dict[GridAddress, str]:
    return {
        position: ""
        for position in positions
        if 0 <= position[1] < len(column_roles)
        and column_roles[position[1]] is BatchColumnRole.INPUT
    }


def resolve_next_position(
    current: GridAddress,
    row_count: int,
    column_count: int,
    direction: str,
) -> GridAddress:
    row, column = current
    if direction == "tab":
        index = (row * column_count + column + 1) % (row_count * column_count)
        return divmod(index, column_count)
    if direction == "shift-tab":
        index = (row * column_count + column - 1) % (row_count * column_count)
        return divmod(index, column_count)
    if direction == "enter":
        return ((row + 1) % row_count, column)
    if direction == "shift-enter":
        return ((row - 1) % row_count, column)
    raise ValueError(f"Unknown navigation direction: {direction!r}")


def resolve_adjacent_position(
    current: GridAddress,
    row_count: int,
    column_count: int,
    direction: str,
) -> GridAddress:
    row, column = current
    offsets = {
        "left": (0, -1),
        "right": (0, 1),
        "up": (-1, 0),
        "down": (1, 0),
    }
    if direction not in offsets:
        raise ValueError(f"Unknown arrow direction: {direction!r}")
    row_delta, column_delta = offsets[direction]
    return (
        min(max(0, row + row_delta), row_count - 1),
        min(max(0, column + column_delta), column_count - 1),
    )


def selection_bounds(anchor: GridAddress, active: GridAddress) -> SelectionBounds:
    return resolve_selection_bounds(anchor, active)
