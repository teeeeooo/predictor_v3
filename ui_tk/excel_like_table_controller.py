"""Excel-like interactions attached to a metadata-bearing Tkinter input table."""

from __future__ import annotations

from collections.abc import Callable, Iterable

from ui_tk.layout_constants import (
    TABLE_ACTIVE_BG,
    TABLE_EDITABLE_BG,
    TABLE_SELECTED_BG,
)
from ui_tk.table_grid_model import parse_numeric_cell

GridAddress = tuple[int, int]
SelectionBounds = tuple[int, int, int, int]
ClipboardMatrix = tuple[tuple[str, ...], ...]


def parse_clipboard_matrix(text: str) -> ClipboardMatrix:
    """Parse rectangular clipboard text; one trailing line ending is ignored."""
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    if normalized.endswith("\n"):
        normalized = normalized[:-1]
    rows = tuple(tuple(row.split("\t")) for row in normalized.split("\n"))
    if not rows or not rows[0] or len({len(row) for row in rows}) != 1:
        raise ValueError("clipboard payload must be a rectangular TSV grid")
    return rows


def encode_selection_to_clipboard(rows: Iterable[Iterable[str]]) -> str:
    return "\n".join("\t".join(row) for row in rows)


def resolve_selection_bounds(
    anchor: GridAddress, active: GridAddress
) -> SelectionBounds:
    return (
        min(anchor[0], active[0]),
        max(anchor[0], active[0]),
        min(anchor[1], active[1]),
        max(anchor[1], active[1]),
    )


def clip_paste_targets(
    matrix: ClipboardMatrix,
    bounds: SelectionBounds,
    row_count: int,
    column_count: int,
) -> tuple[tuple[GridAddress, str], ...]:
    top, bottom, left, right = bounds
    if len(matrix) == 1 and len(matrix[0]) == 1:
        return tuple(
            ((row, column), matrix[0][0])
            for row in range(top, bottom + 1)
            for column in range(left, right + 1)
        )
    return tuple(
        ((top + row, left + column), value)
        for row, values in enumerate(matrix)
        for column, value in enumerate(values)
        if top + row < row_count and left + column < column_count
    )


def validate_paste_matrix(
    matrix: ClipboardMatrix, validator: Callable[[str], object] = parse_numeric_cell
) -> None:
    for row in matrix:
        for value in row:
            validator(value)


def resolve_next_cell(
    current: GridAddress, editable: tuple[GridAddress, ...], direction: str
) -> GridAddress:
    if direction in {"tab", "shift-tab"}:
        ordered = tuple(sorted(editable))
        step = 1 if direction == "tab" else -1
    elif direction in {"enter", "shift-enter"}:
        ordered = tuple(sorted(editable, key=lambda item: (item[1], item[0])))
        step = 1 if direction == "enter" else -1
    else:
        raise ValueError(f"Unknown navigation direction: {direction!r}")
    return ordered[(ordered.index(current) + step) % len(editable)]


class ExcelLikeTableController:
    """Attach spreadsheet-like selection and edits to a ``MetricInputTable``."""

    def __init__(self, table) -> None:
        self.table = table
        self._by_position = {
            (row, column): (row_key, column_key)
            for row, (row_key, _label) in enumerate(table.rows)
            for column, (column_key, _label) in enumerate(table.columns)
        }
        self._editable_positions = tuple(
            position
            for position, address in self._by_position.items()
            if table.field_key_for_address(address) is not None
        )
        self.anchor: GridAddress | None = None
        self.active: GridAddress | None = None
        self._undo: list[dict[str, str]] = []
        self._replace_pending = False
        self._widget_positions: dict[object, GridAddress] = {}
        self._internal_focus_move = False
        self._register()
        table.interaction_controller = self

    def _register(self) -> None:
        for position in self._editable_positions:
            address = self._by_position[position]
            field_key = self.table.field_key_for_address(address)
            entry = self.table.editable_entries[field_key]
            cell = self.table.editable_cell_frames[field_key]
            self._widget_positions[entry] = position
            self._widget_positions[cell] = position
            cell.bind("<Button-1>", lambda event, p=position: self._click(event, p))
            cell.bind("<B1-Motion>", self._drag)
            entry.bind("<Button-1>", lambda event, p=position: self._click(event, p))
            entry.bind("<B1-Motion>", self._drag)
            entry.bind("<Control-c>", self._copy)
            entry.bind("<Command-c>", self._copy)
            entry.bind("<Control-C>", self._copy)
            entry.bind("<Command-C>", self._copy)
            entry.bind("<Control-v>", self._paste)
            entry.bind("<Command-v>", self._paste)
            entry.bind("<Control-V>", self._paste)
            entry.bind("<Command-V>", self._paste)
            entry.bind("<Control-z>", self._undo_last)
            entry.bind("<Command-z>", self._undo_last)
            entry.bind("<Control-Z>", self._undo_last)
            entry.bind("<Command-Z>", self._undo_last)
            entry.bind("<Delete>", self._clear)
            entry.bind("<BackSpace>", self._clear)
            entry.bind("<Tab>", lambda event: self._navigate("tab"))
            entry.bind("<Shift-Tab>", lambda event: self._navigate("shift-tab"))
            entry.bind("<ISO_Left_Tab>", lambda event: self._navigate("shift-tab"))
            entry.bind("<Return>", lambda event: self._navigate("enter"))
            entry.bind("<Shift-Return>", lambda event: self._navigate("shift-enter"))
            entry.bind("<KP_Enter>", lambda event: self._navigate("enter"))
            entry.bind("<Shift-KP_Enter>", lambda event: self._navigate("shift-enter"))
            entry.bind("<Left>", lambda event: self._arrow("left"))
            entry.bind("<Right>", lambda event: self._arrow("right"))
            entry.bind("<Up>", lambda event: self._arrow("up"))
            entry.bind("<Down>", lambda event: self._arrow("down"))
            entry.bind("<Escape>", lambda event: self._clear_selection())
            entry.bind("<FocusOut>", self._on_focus_out)
            entry.bind(
                "<KeyPress>",
                lambda event, p=position: self._type_replace(event, p),
                add="+",
            )

        # Shortcuts on table frame so they work when focus is on the table frame
        for seq, handler in (
            ("<Command-c>", self._copy),
            ("<Command-C>", self._copy),
            ("<Command-v>", self._paste),
            ("<Command-V>", self._paste),
            ("<Command-z>", self._undo_last),
            ("<Command-Z>", self._undo_last),
            ("<Control-c>", self._copy),
            ("<Control-C>", self._copy),
            ("<Control-v>", self._paste),
            ("<Control-V>", self._paste),
            ("<Control-z>", self._undo_last),
            ("<Control-Z>", self._undo_last),
        ):
            self.table.table_frame.bind(seq, handler)

        # Click on non-editable parts clears selection for this table
        for widget in (
            *self.table.header_cells.values(),
            *self.table.row_header_cells.values(),
            *self.table.static_cell_frames.values(),
        ):
            widget.bind("<Button-1>", lambda event: self._clear_selection())

    @property
    def selection_bounds(self) -> SelectionBounds | None:
        if self.anchor is None or self.active is None:
            return None
        return resolve_selection_bounds(self.anchor, self.active)

    def select(self, position: GridAddress, *, extend: bool = False) -> None:
        if position not in self._editable_positions:
            return
        if not extend or self.anchor is None:
            self.anchor = position
        self.active = position
        self._replace_pending = True
        self._paint_selection()

    def selected_positions(self) -> tuple[GridAddress, ...]:
        bounds = self.selection_bounds
        if bounds is None:
            return ()
        top, bottom, left, right = bounds
        return tuple(
            position
            for position in self._editable_positions
            if top <= position[0] <= bottom and left <= position[1] <= right
        )

    def _paint_selection(self) -> None:
        selected = set(self.selected_positions())
        for position in self._editable_positions:
            field_key = self.table.field_key_for_address(self._by_position[position])
            color = TABLE_EDITABLE_BG
            if position in selected:
                color = TABLE_SELECTED_BG
            if position == self.active:
                color = TABLE_ACTIVE_BG
            self.table.editable_entries[field_key].configure(background=color)

    def _click(self, event, position: GridAddress) -> str:
        self.select(position, extend=bool(event.state & 0x0001))
        field_key = self.table.field_key_for_address(self._by_position[position])
        entry = self.table.editable_entries[field_key]
        self._internal_focus_move = True
        entry.focus_set()
        entry.configure(insertontime=0)
        entry.selection_clear()
        entry.icursor(0)
        return "break"

    def _drag(self, event) -> str:
        widget = self.table.winfo_containing(event.x_root, event.y_root)
        position = self._widget_positions.get(widget)
        if position is not None:
            self.select(position, extend=True)
        return "break"

    def _matrix_text(self) -> tuple[tuple[str, ...], ...]:
        if self.selection_bounds is None:
            return ()
        top, bottom, left, right = self.selection_bounds
        return tuple(
            tuple(
                self.table.text_at_address(self._by_position[(row, column)])
                for column in range(left, right + 1)
            )
            for row in range(top, bottom + 1)
        )

    def _copy(self, _event=None) -> str:
        rows = self._matrix_text()
        if rows:
            self.table.clipboard_clear()
            self.table.clipboard_append(encode_selection_to_clipboard(rows))
        return "break"

    def _paste(self, _event=None) -> str:
        if self.selection_bounds is None:
            return "break"
        from tkinter import TclError

        try:
            matrix = parse_clipboard_matrix(self.table.clipboard_get())
            validate_paste_matrix(matrix)
        except (TclError, ValueError):
            return "break"
        targets = clip_paste_targets(
            matrix, self.selection_bounds, len(self.table.rows), len(self.table.columns)
        )
        self._apply({self._by_position[position]: value for position, value in targets})
        return "break"

    def _clear(self, _event=None) -> str:
        self._apply(
            {self._by_position[position]: "" for position in self.selected_positions()}
        )
        return "break"

    def _apply(self, values: dict[tuple[str, str], str]) -> None:
        before = self.table.get_text_values()
        if self.table.set_address_values_batch(values):
            self._undo.append(before)
        self._replace_pending = False

    def _undo_last(self, _event=None) -> str:
        if self._undo:
            self.table.set_values_batch(self._undo.pop())
        return "break"

    def _navigate(self, direction: str) -> str:
        current = self.active or self._editable_positions[0]
        target = resolve_next_cell(current, self._editable_positions, direction)
        self._internal_focus_move = True
        self.select(target)
        address = self._by_position[target]
        field_key = self.table.field_key_for_address(address)
        entry = self.table.editable_entries[field_key]
        entry.focus_set()
        entry.configure(insertontime=0)
        entry.selection_clear()
        entry.icursor(0)
        return "break"

    def _arrow(self, direction: str) -> str:
        if not self._replace_pending or self.active is None:
            return ""
        row, col = self.active
        if direction == "left":
            target = (row, col - 1)
        elif direction == "right":
            target = (row, col + 1)
        elif direction == "up":
            target = (row - 1, col)
        elif direction == "down":
            target = (row + 1, col)
        else:
            return ""
        if target not in self._editable_positions:
            return "break"
        self._internal_focus_move = True
        self.select(target)
        field_key = self.table.field_key_for_address(self._by_position[target])
        entry = self.table.editable_entries[field_key]
        entry.focus_set()
        entry.configure(insertontime=0)
        entry.selection_clear()
        entry.icursor(0)
        return "break"

    def _type_replace(self, event, position: GridAddress) -> str | None:
        if not self._replace_pending or position != self.active:
            return None
        if not event.char or not event.char.isprintable() or event.state & 0x000C:
            return None
        self._apply({self._by_position[position]: event.char})
        field_key = self.table.field_key_for_address(self._by_position[position])
        entry = self.table.editable_entries[field_key]
        entry.icursor("end")
        entry.configure(insertontime=600)
        return "break"

    def _clear_selection(self, event=None) -> str:
        self.anchor = None
        self.active = None
        self._replace_pending = False
        self._paint_selection()
        return "break"

    def _on_focus_out(self, event) -> None:
        if self._internal_focus_move:
            self._internal_focus_move = False
            return
        try:
            exists = self.table.winfo_exists()
        except Exception:
            return
        if not exists:
            return
        self._clear_selection()
