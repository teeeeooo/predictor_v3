from ui_tk.batch.matrix_models import (
    CSEC,
    CSPF,
    DECLARED_CAPACITY,
    FULL_CAPACITY,
    FULL_POWER,
    HALF_CAPACITY,
    HALF_POWER,
    HONG_KONG_CSPF_MATRIX_SPEC,
    MatrixCellKind,
)
from ui_tk.table.controller import TkTableController
from ui_tk.table.roles import CellRole


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


class _FakeMatrixSurface:
    def __init__(self):
        self.spec = HONG_KONG_CSPF_MATRIX_SPEC
        self.cases = [
            {
                DECLARED_CAPACITY: "3500",
                FULL_CAPACITY: "3600",
                FULL_POWER: "900",
                HALF_CAPACITY: "1700",
                HALF_POWER: "380",
                CSPF: "4.939",
                CSEC: "729.0",
            }
        ]
        self.clipboard = ""
        self.frames = {}
        self.widgets = {}
        self._ensure_widgets()

    def row_count(self):
        return self.spec.physical_row_count(len(self.cases))

    def column_count(self):
        return self.spec.column_count

    def cell_roles(self):
        return tuple(CellRole.READONLY for _column in range(self.column_count()))

    def cell_role(self, position):
        kind = self.spec.resolve_cell(position).kind
        if kind is MatrixCellKind.INPUT:
            return CellRole.EDITABLE
        if kind is MatrixCellKind.NOT_APPLICABLE:
            return CellRole.DISABLED
        if kind is MatrixCellKind.RESULT:
            return CellRole.RESULT
        return CellRole.READONLY

    def ensure_row_count(self, count):
        logical_count = (max(0, count) + 1) // 2
        while len(self.cases) < logical_count:
            self.cases.append({})
        self._ensure_widgets()

    def text_at_position(self, position):
        logical_case = self.spec.logical_case_index_from_physical_row(position[0])
        case = self.cases[logical_case]
        return self.spec.display_text(position, case, case)

    def set_positions_batch(self, values):
        changed = False
        for position, value in values.items():
            cell = self.spec.resolve_cell(position)
            if not cell.editable or cell.input_key is None:
                continue
            row = self.cases[cell.logical_case_index]
            if row.get(cell.input_key, "") == value:
                continue
            row[cell.input_key] = value
            changed = True
        return changed

    def snapshot(self):
        return self.spec.snapshot_cases(self.cases)

    def restore_snapshot(self, snapshot):
        self.cases = self.spec.restore_cases(snapshot)
        self._ensure_widgets()

    def cell_frame(self, position):
        return self.frames[position]

    def cell_widget(self, position):
        return self.widgets[position]

    def focus_widget(self, position):
        return self.widgets[position]

    def default_cell_background(self, _position):
        return ""

    def clipboard_clear(self):
        self.clipboard = ""

    def clipboard_append(self, text):
        self.clipboard = text

    def clipboard_get(self):
        return self.clipboard

    def winfo_containing(self, *_args):
        return None

    def _ensure_widgets(self):
        for row in range(self.row_count()):
            for column in range(self.column_count()):
                self.frames.setdefault((row, column), _FakeWidget())
                self.widgets.setdefault((row, column), _FakeWidget())


def test_table_controller_paste_uses_per_cell_editable_roles_only():
    surface = _FakeMatrixSurface()
    controller = TkTableController(surface)
    surface.clipboard = (
        "CASE\tTYPE\t3501\t3601\t1701\tSHOULD_SKIP\tSHOULD_SKIP\n"
        "CASE\tTYPE\tDECLARED_SKIP\t901\t381\tSHOULD_SKIP\tSHOULD_SKIP"
    )

    controller.select((0, 0))
    controller.select((1, 6), extend=True)
    controller._paste()

    assert surface.cases == [
        {
            DECLARED_CAPACITY: "3501",
            FULL_CAPACITY: "3601",
            FULL_POWER: "901",
            HALF_CAPACITY: "1701",
            HALF_POWER: "381",
            CSPF: "4.939",
            CSEC: "729.0",
        }
    ]


def test_table_controller_clear_uses_per_cell_editable_roles_only():
    surface = _FakeMatrixSurface()
    controller = TkTableController(surface)

    controller.select((0, 0))
    controller.select((1, 6), extend=True)
    controller._clear()

    assert surface.cases == [
        {
            DECLARED_CAPACITY: "",
            FULL_CAPACITY: "",
            FULL_POWER: "",
            HALF_CAPACITY: "",
            HALF_POWER: "",
            CSPF: "4.939",
            CSEC: "729.0",
        }
    ]

    controller._undo_last()

    assert surface.cases[0][DECLARED_CAPACITY] == "3500"
    assert surface.cases[0][FULL_POWER] == "900"
    assert surface.cases[0][CSPF] == "4.939"


def test_table_controller_selected_range_fill_paste_respects_per_cell_roles():
    surface = _FakeMatrixSurface()
    controller = TkTableController(surface)
    surface.clipboard = "A\tB\tC"

    controller.select((0, 2))
    controller.select((1, 4), extend=True)
    controller._paste()

    assert surface.cases[0][DECLARED_CAPACITY] == "A"
    assert surface.cases[0][FULL_CAPACITY] == "B"
    assert surface.cases[0][HALF_CAPACITY] == "C"
    assert surface.cases[0][FULL_POWER] == "B"
    assert surface.cases[0][HALF_POWER] == "C"


def test_table_controller_copy_keeps_physical_rectangular_grid_semantics():
    surface = _FakeMatrixSurface()
    controller = TkTableController(surface)

    controller.select((0, 0))
    controller.select((1, 6), extend=True)
    controller._copy()

    assert surface.clipboard == (
        "1\tCapacity\t3500\t3600\t1700\t4.939\t729.0\n"
        "\tPower\t\t900\t380\t\t"
    )
