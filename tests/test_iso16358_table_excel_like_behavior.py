"""ISO16358 input table — Excel-like behavior contract tests.

Protects the contract alignment patch for `ProfileInputGridModel` /
`ProfileInputGridView`: Ctrl+C TSV copy, Delete/Backspace clear,
Ctrl+Z undo, Enter / Shift+Enter / Tab / Shift+Tab navigation, and
invalid numeric cell BackgroundRole / ToolTipRole.

PyQt5-less environments skip via `pytest.importorskip` so the suite
still collects on headless CI.
"""

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

pytest.importorskip("PyQt5")

from PyQt5.QtCore import QItemSelection, QItemSelectionModel, Qt
from PyQt5.QtGui import QBrush
from PyQt5.QtWidgets import QApplication

from ui.calculators_2point import ProfileInputGridModel, ProfileInputGridView
from ui.spreadsheet_table import (
    INVALID_CELL_BACKGROUND_RGB,
    INVALID_CELL_TOOLTIP,
)


def _qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def _make_view_with_points(points):
    _qapp()
    model = ProfileInputGridModel()
    model.set_points(points)
    view = ProfileInputGridView()
    view.setModel(model)
    return view, model


POINTS_2 = [("35°C Full", "35_full"), ("35°C Half", "35_half")]
POINTS_3 = [("A", "a"), ("B", "b"), ("C", "c")]


def _select_range(view, top_row, left_col, bottom_row, right_col):
    model = view.model()
    sel = QItemSelection(
        model.index(top_row, left_col),
        model.index(bottom_row, right_col),
    )
    sel_model = view.selectionModel()
    sel_model.select(sel, QItemSelectionModel.ClearAndSelect)
    sel_model.setCurrentIndex(
        model.index(top_row, left_col), QItemSelectionModel.NoUpdate
    )


# --- copy ---------------------------------------------------------------


def test_selected_to_tsv_emits_bounding_rectangle():
    view, model = _make_view_with_points(POINTS_3)
    model.setData(model.index(0, 0), "100")
    model.setData(model.index(0, 1), "200")
    model.setData(model.index(0, 2), "300")
    model.setData(model.index(1, 0), "10")
    model.setData(model.index(1, 1), "20")
    model.setData(model.index(1, 2), "30")

    tsv = model.selected_to_tsv([(0, 0), (0, 1), (1, 0), (1, 1)])
    assert tsv == "100\t200\n10\t20\n"


def test_copy_selection_puts_tsv_on_clipboard():
    app = _qapp()
    view, model = _make_view_with_points(POINTS_2)
    model.setData(model.index(0, 0), "1000")
    model.setData(model.index(0, 1), "500")
    model.setData(model.index(1, 0), "300")
    model.setData(model.index(1, 1), "150")
    _select_range(view, 0, 0, 1, 1)

    view.copy_selection_to_clipboard()
    assert app.clipboard().text() == "1000\t500\n300\t150\n"


# --- clear --------------------------------------------------------------


def test_clear_selection_blanks_cells_and_groups_undo():
    view, model = _make_view_with_points(POINTS_2)
    model.setData(model.index(0, 0), "1000")
    model.setData(model.index(0, 1), "500")
    model.setData(model.index(1, 0), "300")
    model.setData(model.index(1, 1), "150")
    _select_range(view, 0, 0, 1, 1)

    cleared = view.clear_selection()
    assert cleared == 4
    assert model.parsed_points() is None
    for row in range(2):
        for col in range(2):
            assert model.data(model.index(row, col), Qt.DisplayRole) == ""

    model.undo()
    parsed = model.parsed_points()
    assert parsed == {
        "35_full": {"capacity": 1000.0, "power": 300.0},
        "35_half": {"capacity": 500.0, "power": 150.0},
    }


def test_clear_with_no_selection_uses_current_index():
    view, model = _make_view_with_points(POINTS_2)
    model.setData(model.index(0, 0), "1000")
    view.setCurrentIndex(model.index(0, 0))

    cleared = view.clear_selection()
    assert cleared == 1
    assert model.data(model.index(0, 0), Qt.DisplayRole) == ""


# --- invalid display ----------------------------------------------------


def test_empty_cell_is_not_invalid():
    view, model = _make_view_with_points(POINTS_2)
    assert model.is_cell_invalid(0, 0) is False
    # BackgroundRole stays at the default white for empty cells.
    bg = model.data(model.index(0, 0), Qt.BackgroundRole)
    assert bg is not None
    assert not isinstance(bg, QBrush)


def test_non_numeric_cell_is_invalid_with_tooltip():
    view, model = _make_view_with_points(POINTS_2)
    model.setData(model.index(0, 0), "abc")

    assert model.is_cell_invalid(0, 0) is True
    bg = model.data(model.index(0, 0), Qt.BackgroundRole)
    assert isinstance(bg, QBrush)
    assert bg.color().getRgb()[:3] == INVALID_CELL_BACKGROUND_RGB
    assert model.data(model.index(0, 0), Qt.ToolTipRole) == INVALID_CELL_TOOLTIP


@pytest.mark.parametrize("text", ["0", "-5", "0.0"])
def test_zero_or_negative_cell_is_invalid(text):
    view, model = _make_view_with_points(POINTS_2)
    model.setData(model.index(0, 0), text)
    assert model.is_cell_invalid(0, 0) is True
    bg = model.data(model.index(0, 0), Qt.BackgroundRole)
    assert isinstance(bg, QBrush)


def test_positive_numeric_cell_is_not_invalid():
    view, model = _make_view_with_points(POINTS_2)
    model.setData(model.index(0, 0), "1000")
    assert model.is_cell_invalid(0, 0) is False


# --- navigation ---------------------------------------------------------


@pytest.mark.parametrize(
    "row, col, direction, expected",
    [
        (0, 0, "right", (0, 1)),
        (0, 1, "right", (1, 0)),
        (1, 1, "right", (1, 1)),
        (1, 1, "left", (1, 0)),
        (1, 0, "left", (0, 1)),
        (0, 0, "left", (0, 0)),
        (0, 0, "down", (1, 0)),
        (1, 0, "down", (0, 1)),
        (1, 1, "down", (1, 1)),
        (1, 1, "up", (0, 1)),
        (0, 1, "up", (1, 0)),
        (0, 0, "up", (0, 0)),
    ],
)
def test_next_navigation_index_wrap_and_clamp(row, col, direction, expected):
    view, _ = _make_view_with_points(POINTS_2)
    assert view.next_navigation_index(row, col, direction) == expected


def test_move_active_cell_updates_current_index():
    view, model = _make_view_with_points(POINTS_2)
    view.setCurrentIndex(model.index(0, 0))

    view.move_active_cell("down")
    assert (view.currentIndex().row(), view.currentIndex().column()) == (1, 0)

    view.move_active_cell("right")
    assert (view.currentIndex().row(), view.currentIndex().column()) == (1, 1)

    view.move_active_cell("up")
    assert (view.currentIndex().row(), view.currentIndex().column()) == (0, 1)

    view.move_active_cell("left")
    assert (view.currentIndex().row(), view.currentIndex().column()) == (0, 0)
