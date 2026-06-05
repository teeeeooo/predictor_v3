from types import SimpleNamespace

from ui_tk.table.controller import TkTableController
from ui_tk.table.roles import CellRole


class _FakeWidget:
    def __init__(self):
        self.background = ""
        self.focused = False
        self.cursor = None
        self.selection = None
        self.bindings = {}

    def bind(self, sequence, handler):
        self.bindings[sequence] = handler
        return None

    def configure(self, **kwargs):
        self.background = kwargs.get("background", self.background)

    def focus_set(self):
        self.focused = True

    def selection_range(self, *args):
        self.selection = args

    def selection_clear(self):
        self.selection = None

    def icursor(self, index):
        self.cursor = index


class _FakeSurface:
    keys = ("a", "b", "result")

    def __init__(self):
        self.roles = (CellRole.EDITABLE, CellRole.EDITABLE, CellRole.RESULT)
        self.rows = [{"a": "3500", "b": "900", "result": "4.939"}]
        self.clipboard = ""
        self.frames = {}
        self.widgets = {}
        self.changed = 0
        self._ensure_widgets()

    def row_count(self):
        return len(self.rows)

    def column_count(self):
        return len(self.roles)

    def cell_roles(self):
        return self.roles

    def ensure_row_count(self, count):
        while len(self.rows) < count:
            self.rows.append({"a": "", "b": "", "result": ""})
        self._ensure_widgets()

    def text_at_position(self, position):
        return self.rows[position[0]][self.keys[position[1]]]

    def set_positions_batch(self, values):
        changed = False
        for (row, column), value in values.items():
            if self.roles[column] is not CellRole.EDITABLE:
                continue
            key = self.keys[column]
            if self.rows[row][key] != value:
                self.rows[row][key] = value
                changed = True
        if changed:
            self.changed += 1
        return changed

    def snapshot(self):
        return [dict(row) for row in self.rows]

    def restore_snapshot(self, snapshot):
        self.rows = [dict(row) for row in snapshot]
        self._ensure_widgets()
        self.changed += 1

    def cell_frame(self, position):
        return self.frames[position]

    def cell_widget(self, position):
        return self.widgets[position]

    def focus_widget(self, position):
        return self.widgets[position] if self.roles[position[1]] is CellRole.EDITABLE else self.frames[position]

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


def test_controller_copies_selectable_result_cells():
    surface = _FakeSurface()
    controller = TkTableController(surface)

    controller.select((0, 0))
    controller.select((0, 2), extend=True)
    controller._copy()

    assert surface.clipboard == "3500\t900\t4.939"


def test_controller_paste_expands_rows_skips_result_and_undo_restores_original_rows():
    surface = _FakeSurface()
    controller = TkTableController(surface)
    surface.clipboard = "10\t20\tSHOULD_SKIP\n30\t40\tSHOULD_SKIP"

    controller.select((0, 0))
    controller._paste()

    assert surface.rows == [
        {"a": "10", "b": "20", "result": "4.939"},
        {"a": "30", "b": "40", "result": ""},
    ]

    controller.select((1, 2))
    controller._undo_last()

    assert surface.rows == [{"a": "3500", "b": "900", "result": "4.939"}]


def test_controller_selected_range_fill_paste_repeats_clipboard_row():
    surface = _FakeSurface()
    controller = TkTableController(surface)
    surface.ensure_row_count(4)
    surface.clipboard = "1\t2\tSHOULD_SKIP"

    controller.select((0, 0))
    controller.select((3, 2), extend=True)
    controller._paste()

    assert surface.rows == [
        {"a": "1", "b": "2", "result": "4.939"},
        {"a": "1", "b": "2", "result": ""},
        {"a": "1", "b": "2", "result": ""},
        {"a": "1", "b": "2", "result": ""},
    ]

    controller._undo_last()

    assert surface.rows == [
        {"a": "3500", "b": "900", "result": "4.939"},
        {"a": "", "b": "", "result": ""},
        {"a": "", "b": "", "result": ""},
        {"a": "", "b": "", "result": ""},
    ]


def test_controller_selected_range_single_cell_paste_fills_editable_cells_only():
    surface = _FakeSurface()
    controller = TkTableController(surface)
    surface.ensure_row_count(2)
    surface.clipboard = "x"

    controller.select((0, 0))
    controller.select((1, 2), extend=True)
    controller._paste()

    assert surface.rows == [
        {"a": "x", "b": "x", "result": "4.939"},
        {"a": "x", "b": "x", "result": ""},
    ]


def test_controller_clear_and_undo_are_grouped_and_active_cell_independent():
    surface = _FakeSurface()
    controller = TkTableController(surface)

    controller.select((0, 0))
    controller.select((0, 2), extend=True)
    controller._clear()
    controller.select((0, 2))
    controller._undo_last()

    assert surface.rows == [{"a": "3500", "b": "900", "result": "4.939"}]


def test_controller_click_type_replace_then_repeated_undo_without_focus_move():
    surface = _FakeSurface()
    controller = TkTableController(surface)

    controller.select((0, 0))
    assert controller._type_replace(SimpleNamespace(keysym="1", char="1", state=0), (0, 0)) == "break"
    surface.set_positions_batch({(0, 0): "100"})
    controller._commit_edit()
    surface.clipboard = "200"
    controller._paste()

    assert surface.rows[0]["a"] == "200"
    controller._undo_last()
    assert surface.rows[0]["a"] == "100"
    controller._undo_last()
    assert surface.rows[0]["a"] == "3500"


def test_controller_navigation_helpers_are_bound_to_visible_cells():
    surface = _FakeSurface()
    controller = TkTableController(surface)

    controller.select((0, 0))
    controller._navigate("tab")
    assert controller.active == (0, 1)
    controller._arrow("right")
    assert controller.active == (0, 2)
    assert controller._type_replace(SimpleNamespace(keysym="x", char="x", state=0), (0, 2)) == "break"
    assert surface.rows[0]["result"] == "4.939"
