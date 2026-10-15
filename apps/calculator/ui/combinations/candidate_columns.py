"""Candidate-column projection using the shared metric grid and table controller."""
from dataclasses import replace
from tkinter import ttk

from apps.calculator.application.combinations.models import Candidate
from apps.calculator.application.combinations.service import validate_candidate, ValidationError
from apps.calculator.ui.metric_input_table import MetricInputTable
from apps.calculator.ui.table.controller import TkTableController
from apps.calculator.ui.table.roles import CellRole

PAGE_SIZE = 100


class CandidateColumnController(TkTableController):
    def _undo_last(self, event=None):
        if self.table.locked:
            return "break"
        return super()._undo_last(event)

    def _paste(self, event=None):
        # Numeric rectangles cannot spill into the optional test-name row.
        self.table.pasting_measurements = self.active is not None and self.selection_bounds[0] < 2
        try:
            return super()._paste(event)
        finally:
            self.table.pasting_measurements = False


class CandidateColumns(ttk.Frame):
    """One bounded point page; numeric rows never paste into another block."""

    def __init__(self, parent, point, candidates, offset, changed, *, title):
        super().__init__(parent)
        self.point, self.offset, self.changed = point, offset, changed
        self.title = title
        self.candidates = list(candidates)
        self.locked = False
        self.pasting_measurements = False
        self.show_names = False
        self.grid_table = None
        self.interaction_controller = None
        self.rebuild()
        self.interaction_controller = CandidateColumnController(self)
        self.bind_headers()

    @property
    def fields(self):
        return ("capacity", "power", "label") if self.show_names else ("capacity", "power")

    def rebuild(self):
        if self.grid_table:
            self.grid_table.destroy()
        columns = tuple((str(i), f"#{self.offset+i+1}") for i in range(len(self.candidates)))
        labels = dict(capacity=f"Capacity [{self.point.capacity_unit}]", power="Power [W]", label="시험명")
        self.grid_table = MetricInputTable(self, columns=columns, corner_label=self.title,
            rows=tuple((key, labels[key]) for key in self.fields),
            editable_cells={(key, col): f"{key}:{col}" for key in self.fields for col, _ in columns})
        self.grid_table.grid(row=0, column=0, sticky="w")
        self.grid_table.set_values_batch({f"{key}:{i}": getattr(candidate, key)
            for i, candidate in enumerate(self.candidates) for key in self.fields})
        self.grid_table.set_values_changed_callback(self.sync)
        self.present()
        if self.interaction_controller:
            self.interaction_controller.refresh()
            self.bind_headers()

    def bind_headers(self):
        for i, cell in enumerate(self.grid_table.header_cells.values()):
            for widget in (cell, *cell.winfo_children()):
                widget.bind("<Button-1>", lambda event, col=i: self.select_column(col, bool(event.state & 1)))

    def select_column(self, column, extend=False):
        controller = self.interaction_controller
        if not extend or controller.anchor is None:
            controller.select((0, column))
        controller.select((1, column), extend=True)
        self.focus_widget((0, column)).focus_set()
        return "break"

    def row_count(self):
        return len(self.fields)

    def column_count(self):
        return len(self.candidates)

    def cell_roles(self):
        return (CellRole.READONLY if self.locked else CellRole.EDITABLE,) * self.column_count()

    def cell_role(self, position):
        row, column = position
        if self.pasting_measurements and row >= 2:
            return CellRole.READONLY
        if not self.locked and 0 <= row < self.row_count() and 0 <= column < PAGE_SIZE:
            return CellRole.EDITABLE
        return CellRole.READONLY

    def text_at_position(self, position):
        return getattr(self.candidates[position[1]], self.fields[position[0]])

    def snapshot(self):
        return tuple(self.candidates)

    def restore_snapshot(self, snapshot):
        if self.locked or tuple(self.candidates) == tuple(snapshot):
            return
        shape_changed = len(snapshot) != len(self.candidates)
        self.candidates = list(snapshot)
        if shape_changed:
            self.rebuild()
        else:
            self.grid_table.set_values_changed_callback(None)
            self.grid_table.set_values_batch({f"{key}:{i}": getattr(candidate, key)
                for i, candidate in enumerate(self.candidates) for key in self.fields})
            self.grid_table.set_values_changed_callback(self.sync)
            self.present()
        self.changed()

    def set_positions_batch(self, values):
        if self.locked:
            return False
        values = {p: v for p, v in values.items() if self.cell_role(p) == CellRole.EDITABLE}
        if not values:
            return False
        updated = list(self.candidates)
        count = max(column for _, column in values) + 1
        updated.extend(Candidate() for _ in range(count - len(updated)))
        for (row, column), value in values.items():
            updated[column] = replace(updated[column], **{self.fields[row]: value})
        if updated == self.candidates:
            return False
        self.restore_snapshot(updated)
        return True

    def ensure_row_count(self, count):
        # Rows are physical measurements, never candidate growth.
        pass

    def sync(self):
        if self.locked:
            return
        text = self.grid_table.get_text_values()
        updated = [replace(candidate, **{key: text[f"{key}:{i}"] for key in self.fields})
                   for i, candidate in enumerate(self.candidates)]
        if updated != self.candidates:
            self.candidates = updated
            self.present()
            self.changed()

    def present(self):
        errors = {}
        for i, candidate in enumerate(self.candidates):
            marker = " ✓" if candidate.included else " · 제외"
            try:
                validate_candidate(candidate, self.point, self.offset+i+1)
            except ValidationError as exc:
                marker = " · 오류"
                for key in ("capacity", "power"):
                    errors[f"{key}:{i}"] = str(exc).replace(" · 행 ", " · 후보 #")
            self.grid_table.update_column_header(str(i), f"#{self.offset+i+1}{marker}")
        self.grid_table.clear_invalid_fields()
        self.grid_table.set_invalid_fields(errors)
        for entry in self.grid_table.editable_entries.values():
            entry.configure(state="readonly" if self.locked else "normal")
        if self.interaction_controller:
            self.interaction_controller.repaint_presentation()

    def names(self, visible):
        self.interaction_controller._commit_edit()
        self.show_names = visible
        self.rebuild()

    def lock(self, locked):
        self.locked = locked
        self.present()
        self.interaction_controller.refresh()

    def cell_frame(self, position):
        return self.grid_table.cell_frame(position)

    def cell_widget(self, position):
        return self.grid_table.cell_widget(position)

    def focus_widget(self, position):
        return self.grid_table.focus_widget(position)

    def default_cell_background(self, position):
        return self.grid_table.default_cell_background(position)
