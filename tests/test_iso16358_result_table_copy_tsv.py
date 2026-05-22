"""ISO16358 read-only result table — Ctrl+C TSV copy tests.

Protects the read-only result/trace table copy patch (report 105):
TwoPointTableModel, RegionResultTableModel, TraceTableModel, and
RegionDetailTab.table. PyQt5-less environments skip via
``pytest.importorskip`` so the suite still collects on headless CI.
"""

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

pytest.importorskip("PyQt5")

from tests.helpers.pyqt_env import macos_python314_pyqt5_known_bad_skip_mark

pytestmark = macos_python314_pyqt5_known_bad_skip_mark()

from PyQt5.QtCore import QItemSelection, QItemSelectionModel, Qt
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QApplication

from ui.calculators_2point import (
    ReadOnlyCopyTableView,
    RegionDetailTab,
    RegionResultTableModel,
    TraceTableModel,
    TwoPointTableModel,
    TwoPointTableView,
    selected_cells_to_tsv,
)


def _qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def _select_range(view, top_row, left_col, bottom_row, right_col):
    model = view.model()
    sel = QItemSelection(
        model.index(top_row, left_col),
        model.index(bottom_row, right_col),
    )
    sm = view.selectionModel()
    sm.select(sel, QItemSelectionModel.ClearAndSelect)
    sm.setCurrentIndex(
        model.index(top_row, left_col), QItemSelectionModel.NoUpdate
    )


def _key_copy(view):
    # Programmatic copy via the same code path the view's Ctrl+C uses.
    view.copy_selection_to_clipboard()


def test_two_point_table_copy_tsv_via_clipboard():
    _qapp()
    model = TwoPointTableModel()
    view = TwoPointTableView()
    view.setModel(model)

    # Fill two rows of editable input cells (cols 1..4).
    model.setData(model.index(0, 1), "10000")
    model.setData(model.index(0, 2), "3000")
    model.setData(model.index(1, 1), "5000")
    model.setData(model.index(1, 2), "1500")

    _select_range(view, 0, 1, 1, 2)
    QApplication.clipboard().clear()
    _key_copy(view)
    text = QApplication.clipboard().text()
    assert text == "10000\t3000\n5000\t1500\n"


def test_region_result_table_copy_tsv_via_clipboard():
    _qapp()
    model = RegionResultTableModel()
    model.set_schema(
        ["Region", "CSPF", "CSTL"],
        [
            ["ISO 16358-1", "4.21", "1234.5"],
            ["India ISEER", "3.85", "1100.0"],
        ],
    )
    view = ReadOnlyCopyTableView()
    view.setModel(model)

    _select_range(view, 0, 0, 1, 2)
    QApplication.clipboard().clear()
    _key_copy(view)
    assert QApplication.clipboard().text() == (
        "ISO 16358-1\t4.21\t1234.5\n"
        "India ISEER\t3.85\t1100.0\n"
    )


def test_trace_table_copy_tsv_via_clipboard():
    _qapp()
    model = TraceTableModel()
    model.set_data([
        {"bin_no": 1, "tj": -8.0, "nj": 1, "lc": 100.0,
         "capacity": 200.0, "power": 50.0, "eer": 4.0,
         "cstl_bin": 100.0, "csec_bin": 25.0},
        {"bin_no": 2, "tj": -7.0, "nj": 2, "lc": 110.0,
         "capacity": 210.0, "power": 55.0, "eer": 3.8,
         "cstl_bin": 220.0, "csec_bin": 60.0},
    ])
    view = ReadOnlyCopyTableView()
    view.setModel(model)

    # Select first two columns of both rows.
    _select_range(view, 0, 0, 1, 1)
    QApplication.clipboard().clear()
    _key_copy(view)
    assert QApplication.clipboard().text() == "1\t-8.00\n2\t-7.00\n"


def test_region_detail_tab_table_is_copy_enabled():
    _qapp()
    tab = RegionDetailTab("ISO 16358-1")
    assert isinstance(tab.table, ReadOnlyCopyTableView)
    tab.table_model.set_data([
        {"bin_no": 1, "tj": -8.0, "nj": 1, "lc": 100.0,
         "capacity": 200.0, "power": 50.0, "eer": 4.0,
         "cstl_bin": 100.0, "csec_bin": 25.0},
    ])
    _select_range(tab.table, 0, 0, 0, 1)
    QApplication.clipboard().clear()
    tab.table.copy_selection_to_clipboard()
    assert QApplication.clipboard().text() == "1\t-8.00\n"


def test_non_rectangular_selection_uses_bounding_rectangle():
    _qapp()
    model = RegionResultTableModel()
    model.set_schema(
        ["A", "B", "C"],
        [
            ["a0", "b0", "c0"],
            ["a1", "b1", "c1"],
            ["a2", "b2", "c2"],
        ],
    )
    view = ReadOnlyCopyTableView()
    view.setModel(model)
    # Two disjoint single cells: (0, 0) and (2, 2). Bounding rect is the
    # full 3x3.
    sm = view.selectionModel()
    sm.select(
        QItemSelection(model.index(0, 0), model.index(0, 0)),
        QItemSelectionModel.ClearAndSelect,
    )
    sm.select(
        QItemSelection(model.index(2, 2), model.index(2, 2)),
        QItemSelectionModel.Select,
    )
    sm.setCurrentIndex(model.index(0, 0), QItemSelectionModel.NoUpdate)
    QApplication.clipboard().clear()
    view.copy_selection_to_clipboard()
    assert QApplication.clipboard().text() == (
        "a0\tb0\tc0\n"
        "a1\tb1\tc1\n"
        "a2\tb2\tc2\n"
    )


def test_empty_selection_falls_back_to_current_index():
    _qapp()
    model = RegionResultTableModel()
    model.set_schema(["X"], [["onlycell"]])
    view = ReadOnlyCopyTableView()
    view.setModel(model)
    sm = view.selectionModel()
    sm.clearSelection()
    sm.setCurrentIndex(model.index(0, 0), QItemSelectionModel.NoUpdate)
    QApplication.clipboard().clear()
    view.copy_selection_to_clipboard()
    assert QApplication.clipboard().text() == "onlycell\n"


def test_selected_cells_to_tsv_out_of_range_returns_blank():
    _qapp()
    model = RegionResultTableModel()
    model.set_schema(["A", "B"], [["a0", "b0"]])
    tsv = selected_cells_to_tsv(model, [(0, 0), (1, 1)])
    # Row 1 is out of range -> empty cells. Bounding rect is 2x2.
    assert tsv == "a0\tb0\n\t\n"
