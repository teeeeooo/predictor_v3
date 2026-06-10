import pytest
import tkinter as tk

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
from ui_tk.batch_matrix_table import BatchMatrixTable
from ui_tk.table.controller import TkTableController
from ui_tk.table.roles import CellRole

tk_mod = pytest.importorskip("tkinter")

_root = None
try:
    _root = tk_mod.Tk()
    _root.withdraw()
except tk_mod.TclError as exc:
    pytest.skip(f"Tk unavailable: {exc}", allow_module_level=True)
finally:
    if _root is not None:
        _root.destroy()


@pytest.fixture(scope="module")
def root():
    r = tk_mod.Tk()
    r.withdraw()
    yield r
    r.destroy()


@pytest.fixture
def table(root):
    t = BatchMatrixTable(root, HONG_KONG_CSPF_MATRIX_SPEC)
    t.update_idletasks()
    yield t
    t.destroy()


def test_matrix_table_constructs_with_hong_kong_spec(root):
    t = BatchMatrixTable(root, HONG_KONG_CSPF_MATRIX_SPEC)
    assert t.spec is HONG_KONG_CSPF_MATRIX_SPEC
    assert t.row_count() == 10  # 5 default cases * 2 physical rows
    t.destroy()


def test_one_logical_case_renders_two_physical_rows(table):
    assert table.row_count() == 10
    assert table.column_count() == 7  # Case, RowType, 3 measurement, 2 result


def test_case_first_row_displays_number_second_row_blank_read_only(table):
    assert table.text_at_position((0, 0)) == "1"
    assert table.text_at_position((1, 0)) == ""
    assert table.spec.is_blank_read_only((1, 0))
    assert not table.spec.is_editable((1, 0))


def test_row_type_displays_spec_labels(table):
    assert table.text_at_position((0, 1)) == "Capacity"
    assert table.text_at_position((1, 1)) == "Power"
    assert table.text_at_position((2, 1)) == "Capacity"


def test_result_first_row_displays_values_second_row_blank(table):
    table.set_result(0, {CSPF: "4.939", CSEC: "729.0"})
    table.update_idletasks()
    assert table.text_at_position((0, 5)) == "4.939"
    assert table.text_at_position((1, 5)) == ""
    assert table.text_at_position((0, 6)) == "729.0"
    assert table.text_at_position((1, 6)) == ""


def test_not_applicable_cell_is_non_editable(table):
    assert table.spec.is_not_applicable((1, 2))
    assert not table.spec.is_editable((1, 2))
    assert table.cell_role((1, 2)) is CellRole.DISABLED


def test_cell_role_returns_expected_roles(table):
    assert table.cell_role((0, 0)) is CellRole.READONLY   # CASE
    assert table.cell_role((0, 1)) is CellRole.READONLY   # ROW_TYPE
    assert table.cell_role((0, 2)) is CellRole.EDITABLE   # INPUT
    assert table.cell_role((1, 2)) is CellRole.DISABLED   # NOT_APPLICABLE
    assert table.cell_role((0, 5)) is CellRole.RESULT     # RESULT


def test_paste_through_controller_updates_editable_input_cells_only(root):
    t = BatchMatrixTable(root, HONG_KONG_CSPF_MATRIX_SPEC)
    controller = TkTableController(t)
    t.clipboard_clear()
    t.clipboard_append(
        "CASE\tTYPE\t3501\t3601\t1701\tSHOULD_SKIP\tSHOULD_SKIP\n"
        "CASE\tTYPE\tDECLARED_SKIP\t901\t381\tSHOULD_SKIP\tSHOULD_SKIP"
    )
    controller.select((0, 0))
    controller.select((1, 6), extend=True)
    controller._paste()
    assert t.cases[0][DECLARED_CAPACITY] == "3501"
    assert t.cases[0][FULL_CAPACITY] == "3601"
    assert t.cases[0][FULL_POWER] == "901"
    assert t.cases[0][HALF_CAPACITY] == "1701"
    assert t.cases[0][HALF_POWER] == "381"
    assert t.cases[0].get(CSPF, "") == ""  # result not mutated
    t.destroy()


def test_clear_through_controller_clears_editable_input_cells_only(root):
    t = BatchMatrixTable(root, HONG_KONG_CSPF_MATRIX_SPEC)
    controller = TkTableController(t)
    controller.select((0, 0))
    controller.select((1, 6), extend=True)
    controller._clear()
    assert t.cases[0][DECLARED_CAPACITY] == ""
    assert t.cases[0][FULL_CAPACITY] == ""
    assert t.cases[0][FULL_POWER] == ""
    assert t.cases[0][HALF_CAPACITY] == ""
    assert t.cases[0][HALF_POWER] == ""
    assert t.cases[0].get(CSPF, "") == ""  # result stays blank
    controller._undo_last()
    assert t.cases[0][DECLARED_CAPACITY] == "3500"
    assert t.cases[0][FULL_POWER] == "900"
    t.destroy()


def test_copy_keeps_physical_rectangular_grid_shape(root):
    t = BatchMatrixTable(root, HONG_KONG_CSPF_MATRIX_SPEC)
    t.set_result(0, {CSPF: "4.939", CSEC: "729.0"})
    controller = TkTableController(t)
    controller.select((0, 0))
    controller.select((1, 6), extend=True)
    controller._copy()
    expected = (
        "1\tCapacity\t3500\t3600\t1700\t4.939\t729.0\n"
        "\tPower\t\t900\t380\t\t"
    )
    assert t.clipboard_get() == expected
    t.destroy()


def test_add_case_creates_complete_two_row_pair(root):
    t = BatchMatrixTable(root, HONG_KONG_CSPF_MATRIX_SPEC)
    before = t.row_count()
    t.add_case({DECLARED_CAPACITY: "9999"})
    assert t.row_count() == before + 2
    assert t.text_at_position((before, 0)) == "6"
    assert t.text_at_position((before + 1, 0)) == ""
    t.destroy()


def test_remove_case_removes_logical_pair_and_preserves_minimum_one(root):
    t = BatchMatrixTable(root, HONG_KONG_CSPF_MATRIX_SPEC)
    while len(t.cases) > 1:
        t.remove_case()
    assert len(t.cases) == 1
    t.remove_case()
    assert len(t.cases) == 1
    t.destroy()


def test_snapshot_restore_is_logical_case_based(root):
    t = BatchMatrixTable(root, HONG_KONG_CSPF_MATRIX_SPEC)
    original = dict(t.cases[0])
    snapshot = t.snapshot()
    t.cases[0][DECLARED_CAPACITY] = "9999"
    t.restore_snapshot(snapshot)
    assert t.cases[0][DECLARED_CAPACITY] == original[DECLARED_CAPACITY]
    t.destroy()


def test_same_shape_restore_preserves_widgets(root):
    t = BatchMatrixTable(root, HONG_KONG_CSPF_MATRIX_SPEC)
    original_widget_ids = {pos: id(t.cell_widget(pos)) for pos in t._cell_widgets}
    snapshot = t.snapshot()
    t.cases[0][DECLARED_CAPACITY] = "9999"
    t.restore_snapshot(snapshot)
    # same-shape restore should not rebuild widgets
    for pos in original_widget_ids:
        assert pos in t._cell_widgets
        assert id(t.cell_widget(pos)) == original_widget_ids[pos]
    t.destroy()


def test_shape_changing_restore_rebuilds_widgets(root):
    t = BatchMatrixTable(root, HONG_KONG_CSPF_MATRIX_SPEC)
    original_widget_ids = {pos: id(t.cell_widget(pos)) for pos in t._cell_widgets}
    # create a snapshot with different number of cases
    snapshot = [{}, {}]
    t.restore_snapshot(snapshot)
    # shape changed: widgets should be rebuilt
    assert len(t.cases) == 2
    assert t.row_count() == 4
    t.destroy()


def test_table_export_data_returns_headers_and_physical_rows(root):
    t = BatchMatrixTable(root, HONG_KONG_CSPF_MATRIX_SPEC)
    headers, rows = t.table_export_data()
    assert headers == ("Case", "Row Type", "Declared", "35 Full", "35 Half", "CSPF", "CSEC")
    assert len(rows) == 10  # 5 cases * 2 physical rows
    assert rows[0][0] == "1"  # Case 1 on first physical row
    assert rows[1][0] == ""  # blank on second physical row
    assert rows[0][1] == "Capacity"
    assert rows[1][1] == "Power"
    t.destroy()


def test_table_export_data_includes_result_first_row_only(root):
    t = BatchMatrixTable(root, HONG_KONG_CSPF_MATRIX_SPEC)
    t.set_result(0, {CSPF: "4.939", CSEC: "729.0"})
    t.update_idletasks()
    headers, rows = t.table_export_data()
    assert rows[0][5] == "4.939"
    assert rows[1][5] == ""  # blank on second physical row
    assert rows[0][6] == "729.0"
    assert rows[1][6] == ""  # blank on second physical row
    t.destroy()


def test_copy_all_puts_physical_grid_on_clipboard(root):
    t = BatchMatrixTable(root, HONG_KONG_CSPF_MATRIX_SPEC)
    t.set_result(0, {CSPF: "4.939", CSEC: "729.0"})
    t.copy_all()
    clipboard = t.clipboard_get()
    lines = clipboard.splitlines()
    assert lines[0] == "Case\tRow Type\tDeclared\t35 Full\t35 Half\tCSPF\tCSEC"
    assert lines[1].startswith("1\tCapacity\t3500\t3600\t1700\t4.939\t729.0")
    assert lines[2].startswith("\tPower\t\t900\t380\t\t")
    t.destroy()
