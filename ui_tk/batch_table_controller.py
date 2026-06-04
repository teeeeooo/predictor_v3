"""Excel-like interaction controller for Tkinter batch tables."""

from __future__ import annotations

from collections.abc import Mapping

from ui_tk.batch_models import BatchColumnRole
from ui_tk.batch_table import (
    BatchTableSurface,
    GridAddress,
    SelectionBounds,
    editable_clear_targets,
    editable_paste_targets,
    positions_in_bounds,
    resolve_next_position,
    selection_bounds,
)
from ui_tk.excel_like_table_controller import (
    encode_selection_to_clipboard,
    parse_clipboard_matrix,
)
from ui_tk.layout_constants import (
    TABLE_ACTIVE_BG,
    TABLE_SELECTED_BG,
)


class BatchTableController:
    """Owns spreadsheet-like interaction for a row-per-case table surface."""

    def __init__(self, table: BatchTableSurface) -> None:
        self.table = table
        self.anchor: GridAddress | None = None
        self.active: GridAddress | None = None
        self._mode = "none"
        self._replace_pending = False
        self._edit_snapshot: list[dict[str, str]] | None = None
        self._undo: list[list[dict[str, str]]] = []
        self._widget_positions: dict[object, GridAddress] = {}
        self.refresh()

    @property
    def selection_bounds(self) -> SelectionBounds | None:
        if self.anchor is None or self.active is None:
            return None
        return selection_bounds(self.anchor, self.active)

    def selected_positions(self) -> tuple[GridAddress, ...]:
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
                for widget in (self.table.cell_frame(position), self.table.cell_widget(position)):
                    self._widget_positions[widget] = position
                    widget.bind("<Button-1>", lambda event, p=position: self._click(event, p))
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

    def select(self, position: GridAddress, *, extend: bool = False) -> None:
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
            ("<Control-c>", self._copy), ("<Command-c>", self._copy),
            ("<Control-C>", self._copy), ("<Command-C>", self._copy),
            ("<Control-v>", self._paste), ("<Command-v>", self._paste),
            ("<Control-V>", self._paste), ("<Command-V>", self._paste),
            ("<Control-z>", self._undo_last), ("<Command-z>", self._undo_last),
            ("<Control-Z>", self._undo_last), ("<Command-Z>", self._undo_last),
            ("<Delete>", self._clear), ("<BackSpace>", self._clear),
            ("<Tab>", lambda _event: self._navigate("tab")),
            ("<Shift-Tab>", lambda _event: self._navigate("shift-tab")),
            ("<ISO_Left_Tab>", lambda _event: self._navigate("shift-tab")),
            ("<Return>", lambda _event: self._navigate("enter")),
            ("<Shift-Return>", lambda _event: self._navigate("shift-enter")),
            ("<KP_Enter>", lambda _event: self._navigate("enter")),
            ("<Shift-KP_Enter>", lambda _event: self._navigate("shift-enter")),
            ("<F2>", self._edit_f2),
            ("<Escape>", self._escape),
        )

    def _click(self, event, position: GridAddress) -> str:
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
        if self.selection_bounds is None:
            return "break"
        rows = self._matrix_text()
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
        targets = editable_paste_targets(matrix, self.selection_bounds, self.table.column_roles())
        if targets:
            max_row = max(row for row, _column in targets) + 1
            self.table.ensure_row_count(max_row)
            self._apply(targets)
        return "break"

    def _clear(self, _event=None) -> str:
        if self._mode == "edit":
            return ""
        self._apply(editable_clear_targets(self.selected_positions(), self.table.column_roles()))
        return "break"

    def _undo_last(self, _event=None) -> str:
        self._commit_edit()
        if self._undo:
            self.table.set_text_rows(self._undo.pop())
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

    def _type_replace(self, event, position: GridAddress) -> str | None:
        if self._mode == "edit" or not self._replace_pending:
            return None
        if position != self.active or not self._is_editable(position):
            return "break"
        if not event.char or not event.char.isprintable() or event.state & 0x000C:
            return None
        self._edit_snapshot = self.table.get_text_rows()
        if self.table.set_positions_batch({position: event.char}):
            self._mode = "edit"
            self._replace_pending = False
            self.table.focus_widget(position).focus_set()
            widget = self.table.focus_widget(position)
            widget.icursor("end")
        return "break"

    def _edit_f2(self, _event=None) -> str:
        if self.active is not None and self._is_editable(self.active):
            self._enter_edit_mode(self.active)
        return "break"

    def _escape(self, _event=None) -> str:
        if self._mode == "edit" and self._edit_snapshot is not None:
            self.table.set_text_rows(self._edit_snapshot)
        self._mode = "selection" if self.active is not None else "none"
        self._edit_snapshot = None
        self._replace_pending = self.active is not None
        return "break"

    def _focus_out(self, _event=None) -> None:
        self._commit_edit()

    def _apply(self, values: Mapping[GridAddress, str]) -> None:
        self._commit_edit()
        if not values:
            return
        before = self.table.get_text_rows()
        if self.table.set_positions_batch(values):
            self._undo.append(before)
        self._mode = "selection" if self.active is not None else "none"
        self._replace_pending = self.active is not None

    def _commit_edit(self) -> None:
        if self._mode != "edit":
            return
        snapshot = self._edit_snapshot
        self._mode = "selection" if self.active is not None else "none"
        self._edit_snapshot = None
        self._replace_pending = self.active is not None
        if snapshot is not None and self.table.get_text_rows() != snapshot:
            self._undo.append(snapshot)

    def _enter_edit_mode(self, position: GridAddress) -> None:
        self._commit_edit()
        self._mode = "edit"
        self._replace_pending = False
        self._edit_snapshot = self.table.get_text_rows()
        widget = self.table.focus_widget(position)
        widget.selection_clear()
        widget.icursor("end")

    def _matrix_text(self) -> tuple[tuple[str, ...], ...]:
        bounds = self.selection_bounds
        if bounds is None:
            return ()
        top, bottom, left, right = bounds
        return tuple(
            tuple(self.table.text_at_position((row, column)) for column in range(left, right + 1))
            for row in range(top, bottom + 1)
        )

    def _show_selection_caret(self, position: GridAddress) -> None:
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

    def _position_exists(self, position: GridAddress) -> bool:
        row, column = position
        return 0 <= row < self.table.row_count() and 0 <= column < self.table.column_count()

    def _is_editable(self, position: GridAddress) -> bool:
        return self.table.column_roles()[position[1]] is BatchColumnRole.INPUT
