"""Tk-free helpers for Excel-like table interaction."""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field

from ui_tk.table.roles import CellRole, is_copyable, is_mutable, is_selectable

CellAddress = tuple[int, int]
SelectionBounds = tuple[int, int, int, int]
ClipboardMatrix = tuple[tuple[str, ...], ...]

_CONTROL_MASK = 0x0004
_ALT_MASK = 0x0008
_REPLACE_NONPRINTABLE_KEYSYMS = frozenset(
    {
        "BackSpace",
        "Delete",
        "Escape",
        "Return",
        "Tab",
        "ISO_Left_Tab",
        "Left",
        "Right",
        "Up",
        "Down",
        "Home",
        "End",
        "Page_Up",
        "Page_Down",
        "Insert",
        "Shift_L",
        "Shift_R",
        "Control_L",
        "Control_R",
        "Alt_L",
        "Alt_R",
        "Meta_L",
        "Meta_R",
        "Super_L",
        "Super_R",
        "Caps_Lock",
        "Num_Lock",
        "Scroll_Lock",
    }
)


def parse_clipboard_matrix(text: str | None) -> ClipboardMatrix:
    """Parse TSV clipboard text and preserve rectangular/ragged shape."""
    if text is None:
        return ()
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    if normalized.endswith("\n"):
        normalized = normalized[:-1]
    if normalized == "":
        return (("",),)
    return tuple(tuple(row.split("\t")) for row in normalized.split("\n"))


def encode_selection_to_clipboard(rows: Iterable[Iterable[str]]) -> str:
    return "\n".join("\t".join(str(cell) for cell in row) for row in rows)


def selection_bounds(anchor: CellAddress, active: CellAddress) -> SelectionBounds:
    return (
        min(anchor[0], active[0]),
        max(anchor[0], active[0]),
        min(anchor[1], active[1]),
        max(anchor[1], active[1]),
    )


def positions_in_bounds(
    bounds: SelectionBounds, row_count: int, column_count: int
) -> tuple[CellAddress, ...]:
    top, bottom, left, right = bounds
    return tuple(
        (row, column)
        for row in range(max(top, 0), min(bottom, row_count - 1) + 1)
        for column in range(max(left, 0), min(right, column_count - 1) + 1)
    )


def copyable_positions(
    bounds: SelectionBounds,
    row_count: int,
    column_count: int,
    roles: Sequence[CellRole],
) -> tuple[CellAddress, ...]:
    return tuple(
        position
        for position in positions_in_bounds(bounds, row_count, column_count)
        if is_copyable(roles[position[1]])
    )


def editable_clear_targets(
    positions: Iterable[CellAddress], roles: Sequence[CellRole]
) -> dict[CellAddress, str]:
    return {
        position: ""
        for position in positions
        if 0 <= position[1] < len(roles) and is_mutable(roles[position[1]])
    }


def editable_paste_targets(
    matrix: ClipboardMatrix,
    bounds: SelectionBounds,
    roles: Sequence[CellRole],
) -> dict[CellAddress, str]:
    top, bottom, left, right = bounds
    if not matrix:
        return {}
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
        if 0 <= position[1] < len(roles) and is_mutable(roles[position[1]])
    }


def resolve_next_position(
    current: CellAddress,
    row_count: int,
    column_count: int,
    direction: str,
) -> CellAddress:
    row, column = current
    if row_count <= 0 or column_count <= 0:
        return current
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
    current: CellAddress,
    row_count: int,
    column_count: int,
    direction: str,
) -> CellAddress:
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


def is_replace_printable(keysym: str, char: str, state: int | None = 0) -> bool:
    if keysym in _REPLACE_NONPRINTABLE_KEYSYMS:
        return False
    if len(keysym) >= 2 and keysym[0] == "F" and keysym[1:].isdigit():
        return False
    if not char:
        return False
    if ord(char[0]) < 0x20:
        return False
    event_state = int(state) if state is not None else 0
    if event_state & _CONTROL_MASK:
        return False
    if event_state & _ALT_MASK:
        return False
    return True


def selectable_position_or_none(
    position: CellAddress,
    row_count: int,
    column_count: int,
    roles: Sequence[CellRole],
) -> CellAddress | None:
    row, column = position
    if not (0 <= row < row_count and 0 <= column < column_count):
        return None
    if not is_selectable(roles[column]):
        return None
    return position


@dataclass
class UndoStack:
    """Simple grouped undo stack for table snapshots."""

    limit: int = 50
    _items: list[object] = field(default_factory=list)

    def push(self, snapshot: object) -> None:
        self._items.append(snapshot)
        while len(self._items) > self.limit:
            self._items.pop(0)

    def pop(self) -> object | None:
        if not self._items:
            return None
        return self._items.pop()

    def clear(self) -> None:
        self._items.clear()

    def __len__(self) -> int:
        return len(self._items)


def values_changed(before: Mapping[object, object], after: Mapping[object, object]) -> bool:
    return dict(before) != dict(after)
