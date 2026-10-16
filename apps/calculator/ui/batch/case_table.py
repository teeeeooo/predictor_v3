"""Tkinter row-per-case batch table surface."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from collections.abc import Callable, Iterable, Mapping

from apps.calculator.ui.batch.models import (
    BatchColumnRole,
    BatchProfileSpec,
    BatchTableModel,
)
from apps.calculator.ui.batch.compat_table import GridAddress, batch_roles_to_cell_roles
from apps.calculator.ui.batch.table_controller import BatchTableController
from apps.calculator.ui.batch.viewport import BatchTableViewport
from apps.calculator.ui.layout_constants import TABLE_GRID_COLOR
from apps.calculator.ui.table.cell_background import cell_background
from apps.calculator.ui.table.canvas_matrix_view import CanvasMatrixView
from apps.calculator.ui.table.canvas_binding import CanvasTableBinding


ValuesChangedCallback = Callable[[], None]
ROW_HEADER_WIDTH_CHARS = 4


class BatchCaseTable(ttk.Frame):
    """Row-per-case table with editable input columns and read-only results."""

    reserve_vertical_scrollbar = False

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

    def cell_role(self, position):
        return self.cell_roles()[position[1]]

    def focus_widget(self, position: GridAddress) -> tk.Widget:
        return self.canvas_view.editor.focus_widget(position)

    def default_cell_background(self, position: GridAddress) -> str:
        role = self.model.spec.columns[position[1]].role
        return cell_background(editable=role is BatchColumnRole.INPUT)

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
        self.canvas_view.refresh()

    def clear_results(self) -> None:
        self.model.clear_results()
        self.canvas_view.refresh()

    def text_at_position(self, position: GridAddress) -> str:
        row, column = position
        key = self.model.spec.columns[column].key
        return self.model.rows[row].get(key, "")

    def set_positions_batch(self, values: Mapping[GridAddress, str]) -> bool:
        changed = False
        for (row, column), value in values.items():
            if not (0 <= row < self.row_count() and 0 <= column < self.column_count()):
                continue
            key = self.model.spec.columns[column].key
            if key not in self.model.spec.input_keys or self.model.rows[row].get(key, "") == value:
                continue
            self.model.set_cell(row, key, value)
            changed = True
        if changed:
            self.canvas_view.refresh()
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
        changed = normalized != self.model.rows
        if changed:
            for row, values in zip(self.model.rows, normalized):
                row.update(values)
            self.canvas_view.refresh()
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
            reserve_vertical_scrollbar=self.reserve_vertical_scrollbar,
        )
        self.viewport_frame.grid(row=0, column=0, sticky="nsew")
        self.table_frame = self.viewport_frame.content
        self.table_frame.surface_role = "table_frame"
        self.table_frame.layout_policy = "vertical_scroll_containment"
        self.table_frame.columnconfigure(0, weight=1)
        self.canvas_view = CanvasMatrixView(
            self.table_frame, table=self,
            headers=tuple(column.label for column in self.model.spec.columns),
            widths=(ROW_HEADER_WIDTH_CHARS, *(column.width_chars for column in self.model.spec.columns)),
            row_labels=lambda row: str(row+1), corner="#",
            weights=(0, *(1 for _ in self.model.spec.columns)),
            viewport=self.viewport_frame,
        )
        self.canvas_view.frame.grid(row=0, column=0, sticky="ew")
        self.table_presentation = CanvasTableBinding(lambda: self.canvas_view)
        self._rebuild_table()

    @property
    def scrollbar_visible(self) -> bool:
        return self.viewport_frame.scrollbar_visible

    def _rebuild_table(self) -> None:
        self.canvas_view.refresh()
        if self.interaction_controller is not None:
            self.interaction_controller.refresh()
        self.viewport_frame.sync(self._visible_rows_height())

    def _visible_rows_height(self) -> int:
        visible_rows = min(self.row_count(), max(1, len(self.model.spec.default_rows)))
        return self.canvas_view.layout.height(visible_rows)

    def scroll_to_bottom(self) -> None:
        self.viewport_frame.sync(self._visible_rows_height())
        self.viewport_frame.scroll_to_bottom()

    def _notify_changed(self) -> None:
        if self._values_changed_callback is not None:
            self._values_changed_callback()
