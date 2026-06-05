from ui_tk.batch_models import BatchColumnRole
from ui_tk.batch_table import (
    batch_roles_to_cell_roles,
    editable_clear_targets,
    editable_paste_targets,
    positions_in_bounds,
    resolve_adjacent_position,
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
        self.roles = (BatchColumnRole.INPUT, BatchColumnRole.INPUT, BatchColumnRole.RESULT)
        self.rows = [{"a": "3500", "b": "900", "result": "4.939"}]
        self.clipboard = ""
        self.frames = {}
        self.widgets = {}
        self._ensure_widgets()

    def row_count(self):
        return len(self.rows)

    def column_count(self):
        return len(self.roles)

    def column_roles(self):
        return self.roles

    def cell_roles(self):
        return batch_roles_to_cell_roles(self.roles)

    def ensure_row_count(self, count):
        while len(self.rows) < count:
            self.rows.append({"a": "", "b": "", "result": ""})
        self._ensure_widgets()

    def text_at_position(self, position):
        key = ("a", "b", "result")[position[1]]
        return self.rows[position[0]][key]

    def set_positions_batch(self, values):
        changed = False
        for (row, column), value in values.items():
            if column not in (0, 1):
                continue
            key = ("a", "b")[column]
            if self.rows[row][key] != value:
                self.rows[row][key] = value
                changed = True
        return changed

    def get_text_rows(self):
        return [dict(row) for row in self.rows]

    def snapshot(self):
        return self.get_text_rows()

    def restore_snapshot(self, snapshot):
        self.rows = [dict(row) for row in snapshot]
        self._ensure_widgets()

    def set_text_rows(self, rows):
        self.rows = [dict(row) for row in rows]
        self._ensure_widgets()

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

    def clipboard_clear(self):
        self.clipboard = ""

    def clipboard_append(self, text):
        self.clipboard = text

    def clipboard_get(self):
        return self.clipboard

    def _ensure_widgets(self):
        for row in range(len(self.rows)):
            for column in range(len(self.roles)):
                self.frames.setdefault((row, column), _FakeWidget())
                self.widgets.setdefault((row, column), _FakeWidget())


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


def test_batch_table_selected_range_fill_paste_repeats_clipboard_row():
    roles = (
        BatchColumnRole.INPUT,
        BatchColumnRole.INPUT,
        BatchColumnRole.RESULT,
    )

    targets = editable_paste_targets((("10", "20", "SHOULD_SKIP"),), (0, 2, 0, 2), roles)

    assert targets == {
        (0, 0): "10",
        (0, 1): "20",
        (1, 0): "10",
        (1, 1): "20",
        (2, 0): "10",
        (2, 1): "20",
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


def test_batch_table_arrow_navigation_clamps_to_adjacent_visible_cell():
    assert resolve_adjacent_position((1, 1), 3, 3, "left") == (1, 0)
    assert resolve_adjacent_position((1, 1), 3, 3, "right") == (1, 2)
    assert resolve_adjacent_position((1, 1), 3, 3, "up") == (0, 1)
    assert resolve_adjacent_position((1, 1), 3, 3, "down") == (2, 1)
    assert resolve_adjacent_position((0, 0), 3, 3, "left") == (0, 0)


def test_batch_table_controller_undo_restores_grouped_clear_without_mutating_result():
    table = _FakeBatchTable()
    controller = BatchTableController(table)

    controller.select((0, 0))
    controller.select((0, 2), extend=True)
    controller._clear()

    assert table.rows == [{"a": "", "b": "", "result": "4.939"}]

    controller._undo_last()

    assert table.rows == [{"a": "3500", "b": "900", "result": "4.939"}]


def test_batch_table_controller_undo_is_global_not_active_cell_local():
    table = _FakeBatchTable()
    controller = BatchTableController(table)

    controller.select((0, 0))
    controller.select((0, 1), extend=True)
    controller._clear()
    controller.select((0, 2))
    controller._undo_last()

    assert table.rows == [{"a": "3500", "b": "900", "result": "4.939"}]


def test_batch_table_controller_single_column_paste_fills_multiple_rows():
    table = _FakeBatchTable()
    controller = BatchTableController(table)
    table.clipboard = "10\n20\n30"

    controller.select((0, 0))
    controller._paste()

    assert table.rows == [
        {"a": "10", "b": "900", "result": "4.939"},
        {"a": "20", "b": "", "result": ""},
        {"a": "30", "b": "", "result": ""},
    ]


def test_batch_table_controller_multi_column_paste_skips_result_column():
    table = _FakeBatchTable()
    controller = BatchTableController(table)
    table.clipboard = "10\t20\tSHOULD_NOT_SET\n30\t40\tSHOULD_NOT_SET"

    controller.select((0, 0))
    controller._paste()

    assert table.rows == [
        {"a": "10", "b": "20", "result": "4.939"},
        {"a": "30", "b": "40", "result": ""},
    ]


def test_batch_table_controller_selected_range_fill_paste_repeats_clipboard_row():
    table = _FakeBatchTable()
    table.ensure_row_count(4)
    controller = BatchTableController(table)
    table.clipboard = "1\t2\tSHOULD_SKIP"

    controller.select((0, 0))
    controller.select((3, 2), extend=True)
    controller._paste()

    assert table.rows == [
        {"a": "1", "b": "2", "result": "4.939"},
        {"a": "1", "b": "2", "result": ""},
        {"a": "1", "b": "2", "result": ""},
        {"a": "1", "b": "2", "result": ""},
    ]

    controller._undo_last()

    assert table.rows == [
        {"a": "3500", "b": "900", "result": "4.939"},
        {"a": "", "b": "", "result": ""},
        {"a": "", "b": "", "result": ""},
        {"a": "", "b": "", "result": ""},
    ]
