"""Tkinter two-row matrix table surface for calculator batch workflows."""

from __future__ import annotations

import tkinter as tk
from collections.abc import Callable, Mapping
from tkinter import ttk

from apps.calculator.ui.batch.matrix_models import BatchMatrixSpec, MatrixCellKind
from apps.calculator.ui.batch.viewport import BatchTableViewport
from apps.calculator.ui.layout_constants import (
    BATCH_MATRIX_CASE_COLUMN_WIDTH_CHARS,
    BATCH_MATRIX_ROW_TYPE_COLUMN_WIDTH_CHARS,
    TABLE_GRID_COLOR,
)
from apps.calculator.ui.table.roles import CellRole
from apps.calculator.ui.table.cell_background import cell_background
from apps.calculator.ui.table.canvas_matrix_view import CanvasMatrixView
from apps.calculator.ui.table.canvas_binding import CanvasTableBinding


ValuesChangedCallback = Callable[[], None]


class BatchMatrixTable(ttk.Frame):
    """Two-row matrix table surface backed by BatchMatrixSpec.

    One logical case renders two physical rows.  Case and result values
    appear only on the first physical row; the second physical row uses
    real blank read-only cells.
    """

    def __init__(
        self,
        master: tk.Misc,
        spec: BatchMatrixSpec,
        *,
        values_changed_callback: ValuesChangedCallback | None = None,
        **kwargs: object,
    ) -> None:
        super().__init__(master, **kwargs)
        self.spec = spec
        self._values_changed_callback = values_changed_callback
        self.cases: list[dict[str, str]] = [
            dict(case) for case in self.spec.default_cases
        ] or [{}]
        self.interaction_controller = None
        self._build_table()

    # ---- TkTableSurface contract ----

    def row_count(self) -> int:
        return self.spec.physical_row_count(len(self.cases))

    def column_count(self) -> int:
        return self.spec.column_count

    def cell_role(self, position: tuple[int, int]) -> CellRole:
        kind = self.spec.resolve_cell(position).kind
        if kind is MatrixCellKind.INPUT:
            return CellRole.EDITABLE
        if kind is MatrixCellKind.NOT_APPLICABLE:
            return CellRole.DISABLED
        if kind is MatrixCellKind.RESULT:
            return CellRole.RESULT
        return CellRole.READONLY

    def cell_roles(self):
        """Broad column fallback; matrix uses cell_role(position)."""
        return tuple(CellRole.READONLY for _ in range(self.column_count()))

    def text_at_position(self, position: tuple[int, int]) -> str:
        logical = self.spec.logical_case_index_from_physical_row(position[0])
        case = self.cases[logical]
        return self.spec.display_text(position, case, case)

    def set_positions_batch(self, values: Mapping[tuple[int, int], str]) -> bool:
        changed = False
        for position, value in values.items():
            if not (0 <= position[0] < self.row_count() and 0 <= position[1] < self.column_count()):
                continue
            cell = self.spec.resolve_cell(position)
            if not cell.editable or cell.input_key is None:
                continue
            case = self.cases[cell.logical_case_index]
            if case.get(cell.input_key, "") != value:
                case[cell.input_key] = value
                changed = True
        if changed:
            self.canvas_view.refresh()
            self._notify_changed()
        return changed

    def snapshot(self):
        return self.spec.snapshot_cases(self.cases)

    def restore_snapshot(self, snapshot: object) -> None:
        if not isinstance(snapshot, (tuple, list)):
            return
        restored = self.spec.restore_cases(snapshot)
        if len(restored) != len(self.cases):
            self.cases = restored
            self._rebuild_table()
            self._notify_changed()
            return
        changed = False
        for case, values in zip(self.cases, restored):
            for key in (*self.spec.input_keys, *self.spec.result_keys):
                value = values.get(key, "")
                if case.get(key, "") != value:
                    case[key] = value
                    changed = True
        if changed:
            self.canvas_view.refresh()
            self._notify_changed()

    def focus_widget(self, position: tuple[int, int]) -> tk.Widget:
        return self.canvas_view.editor.focus_widget(position)

    def default_cell_background(self, position: tuple[int, int]) -> str:
        return cell_background(editable=self.spec.is_editable(position))

    def ensure_row_count(self, count: int) -> None:
        physical_rows_per_case = len(self.spec.physical_rows)
        logical_count = max(0, count + physical_rows_per_case - 1) // physical_rows_per_case
        changed = False
        while len(self.cases) < logical_count:
            self.cases.append({})
            changed = True
        if changed:
            self._rebuild_table()

    # ---- Logical-case operations ----

    def add_case(self, values: Mapping[str, str] | None = None) -> None:
        self.cases.append(dict(values) if values is not None else {})
        self._rebuild_table()
        self.scroll_to_bottom()
        self._notify_changed()

    def remove_case(self) -> None:
        if len(self.cases) <= 1:
            return
        self.cases.pop()
        self._rebuild_table()
        self._notify_changed()

    def set_values_changed_callback(
        self, callback: ValuesChangedCallback | None
    ) -> None:
        self._values_changed_callback = callback

    def table_export_data(self) -> tuple[tuple[str, ...], tuple[tuple[str, ...], ...]]:
        headers = tuple(self._header_label(c) for c in range(self.column_count()))
        rows = tuple(
            tuple(self.text_at_position((r, c)) for c in range(self.column_count()))
            for r in range(self.row_count())
        )
        return headers, rows

    def copy_all(self) -> bool:
        from apps.calculator.ui.table_clipboard import copy_table_to_clipboard

        headers, rows = self.table_export_data()
        return copy_table_to_clipboard(self, headers, rows)

    def set_result(
        self, logical_case_index: int, result_data: Mapping[str, str]
    ) -> None:
        if logical_case_index >= len(self.cases):
            return
        case = self.cases[logical_case_index]
        for key, value in result_data.items():
            case[key] = value
        self.repaint_case_backgrounds(logical_case_index)

    def repaint_case_backgrounds(self, logical_case_index: int) -> None:
        """Reapply semantic colors without disturbing the selection overlay."""
        self.canvas_view.refresh()

    def clear_results(self) -> None:
        for key in self.spec.result_keys:
            for case in self.cases:
                if key in case:
                    case[key] = ""
        self.canvas_view.refresh()

    def header_text_metrics(self, column_index: int) -> tuple[int, int, int]:
        """Return measured text, horizontal padding, and token content widths."""
        layout = self.canvas_view.layout
        text_width = layout.header_font.measure(self._header_label(column_index))
        horizontal_padding = 2 * layout.label_padx
        content_width = layout.header_font.measure("0" * self._header_width(column_index))
        return text_width, horizontal_padding, content_width

    # ---- Viewport helpers ----

    @property
    def scrollbar_visible(self) -> bool:
        return self.viewport_frame.scrollbar_visible

    def preferred_content_size(self) -> tuple[int, int]:
        """Return the matrix's natural table size for dialog initial fitting."""
        return self.viewport_frame.preferred_content_size()

    def scroll_to_bottom(self) -> None:
        self.viewport_frame.sync(self._visible_rows_height())
        self.viewport_frame.scroll_to_bottom()

    # ---- Construction ----

    def _build_table(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.viewport_frame = BatchTableViewport(
            self,
            content_name="batch_matrix_surface",
            content_background=TABLE_GRID_COLOR,
        )
        self.viewport_frame.grid(row=0, column=0, sticky="nsew")
        self.table_frame = self.viewport_frame.content
        self.table_frame.surface_role = "matrix_table_frame"
        self.table_frame.layout_policy = "vertical_scroll_containment"
        self.table_frame.columnconfigure(0, weight=1)
        self.canvas_view = CanvasMatrixView(
            self.table_frame, table=self,
            headers=tuple(self._header_label(col) for col in range(self.column_count())),
            widths=tuple(self._header_width(col) for col in range(self.column_count())),
            row_labels=None,
            weights=tuple(int(col >= self.spec.measurement_start_column) for col in range(self.column_count())),
            viewport=self.viewport_frame,
        )
        self.canvas_view.frame.grid(row=0, column=0, sticky="ew")
        self.table_presentation = CanvasTableBinding(lambda: self.canvas_view)
        self._rebuild_table()

    def _rebuild_table(self) -> None:
        self.canvas_view.refresh()
        if self.interaction_controller is not None:
            self.interaction_controller.refresh()
        self.viewport_frame.sync(self._visible_rows_height())

    def _header_label(self, column_index: int) -> str:
        if column_index == 0:
            return "Case"
        if column_index == 1:
            return "Row Type"
        if column_index < self.spec.result_start_column:
            point = self.spec.measurement_points[column_index - self.spec.measurement_start_column]
            return point.label
        key, label, _width = self.spec.result_metrics[column_index - self.spec.result_start_column]
        return label

    def _header_width(self, column_index: int) -> int:
        if column_index == 0:
            return max(BATCH_MATRIX_CASE_COLUMN_WIDTH_CHARS, len("Case"))
        if column_index == 1:
            return max(
                BATCH_MATRIX_ROW_TYPE_COLUMN_WIDTH_CHARS,
                len("Row Type"),
                *(len(label) for label in self.spec.row_type_labels.values()),
            )
        if column_index < self.spec.result_start_column:
            point = self.spec.measurement_points[column_index - self.spec.measurement_start_column]
            return point.width_chars
        _key, _label, width = self.spec.result_metrics[column_index - self.spec.result_start_column]
        return width

    def _visible_rows_height(self) -> int:
        return self.canvas_view.layout.height(max(1, self.row_count()))

    def _notify_changed(self) -> None:
        if self._values_changed_callback is not None:
            self._values_changed_callback()
