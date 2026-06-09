"""Tk-bound Excel-like controller for registered table surfaces."""

from __future__ import annotations

from collections.abc import Mapping

from ui_tk.layout_constants import TABLE_ACTIVE_BG, TABLE_SELECTED_BG
from ui_tk.table.interaction_core import (
    CellAddress,
    SelectionBounds,
    UndoStack,
    copyable_positions_by_role,
    editable_clear_targets_by_role,
    editable_paste_targets_by_role,
    encode_selection_to_clipboard,
    is_replace_printable,
    parse_clipboard_matrix,
    positions_in_bounds,
    resolve_adjacent_position,
    resolve_next_position,
    selection_bounds,
)
from ui_tk.table.roles import is_mutable
from ui_tk.table.surface import TkTableSurface


class TkTableController:
    """Owns Excel-like interaction for one Tk table surface."""

    def __init__(self, table: TkTableSurface) -> None:
        self.table = table
        self.anchor: CellAddress | None = None
        self.active: CellAddress | None = None
        self._mode = "none"
        self._replace_pending = False
        self._edit_snapshot: object | None = None
        self._undo = UndoStack()
        self._widget_positions: dict[object, CellAddress] = {}
        self._mutating_programmatically = False
        self.refresh()

    @property
    def selection_bounds(self) -> SelectionBounds | None:
        if self.anchor is None or self.active is None:
            return None
        return selection_bounds(self.anchor, self.active)

    def selected_positions(self) -> tuple[CellAddress, ...]:
        if self.selection_bounds is None:
            return ()
        return positions_in_bounds(
            self.selection_bounds, self.table.row_count(), self.table.column_count()
        )

    def refresh(self) -> None:
        self._widget_positions.clear()
        for row in range(self.table.row_count()):
            for column in range(self.table.column_count()):
                position = (row, column)
                for widget in (
                    self.table.cell_frame(position),
                    self.table.cell_widget(position),
                ):
                    self._widget_positions[widget] = position
                    widget.bind(
                        "<Button-1>", lambda event, p=position: self._click(event, p)
                    )
                    widget.bind("<B1-Motion>", self._drag)
                    for seq, handler in self._key_handlers():
                        widget.bind(seq, handler)
                    widget.bind(
                        "<KeyPress>",
                        lambda event, p=position: self._type_replace(event, p),
                    )
                    if self._is_editable(position):
                        widget.bind("<FocusOut>", self._focus_out)
        self._clamp_active()
        self._paint_selection()

    def select(self, position: CellAddress, *, extend: bool = False) -> None:
        if not self._position_exists(position):
            return
        self._commit_edit()
        if not extend or self.anchor is None:
            self.anchor = position
        self.active = position
        self._mode = "selection"
        self._replace_pending = True
        self._paint_selection()

    def _key_handlers(self):
        return (
            ("<Control-c>", self._copy),
            ("<Command-c>", self._copy),
            ("<Control-C>", self._copy),
            ("<Command-C>", self._copy),
            ("<Control-v>", self._paste),
            ("<Command-v>", self._paste),
            ("<Control-V>", self._paste),
            ("<Command-V>", self._paste),
            ("<Control-z>", self._undo_last),
            ("<Command-z>", self._undo_last),
            ("<Control-Z>", self._undo_last),
            ("<Command-Z>", self._undo_last),
            ("<Delete>", self._clear),
            ("<BackSpace>", self._clear),
            ("<Tab>", lambda _event: self._navigate("tab")),
            ("<Shift-Tab>", lambda _event: self._navigate("shift-tab")),
            ("<ISO_Left_Tab>", lambda _event: self._navigate("shift-tab")),
            ("<Return>", lambda _event: self._navigate("enter")),
            ("<Shift-Return>", lambda _event: self._navigate("shift-enter")),
            ("<KP_Enter>", lambda _event: self._navigate("enter")),
            ("<Shift-KP_Enter>", lambda _event: self._navigate("shift-enter")),
            ("<Left>", lambda _event: self._arrow("left")),
            ("<Right>", lambda _event: self._arrow("right")),
            ("<Up>", lambda _event: self._arrow("up")),
            ("<Down>", lambda _event: self._arrow("down")),
            ("<F2>", self._edit_f2),
            ("<Escape>", self._escape),
        )

    def _click(self, event, position: CellAddress) -> str:
        self.select(position, extend=bool(event.state & 0x0001))
        self.table.focus_widget(position).focus_set()
        if self._is_editable(position):
            self._show_selection_caret(position)
        return "break"

    def _drag(self, event) -> str:
        widget = self.table.winfo_containing(event.x_root, event.y_root)
        position = self._widget_positions.get(widget)
        if position is not None:
            self.select(position, extend=True)
        return "break"

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
        except TclError:
            return "break"
        targets = editable_paste_targets_by_role(
            matrix, self.selection_bounds, self._cell_role
        )
        if targets:
            before = self.table.snapshot()
            max_row = max(row for row, _column in targets) + 1
            self.table.ensure_row_count(max_row)
            self._apply(targets, before=before)
        return "break"

    def _clear(self, _event=None) -> str:
        if self._mode == "edit":
            return ""
        self._apply(
            editable_clear_targets_by_role(self.selected_positions(), self._cell_role)
        )
        return "break"

    def _undo_last(self, _event=None) -> str:
        self._commit_edit()
        snapshot = self._undo.pop()
        if snapshot is not None:
            self._mutating_programmatically = True
            try:
                self.table.restore_snapshot(snapshot)
            finally:
                self._mutating_programmatically = False
            self._replace_pending = False
            self.refresh()
        return "break"

    def _navigate(self, direction: str) -> str:
        self._commit_edit()
        current = self.active or (0, 0)
        target = resolve_next_position(
            current, self.table.row_count(), self.table.column_count(), direction
        )
        self.select(target)
        self.table.focus_widget(target).focus_set()
        if self._is_editable(target):
            self._show_selection_caret(target)
        return "break"

    def _arrow(self, direction: str) -> str:
        if self._mode == "edit":
            return ""
        current = self.active or (0, 0)
        target = resolve_adjacent_position(
            current, self.table.row_count(), self.table.column_count(), direction
        )
        self.select(target)
        self.table.focus_widget(target).focus_set()
        if self._is_editable(target):
            self._show_selection_caret(target)
        return "break"

    def _type_replace(self, event, position: CellAddress) -> str | None:
        if self._mode == "edit" or not self._replace_pending:
            return None
        if position != self.active or not self._is_editable(position):
            return "break"
        if not is_replace_printable(event.keysym, event.char, event.state):
            return None
        self._edit_snapshot = self.table.snapshot()
        if self.table.set_positions_batch({position: event.char}):
            self._mode = "edit"
            self._replace_pending = False
            widget = self.table.focus_widget(position)
            widget.select_clear()
            widget.icursor("end")
        return "break"

    def _edit_f2(self, _event=None) -> str:
        if self.active is not None and self._is_editable(self.active):
            self._enter_edit_mode(self.active)
        return "break"

    def _escape(self, _event=None) -> str:
        if self._mode == "edit" and self._edit_snapshot is not None:
            self.table.restore_snapshot(self._edit_snapshot)
        self._mode = "selection" if self.active is not None else "none"
        self._edit_snapshot = None
        self._replace_pending = self.active is not None
        return "break"

    def _focus_out(self, _event=None) -> None:
        if not self._mutating_programmatically:
            self._commit_edit()

    def _apply(
        self, values: Mapping[CellAddress, str], *, before: object | None = None
    ) -> None:
        self._commit_edit()
        if not values:
            return
        snapshot = self.table.snapshot() if before is None else before
        self._mutating_programmatically = True
        try:
            changed = self.table.set_positions_batch(values)
        finally:
            self._mutating_programmatically = False
        if changed:
            self._undo.push(snapshot)
        self._mode = "selection" if self.active is not None else "none"
        self._replace_pending = self.active is not None

    def _commit_edit(self) -> None:
        if self._mode != "edit":
            return
        snapshot = self._edit_snapshot
        self._mode = "selection" if self.active is not None else "none"
        self._edit_snapshot = None
        self._replace_pending = self.active is not None
        if snapshot is not None and self.table.snapshot() != snapshot:
            self._undo.push(snapshot)

    def _enter_edit_mode(self, position: CellAddress) -> None:
        self._commit_edit()
        self._mode = "edit"
        self._replace_pending = False
        self._edit_snapshot = self.table.snapshot()
        widget = self.table.focus_widget(position)
        widget.selection_clear()
        widget.icursor("end")

    def _matrix_text(self) -> tuple[tuple[str, ...], ...]:
        bounds = self.selection_bounds
        if bounds is None:
            return ()
        positions = set(
            copyable_positions_by_role(
                bounds,
                self.table.row_count(),
                self.table.column_count(),
                self._cell_role,
            )
        )
        top, bottom, left, right = bounds
        rows: list[tuple[str, ...]] = []
        for row in range(top, bottom + 1):
            values = []
            for column in range(left, right + 1):
                position = (row, column)
                values.append(
                    self.table.text_at_position(position) if position in positions else ""
                )
            rows.append(tuple(values))
        return tuple(rows)

    def _show_selection_caret(self, position: CellAddress) -> None:
        widget = self.table.focus_widget(position)
        widget.selection_range(0, "end")
        widget.icursor("end")

    def _paint_selection(self) -> None:
        selected = set(self.selected_positions())
        for row in range(self.table.row_count()):
            for column in range(self.table.column_count()):
                position = (row, column)
                color = self.table.default_cell_background(position)
                if position in selected:
                    color = TABLE_SELECTED_BG
                if position == self.active:
                    color = TABLE_ACTIVE_BG
                self.table.cell_frame(position).configure(background=color)
                self.table.cell_widget(position).configure(background=color)
        for position in selected - {self.active}:
            if self._is_editable(position):
                self.table.cell_widget(position).configure(background=TABLE_SELECTED_BG)
        if self.active is not None and self._is_editable(self.active):
            self.table.cell_widget(self.active).configure(background=TABLE_ACTIVE_BG)

    def _clamp_active(self) -> None:
        for attr in ("anchor", "active"):
            position = getattr(self, attr)
            if position is not None and not self._position_exists(position):
                setattr(self, attr, None)
        if self.active is None:
            self._mode = "none"
            self._replace_pending = False

    def _position_exists(self, position: CellAddress) -> bool:
        row, column = position
        return 0 <= row < self.table.row_count() and 0 <= column < self.table.column_count()

    def _is_editable(self, position: CellAddress) -> bool:
        return is_mutable(self._cell_role(position))

    def _cell_role(self, position: CellAddress):
        resolver = getattr(self.table, "cell_role", None)
        if resolver is not None:
            return resolver(position)
        return self.table.cell_roles()[position[1]]
