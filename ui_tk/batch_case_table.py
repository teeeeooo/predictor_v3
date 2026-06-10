"""Tkinter row-per-case batch table surface."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from collections.abc import Callable, Iterable, Mapping

from ui_tk.batch.models import (
    BatchColumnRole,
    BatchProfileSpec,
    BatchTableModel,
)
from ui_tk.batch_table import GridAddress, batch_roles_to_cell_roles
from ui_tk.batch_table_controller import BatchTableController
from ui_tk.batch_table_viewport import BatchTableViewport
from ui_tk.layout_constants import (
    TABLE_BODY_FONT,
    TABLE_CELL_PADX,
    TABLE_CELL_PADY,
    TABLE_EDITABLE_BG,
    TABLE_GRID_COLOR,
    TABLE_HEADER_BG,
    TABLE_HEADER_FONT,
    TABLE_HEADER_PADY,
    TABLE_STATIC_BG,
    TABLE_STATIC_FG,
)

ValuesChangedCallback = Callable[[], None]
ROW_HEADER_WIDTH_CHARS = 4


class BatchCaseTable(ttk.Frame):
    """Row-per-case table with editable input columns and read-only results."""

    def __init__(
        self,
        master: tk.Misc,
        spec: BatchProfileSpec,
        *,
        values_changed_callback: ValuesChangedCallback | None = None,
        **kwargs: object,
    ) -> None:
        super().__init__(master, **kwargs)
        self.model = BatchTableModel(spec)
        self._values_changed_callback = values_changed_callback
        self._variables: list[dict[str, tk.StringVar]] = []
        self._cell_frames: dict[GridAddress, tk.Frame] = {}
        self._cell_widgets: dict[GridAddress, tk.Widget] = {}
        self._batch_depth = 0
        self._batch_changed = False
        self.interaction_controller: BatchTableController | None = None
        self._build_table()
        self.interaction_controller = BatchTableController(self)

    def row_count(self) -> int:
        return len(self.model.rows)

    def column_count(self) -> int:
        return len(self.model.spec.columns)

    def column_roles(self) -> tuple[BatchColumnRole, ...]:
        return tuple(column.role for column in self.model.spec.columns)

    def cell_roles(self):
        return batch_roles_to_cell_roles(self.column_roles())

    def row_header_texts(self) -> tuple[str, ...]:
        return tuple(str(index + 1) for index in range(len(self.model.rows)))

    def cell_frame(self, position: GridAddress) -> tk.Frame:
        return self._cell_frames[position]

    def cell_widget(self, position: GridAddress) -> tk.Widget:
        return self._cell_widgets[position]

    def focus_widget(self, position: GridAddress) -> tk.Widget:
        role = self.model.spec.columns[position[1]].role
        if role is BatchColumnRole.INPUT:
            return self._cell_widgets[position]
        return self._cell_frames[position]

    def default_cell_background(self, position: GridAddress) -> str:
        role = self.model.spec.columns[position[1]].role
        return TABLE_EDITABLE_BG if role is BatchColumnRole.INPUT else TABLE_STATIC_BG

    def set_values_changed_callback(
        self, callback: ValuesChangedCallback | None
    ) -> None:
        self._values_changed_callback = callback

    def add_row(self, values: Mapping[str, str] | None = None) -> None:
        self.model.add_row(values)
        self._rebuild_table()
        self.scroll_to_bottom()
        self._notify_changed()

    def ensure_row_count(self, count: int) -> None:
        changed = False
        while len(self.model.rows) < count:
            self.model.add_row()
            changed = True
        if changed:
            self._rebuild_table()

    def remove_last_row(self) -> None:
        before = len(self.model.rows)
        self.model.remove_row(len(self.model.rows) - 1)
        if len(self.model.rows) != before:
            self._rebuild_table()
            self._notify_changed()

    def input_rows(self) -> list[dict[str, str]]:
        return [self.model.input_values(index) for index in range(len(self.model.rows))]

    def set_row_results(self, row_index: int, values: Mapping[str, str]) -> None:
        self.model.set_results(row_index, values)
        for key in (*self.model.spec.result_keys, *self.model.spec.status_keys):
            self._variables[row_index][key].set(self.model.rows[row_index][key])

    def clear_results(self) -> None:
        self.model.clear_results()
        for row_index, row in enumerate(self.model.rows):
            for key in (*self.model.spec.result_keys, *self.model.spec.status_keys):
                self._variables[row_index][key].set(row[key])

    def text_at_position(self, position: GridAddress) -> str:
        row, column = position
        key = self.model.spec.columns[column].key
        return self.model.rows[row].get(key, "")

    def set_positions_batch(self, values: Mapping[GridAddress, str]) -> bool:
        editable = set(self.model.spec.input_keys)
        outermost = self._batch_depth == 0
        if outermost:
            self._batch_changed = False
        self._batch_depth += 1
        changed = False
        try:
            for (row, column), value in values.items():
                if row >= len(self.model.rows) or column >= len(self.model.spec.columns):
                    continue
                key = self.model.spec.columns[column].key
                if key not in editable:
                    continue
                if self.model.rows[row].get(key, "") == value:
                    continue
                self._variables[row][key].set(value)
                changed = True
        finally:
            self._batch_depth -= 1
        if outermost and (self._batch_changed or changed):
            self._batch_changed = False
            self._notify_changed()
        return changed

    def get_text_rows(self) -> list[dict[str, str]]:
        return [dict(row) for row in self.model.rows]

    def snapshot(self) -> list[dict[str, str]]:
        return self.get_text_rows()

    def restore_snapshot(self, snapshot: object) -> None:
        if not isinstance(snapshot, list):
            return
        normalized = self._normalize_rows(snapshot)
        if len(normalized) != len(self.model.rows):
            self.model.rows = normalized
            self._rebuild_table()
            self._notify_changed()
            return
        outermost = self._batch_depth == 0
        if outermost:
            self._batch_changed = False
        self._batch_depth += 1
        changed = False
        try:
            for row_index, row in enumerate(normalized):
                for key, value in row.items():
                    if self.model.rows[row_index].get(key, "") == value:
                        continue
                    self.model.rows[row_index][key] = value
                    self._variables[row_index][key].set(value)
                    changed = True
        finally:
            self._batch_depth -= 1
        if outermost and (changed or self._batch_changed):
            self._batch_changed = False
            self._notify_changed()

    def set_text_rows(self, rows: Iterable[Mapping[str, str]]) -> None:
        self.model.rows = self._normalize_rows(rows)
        self._rebuild_table()
        self._notify_changed()

    def _normalize_rows(self, rows: Iterable[Mapping[str, str]]) -> list[dict[str, str]]:
        normalized = []
        known = {column.key for column in self.model.spec.columns}
        for values in rows:
            row = {column.key: "" for column in self.model.spec.columns}
            row.update({key: str(value) for key, value in values.items() if key in known})
            normalized.append(row)
        return normalized or [{column.key: "" for column in self.model.spec.columns}]

    def _build_table(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.viewport_frame = BatchTableViewport(
            self,
            content_name="batch_table_surface",
            content_background=TABLE_GRID_COLOR,
        )
        self.viewport_frame.grid(row=0, column=0, sticky="nsew")
        self.table_frame = self.viewport_frame.content
        self.table_frame.surface_role = "table_frame"
        self.table_frame.layout_policy = "vertical_scroll_containment"
        self._rebuild_table()

    @property
    def scrollbar_visible(self) -> bool:
        return self.viewport_frame.scrollbar_visible

    def _rebuild_table(self) -> None:
        for child in self.table_frame.winfo_children():
            child.destroy()
        self._variables.clear()
        self._cell_frames.clear()
        self._cell_widgets.clear()
        self._build_headers()
        for row_index, row in enumerate(self.model.rows):
            self._build_row(row_index, row)
        if self.interaction_controller is not None:
            self.interaction_controller.refresh()
        self.viewport_frame.sync(self._visible_rows_height())

    def _build_headers(self) -> None:
        self.table_frame.columnconfigure(0, weight=0)
        corner = tk.Frame(self.table_frame, background=TABLE_HEADER_BG)
        corner.grid(row=0, column=0, sticky="nsew", padx=(0, 1), pady=(0, 1))
        corner.surface_role = "corner_header_cell"
        tk.Label(
            corner,
            text="#",
            width=ROW_HEADER_WIDTH_CHARS,
            background=TABLE_HEADER_BG,
            font=TABLE_HEADER_FONT,
        ).pack(fill=tk.BOTH, expand=True, padx=TABLE_CELL_PADX, pady=TABLE_HEADER_PADY)
        for column_index, column in enumerate(self.model.spec.columns):
            grid_column = column_index + 1
            self.table_frame.columnconfigure(grid_column, weight=1)
            cell = tk.Frame(self.table_frame, background=TABLE_HEADER_BG)
            cell.grid(row=0, column=grid_column, sticky="nsew", padx=(0, 1), pady=(0, 1))
            cell.surface_role = "header_cell"
            tk.Label(
                cell,
                text=column.label,
                width=column.width_chars,
                background=TABLE_HEADER_BG,
                font=TABLE_HEADER_FONT,
            ).pack(fill=tk.BOTH, expand=True, padx=TABLE_CELL_PADX, pady=TABLE_HEADER_PADY)

    def _build_row(self, row_index: int, row: Mapping[str, str]) -> None:
        variables: dict[str, tk.StringVar] = {}
        self._build_row_header(row_index)
        for column_index, column in enumerate(self.model.spec.columns):
            position = (row_index, column_index)
            variable = tk.StringVar(master=self, value=row.get(column.key, ""))
            variables[column.key] = variable
            is_input = column.role is BatchColumnRole.INPUT
            background = TABLE_EDITABLE_BG if is_input else TABLE_STATIC_BG
            cell = tk.Frame(self.table_frame, background=background, takefocus=1)
            cell.grid(
                row=row_index + 1,
                column=column_index + 1,
                sticky="nsew",
                padx=(0, 1),
                pady=(0, 1),
            )
            cell.surface_role = "editable_cell" if is_input else "result_cell"
            if is_input:
                widget = self._make_entry(cell, variable, row_index, column.key, column.width_chars)
            else:
                widget = tk.Label(
                    cell,
                    textvariable=variable,
                    width=column.width_chars,
                    anchor="center",
                    background=background,
                    foreground=TABLE_STATIC_FG,
                    font=TABLE_BODY_FONT,
                    takefocus=0,
                )
                widget.pack(fill=tk.BOTH, expand=True, padx=TABLE_CELL_PADX, pady=TABLE_CELL_PADY)
            self._cell_frames[position] = cell
            self._cell_widgets[position] = widget
        self._variables.append(variables)

    def _build_row_header(self, row_index: int) -> None:
        cell = tk.Frame(self.table_frame, background=TABLE_HEADER_BG)
        cell.grid(row=row_index + 1, column=0, sticky="nsew", padx=(0, 1), pady=(0, 1))
        cell.surface_role = "row_header_cell"
        tk.Label(
            cell,
            text=str(row_index + 1),
            width=ROW_HEADER_WIDTH_CHARS,
            anchor="center",
            background=TABLE_HEADER_BG,
            font=TABLE_HEADER_FONT,
        ).pack(fill=tk.BOTH, expand=True, padx=TABLE_CELL_PADX, pady=TABLE_CELL_PADY)

    def _make_entry(
        self,
        cell: tk.Frame,
        variable: tk.StringVar,
        row_index: int,
        key: str,
        width_chars: int,
    ) -> tk.Entry:
        variable.trace_add(
            "write",
            lambda *_args, row_index=row_index, key=key, variable=variable:
            self._handle_input_change(row_index, key, variable.get()),
        )
        entry = tk.Entry(
            cell,
            textvariable=variable,
            width=width_chars,
            relief=tk.FLAT,
            borderwidth=0,
            highlightthickness=0,
            background=TABLE_EDITABLE_BG,
            font=TABLE_BODY_FONT,
            justify="center",
        )
        entry.pack(fill=tk.BOTH, expand=True, padx=TABLE_CELL_PADX, pady=TABLE_CELL_PADY)
        entry.surface_role = "editable_entry"
        return entry

    def _visible_rows_height(self) -> int:
        visible_rows = max(1, len(self.model.spec.default_rows))
        bbox = self.table_frame.grid_bbox(0, 0, self.column_count(), visible_rows)
        if bbox:
            return max(1, bbox[3])
        return max(1, self.table_frame.winfo_reqheight())

    def scroll_to_bottom(self) -> None:
        self.viewport_frame.sync(self._visible_rows_height())
        self.viewport_frame.scroll_to_bottom()

    def _handle_input_change(self, row_index: int, key: str, value: str) -> None:
        if self.model.rows[row_index].get(key, "") == value:
            return
        self.model.set_cell(row_index, key, value)
        if self._batch_depth:
            self._batch_changed = True
            return
        self._notify_changed()

    def _notify_changed(self) -> None:
        if self._values_changed_callback is not None:
            self._values_changed_callback()
