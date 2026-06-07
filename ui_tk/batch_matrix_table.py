"""Tkinter two-row matrix table surface for calculator batch workflows."""

from __future__ import annotations

import tkinter as tk
from collections.abc import Callable, Mapping
from tkinter import ttk

from ui_tk.batch_matrix_models import BatchMatrixSpec, MatrixCellKind
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
from ui_tk.table.roles import CellRole

ValuesChangedCallback = Callable[[], None]
CASE_COLUMN_WIDTH_CHARS = 4


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
        self._variables: list[dict[str, tk.StringVar]] = []
        self._cell_frames: dict[tuple[int, int], tk.Frame] = {}
        self._cell_widgets: dict[tuple[int, int], tk.Widget] = {}
        self._batch_depth = 0
        self._batch_changed = False
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
        outermost = self._batch_depth == 0
        if outermost:
            self._batch_changed = False
        self._batch_depth += 1
        changed = False
        try:
            for position, value in values.items():
                cell = self.spec.resolve_cell(position)
                if not cell.editable or cell.input_key is None:
                    continue
                logical = cell.logical_case_index
                if logical >= len(self.cases):
                    continue
                if self.cases[logical].get(cell.input_key, "") == value:
                    continue
                self.cases[logical][cell.input_key] = value
                if logical < len(self._variables):
                    var = self._variables[logical].get(cell.input_key)
                    if var is not None:
                        var.set(value)
                changed = True
        finally:
            self._batch_depth -= 1
        if outermost and (self._batch_changed or changed):
            self._batch_changed = False
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
        # same shape: in-place update to preserve widget continuity
        outermost = self._batch_depth == 0
        if outermost:
            self._batch_changed = False
        self._batch_depth += 1
        changed = False
        try:
            for logical_index, case in enumerate(restored):
                for key, value in case.items():
                    if self.cases[logical_index].get(key, "") == value:
                        continue
                    self.cases[logical_index][key] = value
                    var = self._variables[logical_index].get(key)
                    if var is not None:
                        var.set(value)
                    changed = True
                # snapshot에 없는 known key는 빈 문자열로 갱신
                for key in (*self.spec.input_keys, *self.spec.result_keys):
                    if key not in case:
                        if self.cases[logical_index].get(key, "") != "":
                            self.cases[logical_index][key] = ""
                            var = self._variables[logical_index].get(key)
                            if var is not None:
                                var.set("")
                            changed = True
        finally:
            self._batch_depth -= 1
        if outermost and (changed or self._batch_changed):
            self._batch_changed = False
            self._notify_changed()

    def cell_frame(self, position: tuple[int, int]) -> tk.Frame:
        return self._cell_frames[position]

    def cell_widget(self, position: tuple[int, int]) -> tk.Widget:
        return self._cell_widgets[position]

    def focus_widget(self, position: tuple[int, int]) -> tk.Widget:
        if self.spec.is_editable(position):
            return self._cell_widgets[position]
        return self._cell_frames[position]

    def default_cell_background(self, position: tuple[int, int]) -> str:
        return TABLE_EDITABLE_BG if self.spec.is_editable(position) else TABLE_STATIC_BG

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

    def set_result(
        self, logical_case_index: int, result_data: Mapping[str, str]
    ) -> None:
        if logical_case_index >= len(self.cases):
            return
        case = self.cases[logical_case_index]
        for key, value in result_data.items():
            case[key] = value
        if logical_case_index < len(self._variables):
            for key, value in result_data.items():
                var = self._variables[logical_case_index].get(key)
                if var is not None:
                    var.set(value)

    def clear_results(self) -> None:
        for key in self.spec.result_keys:
            for case in self.cases:
                if key in case:
                    case[key] = ""
        for logical_index, vars_dict in enumerate(self._variables):
            for key in self.spec.result_keys:
                var = vars_dict.get(key)
                if var is not None:
                    var.set("")

    # ---- Viewport helpers ----

    @property
    def scrollbar_visible(self) -> bool:
        return self.viewport_frame.scrollbar_visible

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
        self._rebuild_table()

    def _rebuild_table(self) -> None:
        for child in self.table_frame.winfo_children():
            child.destroy()
        self._variables.clear()
        self._cell_frames.clear()
        self._cell_widgets.clear()
        self._build_headers()
        for logical_index, case in enumerate(self.cases):
            self._build_case_rows(logical_index, case)
        if self.interaction_controller is not None:
            self.interaction_controller.refresh()
        self.viewport_frame.sync(self._visible_rows_height())

    def _build_headers(self) -> None:
        # column headers (no separate row-header corner cell; Case is column 0)
        for column_index in range(self.spec.column_count):
            grid_column = column_index
            self.table_frame.columnconfigure(grid_column, weight=1)
            cell = tk.Frame(self.table_frame, background=TABLE_HEADER_BG)
            cell.grid(row=0, column=grid_column, sticky="nsew", padx=(0, 1), pady=(0, 1))
            cell.surface_role = "header_cell"
            label_text = self._header_label(column_index)
            width_chars = self._header_width(column_index)
            tk.Label(
                cell,
                text=label_text,
                width=width_chars,
                background=TABLE_HEADER_BG,
                font=TABLE_HEADER_FONT,
            ).pack(fill=tk.BOTH, expand=True, padx=TABLE_CELL_PADX, pady=TABLE_HEADER_PADY)

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
            return CASE_COLUMN_WIDTH_CHARS
        if column_index == 1:
            return max(len(label) for label in self.spec.row_type_labels.values())
        if column_index < self.spec.result_start_column:
            point = self.spec.measurement_points[column_index - self.spec.measurement_start_column]
            return point.width_chars
        _key, _label, width = self.spec.result_metrics[column_index - self.spec.result_start_column]
        return width

    def _build_case_rows(self, logical_index: int, case: Mapping[str, str]) -> None:
        base_row = logical_index * len(self.spec.physical_rows)
        variables: dict[str, tk.StringVar] = {}
        self._variables.append(variables)
        for offset in range(len(self.spec.physical_rows)):
            physical_row = base_row + offset
            self._build_physical_row(physical_row, logical_index, case, variables)

    def _build_physical_row(
        self,
        physical_row: int,
        logical_index: int,
        case: Mapping[str, str],
        variables: dict[str, tk.StringVar],
    ) -> None:
        for column_index in range(self.spec.column_count):
            position = (physical_row, column_index)
            cell = self.spec.resolve_cell(position)
            is_editable = cell.editable and cell.input_key is not None
            background = TABLE_EDITABLE_BG if is_editable else TABLE_STATIC_BG

            cell_frame = tk.Frame(self.table_frame, background=background, takefocus=1)
            cell_frame.grid(
                row=physical_row + 1,
                column=column_index,
                sticky="nsew",
                padx=(0, 1),
                pady=(0, 1),
            )
            cell_frame.surface_role = "editable_cell" if is_editable else "static_cell"
            self._cell_frames[position] = cell_frame

            if is_editable and cell.input_key is not None:
                var = tk.StringVar(master=self, value=case.get(cell.input_key, ""))
                variables[cell.input_key] = var
                var.trace_add(
                    "write",
                    lambda *_args, logical=logical_index, key=cell.input_key, variable=var:
                    self._handle_input_change(logical, key, variable.get()),
                )
                widget = self._make_entry(cell_frame, var, self._header_width(column_index))
            else:
                text = self.spec.display_text(position, case, case)
                widget = tk.Label(
                    cell_frame,
                    text=text,
                    width=self._header_width(column_index),
                    anchor="center",
                    background=background,
                    foreground=TABLE_STATIC_FG,
                    font=TABLE_BODY_FONT,
                    takefocus=0,
                )
                widget.pack(fill=tk.BOTH, expand=True, padx=TABLE_CELL_PADX, pady=TABLE_CELL_PADY)
                if cell.result_key is not None:
                    # Result labels may be updated later via set_result.
                    # Store a StringVar so set_result can reach the widget.
                    var = tk.StringVar(master=self, value=text)
                    variables[cell.result_key] = var
                    widget.configure(textvariable=var)

            self._cell_widgets[position] = widget

    def _make_entry(
        self,
        cell: tk.Frame,
        variable: tk.StringVar,
        width_chars: int,
    ) -> tk.Entry:
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
        visible_rows = max(1, len(self.cases) * len(self.spec.physical_rows))
        bbox = self.table_frame.grid_bbox(0, 0, self.column_count() - 1, visible_rows)
        if bbox:
            return max(1, bbox[3])
        return max(1, self.table_frame.winfo_reqheight())

    def _handle_input_change(self, logical_index: int, key: str, value: str) -> None:
        if self.cases[logical_index].get(key, "") == value:
            return
        self.cases[logical_index][key] = value
        if self._batch_depth:
            self._batch_changed = True
            return
        self._notify_changed()

    def _notify_changed(self) -> None:
        if self._values_changed_callback is not None:
            self._values_changed_callback()
