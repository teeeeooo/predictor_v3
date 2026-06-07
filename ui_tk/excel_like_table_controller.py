from __future__ import annotations

from collections.abc import Callable, Iterable

from ui_tk.layout_constants import (
    TABLE_ACTIVE_BG,
    TABLE_EDITABLE_BG,
    TABLE_INVALID_BG,
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
def resolve_selection_bounds(anchor: GridAddress, active: GridAddress) -> SelectionBounds:
    return (min(anchor[0], active[0]), max(anchor[0], active[0]), min(anchor[1], active[1]), max(anchor[1], active[1]))
def clip_paste_targets(
    matrix: ClipboardMatrix,
    bounds: SelectionBounds,
    row_count: int,
    column_count: int,
) -> tuple[tuple[GridAddress, str], ...]:
    top, bottom, left, right = bounds
    if len(matrix) == 1 and len(matrix[0]) == 1:
        return tuple(
            ((row, column), matrix[0][0]) for row in range(top, bottom + 1)
            for column in range(left, right + 1)
        )
    return tuple(
        ((top + row, left + column), value) for row, values in enumerate(matrix)
        for column, value in enumerate(values)
        if top + row < row_count and left + column < column_count
    )
def validate_paste_matrix(matrix: ClipboardMatrix, validator: Callable[[str], object] = parse_numeric_cell) -> None:
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
    _active_controller: ExcelLikeTableController | None = None
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
        self._mode: str = "none"
        self._edit_snapshot: dict[str, str] | None = None
        self._widget_positions: dict[object, GridAddress] = {}
        self._internal_focus_move = False
        self._after_idle_id: str | None = None
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
            for widget in (cell, entry):
                widget.bind("<Button-1>", lambda event, p=position: self._click(event, p))
                widget.bind("<Double-Button-1>",
                            lambda event, p=position: self._double_click(event, p))
                widget.bind("<B1-Motion>", self._drag)
            for seq, handler in (
                ("<Control-c>", self._copy), ("<Command-c>", self._copy),
                ("<Control-C>", self._copy), ("<Command-C>", self._copy),
                ("<Control-v>", self._paste), ("<Command-v>", self._paste),
                ("<Control-V>", self._paste), ("<Command-V>", self._paste),
                ("<Control-z>", self._undo_last), ("<Command-z>", self._undo_last),
                ("<Control-Z>", self._undo_last), ("<Command-Z>", self._undo_last),
                ("<Delete>", self._clear), ("<BackSpace>", self._clear),
                ("<F2>", self._edit_f2),
            ):
                entry.bind(seq, handler)
            for seq, direction in (
                ("<Tab>", "tab"), ("<Shift-Tab>", "shift-tab"),
                ("<ISO_Left_Tab>", "shift-tab"), ("<Return>", "enter"),
                ("<Shift-Return>", "shift-enter"), ("<KP_Enter>", "enter"),
                ("<Shift-KP_Enter>", "shift-enter"),
            ):
                entry.bind(seq, lambda event, d=direction: self._navigate(d))
            for seq, direction in (
                ("<Left>", "left"), ("<Right>", "right"),
                ("<Up>", "up"), ("<Down>", "down"),
            ):
                entry.bind(seq, lambda event, d=direction: self._arrow(d))
            entry.bind("<Escape>", self._escape)
            entry.bind("<FocusOut>", self._on_focus_out)
            entry.bind("<KeyPress>", lambda event, p=position: self._type_replace(event, p))
        for seq, handler in (
            ("<Command-c>", self._copy), ("<Command-C>", self._copy),
            ("<Command-v>", self._paste), ("<Command-V>", self._paste),
            ("<Command-z>", self._undo_last), ("<Command-Z>", self._undo_last),
            ("<Control-c>", self._copy), ("<Control-C>", self._copy),
            ("<Control-v>", self._paste), ("<Control-V>", self._paste),
            ("<Control-z>", self._undo_last), ("<Control-Z>", self._undo_last),
        ):
            self.table.table_frame.bind(seq, handler)
        for widget in (
            *self.table.header_cells.values(),
            *self.table.row_header_cells.values(),
            *self.table.static_cell_frames.values(),
        ):
            self._bind_clear_recursive(widget)
        self.table.table_frame.bind("<Button-1>", self._on_table_frame_click)
    def _bind_clear_recursive(self, widget) -> None:
        widget.bind("<Button-1>", self._clear_external_selection)
        for child in widget.winfo_children():
            self._bind_clear_recursive(child)
    def _on_table_frame_click(self, event) -> str:
        if event.widget is not self.table.table_frame:
            return ""
        self._clear_external_selection()
        return "break"
    def _mark_internal_focus_move(self) -> None:
        self._internal_focus_move = True
        self._after_idle_id = self.table.after_idle(self._reset_internal_focus_move)
    def _reset_internal_focus_move(self) -> None:
        self._internal_focus_move = False
        self._after_idle_id = None
    @property
    def selection_bounds(self) -> SelectionBounds | None:
        if self.anchor is None or self.active is None:
            return None
        return resolve_selection_bounds(self.anchor, self.active)
    def select(self, position: GridAddress, *, extend: bool = False) -> None:
        if position not in self._editable_positions:
            return
        self._commit_edit()
        prev = self.__class__._active_controller
        if prev is not None and prev is not self:
            try:
                if prev.table.winfo_exists():
                    prev._clear_external_selection()
            except Exception:
                pass
        self.__class__._active_controller = self
        if not extend or self.anchor is None:
            self.anchor = position
        self.active = position
        self._replace_pending = True
        self._mode = "selection"
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
    def _base_background_for_field(self, field_key: str) -> str:
        if hasattr(self.table, "is_field_invalid") and self.table.is_field_invalid(field_key):
            return TABLE_INVALID_BG
        return TABLE_EDITABLE_BG

    def _paint_selection(self) -> None:
        selected = set(self.selected_positions())
        for position in self._editable_positions:
            field_key = self.table.field_key_for_address(self._by_position[position])
            color = self._base_background_for_field(field_key)
            if position in selected:
                color = TABLE_SELECTED_BG
            if position == self.active:
                color = TABLE_ACTIVE_BG
            self.table.editable_entries[field_key].configure(background=color)
    def _entry_at(self, position: GridAddress):
        return self.table.editable_entries[
            self.table.field_key_for_address(self._by_position[position])
        ]
    def _click(self, event, position: GridAddress) -> str:
        same_active_selection = (
            self._mode == "selection"
            and self.active == position
            and self.anchor == position
            and not bool(event.state & 0x0001)
        )
        self.select(position, extend=bool(event.state & 0x0001))
        entry = self._entry_at(position)
        self._mark_internal_focus_move()
        entry.focus_set()
        if same_active_selection:
            self._enter_edit_mode(position)
        else:
            self._show_selection_caret_state(position)
        return "break"
    def _double_click(self, event, position: GridAddress) -> str:
        self.select(position, extend=False)
        entry = self._entry_at(position)
        self._mark_internal_focus_move()
        entry.focus_set()
        self._enter_edit_mode(position)
        return "break"
    def _show_selection_caret_state(self, position: GridAddress) -> None:
        entry = self._entry_at(position)
        entry.configure(insertontime=0)
        entry.selection_range(0, "end")
        entry.icursor("end")
    def _enter_edit_mode(self, position: GridAddress, *, caret: str = "end") -> None:
        if position not in self._editable_positions:
            return
        if self._mode == "edit" and self.active == position:
            return
        self._commit_edit()
        self._mode = "edit"
        self._replace_pending = False
        self._edit_snapshot = self.table.get_text_values()
        entry = self._entry_at(position)
        entry.selection_clear()
        entry.icursor(caret)
        entry.configure(insertontime=600)
    def _commit_edit(self) -> None:
        if self._mode != "edit":
            return
        snapshot = self._edit_snapshot
        self._mode = "selection" if self.active is not None else "none"
        self._edit_snapshot = None
        self._replace_pending = self.active is not None
        if snapshot is not None and self.table.get_text_values() != snapshot:
            self._undo.append(snapshot)
        if self.active is not None:
            self._show_selection_caret_state(self.active)
    def _cancel_edit(self) -> None:
        if self._mode != "edit":
            return
        snapshot = self._edit_snapshot
        self._mode = "selection" if self.active is not None else "none"
        self._edit_snapshot = None
        self._replace_pending = self.active is not None
        if snapshot is not None:
            self.table.set_values_batch(snapshot)
        if self.active is not None:
            self._show_selection_caret_state(self.active)
    def _edit_f2(self, _event=None) -> str:
        if self.active is not None:
            self._enter_edit_mode(self.active)
        return "break"
    def _drag(self, event) -> str:
        position = self._widget_positions.get(
            self.table.winfo_containing(event.x_root, event.y_root)
        )
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
        except (TclError, ValueError):
            return "break"
        targets = clip_paste_targets(
            matrix, self.selection_bounds, len(self.table.rows), len(self.table.columns)
        )
        self._apply({self._by_position[position]: value for position, value in targets})
        return "break"
    def _clear(self, _event=None) -> str:
        if self._mode == "edit":
            return ""
        self._apply(
            {self._by_position[position]: "" for position in self.selected_positions()}
        )
        return "break"
    def _apply(self, values: dict[tuple[str, str], str]) -> None:
        self._commit_edit()
        before = self.table.get_text_values()
        if self.table.set_address_values_batch(values):
            self._undo.append(before)
        self._mode = "selection" if self.active is not None else "none"
        self._replace_pending = self.active is not None
    def _undo_last(self, _event=None) -> str:
        self._commit_edit()
        if self._undo:
            self.table.set_values_batch(self._undo.pop())
        return "break"
    def _navigate(self, direction: str) -> str:
        self._commit_edit()
        current = self.active or self._editable_positions[0]
        target = resolve_next_cell(current, self._editable_positions, direction)
        self._mark_internal_focus_move()
        self.select(target)
        entry = self._entry_at(target)
        entry.focus_set()
        self._show_selection_caret_state(target)
        return "break"
    def _arrow(self, direction: str) -> str:
        if self._mode == "edit":
            return ""
        if not self._replace_pending or self.active is None:
            return ""
        row, col = self.active
        offsets = {"left": (0, -1), "right": (0, 1), "up": (-1, 0), "down": (1, 0)}
        if direction not in offsets:
            return ""
        row_delta, col_delta = offsets[direction]
        target = (row + row_delta, col + col_delta)
        if target not in self._editable_positions:
            return "break"
        self._mark_internal_focus_move()
        self.select(target)
        entry = self._entry_at(target)
        entry.focus_set()
        self._show_selection_caret_state(target)
        return "break"
    def _type_replace(self, event, position: GridAddress) -> str | None:
        if self._mode == "edit":
            return None
        if not self._replace_pending or position != self.active:
            return None
        if not event.char or not event.char.isprintable() or event.state & 0x000C:
            return None
        self._edit_snapshot = self.table.get_text_values()
        if self.table.set_address_values_batch({self._by_position[position]: event.char}):
            self._mode = "edit"
            self._replace_pending = False
        entry = self._entry_at(position)
        entry.icursor("end")
        entry.configure(insertontime=600)
        return "break"
    def _clear_selection(self, event=None) -> str:
        if self.__class__._active_controller is self:
            self.__class__._active_controller = None
        self.anchor = None
        self.active = None
        self._replace_pending = False
        self._mode = "none"
        self._edit_snapshot = None
        self._paint_selection()
        return "break"
    def _clear_external_selection(self, event=None) -> str:
        self._commit_edit()
        return self._clear_selection()
    def _escape(self, event=None) -> str:
        if self._mode == "edit":
            self._cancel_edit()
            return "break"
        return self._clear_selection()
    def _on_focus_out(self, event) -> None:
        if self._internal_focus_move:
            return
        try:
            if not self.table.winfo_exists():
                return
        except Exception:
            return
        self._clear_external_selection()
