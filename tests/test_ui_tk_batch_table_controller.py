from ui_tk.batch_models import BatchColumnRole
from ui_tk.batch_table import (
    editable_clear_targets,
    editable_paste_targets,
    positions_in_bounds,
    resolve_next_position,
)
from ui_tk.batch_table_controller import BatchTableController


class _FakeWidget:
    def __init__(self):
        self.background = ""

    def bind(self, *_args):
        return None

    def configure(self, **kwargs):
        self.background = kwargs.get("background", self.background)

    def focus_set(self):
        return None

    def selection_range(self, *_args):
        return None

    def selection_clear(self):
        return None

    def icursor(self, *_args):
        return None


class _FakeBatchTable:
    def __init__(self):
        self.roles = (BatchColumnRole.INPUT, BatchColumnRole.RESULT)
        self.rows = [{"input": "3500", "result": "4.939"}]
        self.frames = {(0, 0): _FakeWidget(), (0, 1): _FakeWidget()}
        self.widgets = {(0, 0): _FakeWidget(), (0, 1): _FakeWidget()}

    def row_count(self):
        return len(self.rows)

    def column_count(self):
        return len(self.roles)

    def column_roles(self):
        return self.roles

    def ensure_row_count(self, count):
        while len(self.rows) < count:
            self.rows.append({"input": "", "result": ""})

    def text_at_position(self, position):
        key = "input" if position[1] == 0 else "result"
        return self.rows[position[0]][key]

    def set_positions_batch(self, values):
        changed = False
        for (row, column), value in values.items():
            if column != 0:
                continue
            if self.rows[row]["input"] != value:
                self.rows[row]["input"] = value
                changed = True
        return changed

    def get_text_rows(self):
        return [dict(row) for row in self.rows]

    def set_text_rows(self, rows):
        self.rows = [dict(row) for row in rows]

    def cell_frame(self, position):
        return self.frames[position]

    def cell_widget(self, position):
        return self.widgets[position]

    def focus_widget(self, position):
        return self.widgets[position]

    def default_cell_background(self, _position):
        return ""

    def winfo_containing(self, *_args):
        return None


def test_batch_table_paste_targets_skip_read_only_result_columns():
    roles = (
        BatchColumnRole.INPUT,
        BatchColumnRole.INPUT,
        BatchColumnRole.RESULT,
        BatchColumnRole.RESULT,
    )

    targets = editable_paste_targets(
        (("A", "B", "C", "D"),),
        (0, 0, 0, 3),
        roles,
    )

    assert targets == {(0, 0): "A", (0, 1): "B"}


def test_batch_table_paste_from_result_column_does_not_mutate_results():
    roles = (
        BatchColumnRole.INPUT,
        BatchColumnRole.RESULT,
        BatchColumnRole.RESULT,
    )

    assert editable_paste_targets((("4.939",),), (0, 0, 1, 1), roles) == {}


def test_batch_table_single_cell_paste_fills_editable_selection_only():
    roles = (
        BatchColumnRole.INPUT,
        BatchColumnRole.INPUT,
        BatchColumnRole.RESULT,
    )

    targets = editable_paste_targets((("3500",),), (0, 2, 0, 2), roles)

    assert targets == {
        (0, 0): "3500",
        (0, 1): "3500",
        (1, 0): "3500",
        (1, 1): "3500",
        (2, 0): "3500",
        (2, 1): "3500",
    }


def test_batch_table_clear_targets_skip_read_only_result_columns():
    roles = (
        BatchColumnRole.INPUT,
        BatchColumnRole.RESULT,
        BatchColumnRole.INPUT,
    )

    targets = editable_clear_targets(((0, 0), (0, 1), (0, 2)), roles)

    assert targets == {(0, 0): "", (0, 2): ""}


def test_batch_table_positions_in_bounds_include_result_cells_for_copy():
    assert positions_in_bounds((0, 1, 1, 2), row_count=3, column_count=4) == (
        (0, 1),
        (0, 2),
        (1, 1),
        (1, 2),
    )


def test_batch_table_navigation_moves_across_all_visible_cells():
    assert resolve_next_position((0, 1), 2, 3, "tab") == (0, 2)
    assert resolve_next_position((0, 2), 2, 3, "tab") == (1, 0)
    assert resolve_next_position((1, 0), 2, 3, "shift-tab") == (0, 2)
    assert resolve_next_position((1, 2), 2, 3, "enter") == (0, 2)


def test_batch_table_controller_undo_restores_grouped_clear_without_mutating_result():
    table = _FakeBatchTable()
    controller = BatchTableController(table)

    controller.select((0, 0))
    controller.select((0, 1), extend=True)
    controller._clear()

    assert table.rows == [{"input": "", "result": "4.939"}]

    controller._undo_last()

    assert table.rows == [{"input": "3500", "result": "4.939"}]
