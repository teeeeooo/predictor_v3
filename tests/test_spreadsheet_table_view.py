import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

pytest.importorskip("PyQt5")

from PyQt5.QtCore import QItemSelectionModel, Qt  # noqa: E402
from PyQt5.QtTest import QTest  # noqa: E402
from PyQt5.QtWidgets import QApplication, QAbstractItemView  # noqa: E402

from ui.spreadsheet_table import SpreadsheetTableModel, SpreadsheetTableView  # noqa: E402


_APP = None


def _qapp():
    global _APP
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    _APP = app
    return app


def _make_view():
    _qapp()
    model = SpreadsheetTableModel(
        row_labels=["capacity", "power"],
        column_labels=["A", "B", "C"],
    )
    view = SpreadsheetTableView()
    view.setModel(model)
    view.setSelectionMode(QAbstractItemView.ExtendedSelection)
    return view, model


def _select_range(view, model, top, left, bottom, right):
    selection_model = view.selectionModel()
    selection_model.clearSelection()
    for row in range(top, bottom + 1):
        for col in range(left, right + 1):
            selection_model.select(
                model.index(row, col),
                QItemSelectionModel.Select,
            )
    selection_model.setCurrentIndex(model.index(top, left), QItemSelectionModel.NoUpdate)


def test_copy_selection_tsv_returns_selected_rectangle():
    view, model = _make_view()
    try:
        model.paste_tsv(0, 0, "1\t2\t3\n4\t5\t6\n")
        _select_range(view, model, 0, 0, 1, 1)

        assert view.copy_selection_tsv() == "1\t2\n4\t5\n"
    finally:
        view.close()


def test_paste_tsv_at_selection_writes_from_top_left_anchor():
    view, model = _make_view()
    try:
        _select_range(view, model, 0, 1, 0, 1)

        written = view.paste_tsv_at_selection("10\t20\n30\t40\n")

        assert written == 4
        assert model.to_grid() == [["", "10", "20"], ["", "30", "40"]]
    finally:
        view.close()


def test_clear_selection_and_undo_last_restore_previous_grid():
    view, model = _make_view()
    try:
        model.paste_tsv(0, 0, "1\t2\t3\n4\t5\t6\n")
        before_clear = model.to_grid()
        _select_range(view, model, 0, 1, 1, 1)

        cleared = view.clear_selection()

        assert cleared == 2
        assert model.to_grid() == [["1", "", "3"], ["4", "", "6"]]
        assert view.undo_last() is True
        assert model.to_grid() == before_clear
    finally:
        view.close()


def test_undo_last_reverts_paste_group():
    view, model = _make_view()
    try:
        model.set_cell(0, 0, "seed")
        model.reset_undo()
        before_paste = model.to_grid()
        _select_range(view, model, 0, 0, 0, 0)

        view.paste_tsv_at_selection("x\ty\n")

        assert model.to_grid()[0][:2] == ["x", "y"]
        assert view.undo_last() is True
        assert model.to_grid() == before_paste
    finally:
        view.close()


def test_delete_key_clears_selection_without_clipboard_dependency():
    view, model = _make_view()
    try:
        model.paste_tsv(0, 0, "1\t2\t3\n4\t5\t6\n")
        _select_range(view, model, 0, 0, 0, 1)
        view.show()
        view.setFocus()

        QTest.keyClick(view, Qt.Key_Delete)

        assert model.to_grid() == [["", "", "3"], ["4", "5", "6"]]
    finally:
        view.close()
