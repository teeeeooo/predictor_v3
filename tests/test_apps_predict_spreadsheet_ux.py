"""Unified Predict case table spreadsheet interaction tests."""

import os

from PySide6.QtCore import QEvent, QItemSelectionModel, Qt
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QApplication

from apps.predict.state.predict_session import PredictSession
from apps.predict.state.result_row import ResultRow
from apps.predict.ui.tables.case_table_model import CaseTableModel
from apps.predict.ui.tables.case_table_view import CaseTableView


def _app() -> QApplication:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    return QApplication.instance() or QApplication([])


def _table() -> tuple[PredictSession, CaseTableModel, CaseTableView]:
    _app()
    session = PredictSession()
    session.case_store.append_empty_rows(3)
    model = CaseTableModel(session)
    view = CaseTableView()
    view.setModel(model)
    return session, model, view


def _column_index(model: CaseTableModel, key: str) -> int:
    return next(index for index, column in enumerate(model.columns) if column.key == key)


def _select(view: CaseTableView, model: CaseTableModel, *cells: tuple[int, int]) -> None:
    selection = view.selectionModel()
    first_row, first_col = cells[0]
    selection.setCurrentIndex(
        model.index(first_row, first_col),
        QItemSelectionModel.ClearAndSelect,
    )
    for row, col in cells[1:]:
        selection.select(model.index(row, col), QItemSelectionModel.Select)


def _send_key(view: CaseTableView, key: int, text: str = "", modifiers=Qt.NoModifier) -> None:
    event = QKeyEvent(QEvent.KeyPress, key, modifiers, text)
    QApplication.sendEvent(view, event)


def test_undo_edit_restores_previous_value():
    _session, model, view = _table()
    cooling = _column_index(model, "cooling_capa")
    _select(view, model, (0, cooling))

    assert view.replace_current_cell("7.1")
    assert model.cell_value(0, cooling) == "7.1"
    assert view.undo() == 1
    assert model.cell_value(0, cooling) == ""


def test_undo_paste_group_restores_all_changed_cells():
    _session, model, view = _table()
    _select(view, model, (0, 0))

    assert view.paste_tsv_at_selection("7.1\t8.2\n5.3\t6.4\n") == 4
    assert model.cell_value(1, 1) == "6.4"
    assert view.undo() == 4
    assert model.cell_value(0, 0) == ""
    assert model.cell_value(1, 1) == ""


def test_undo_clear_group_restores_selected_editable_cells():
    _session, model, view = _table()
    assert model.setData(model.index(0, 0), "7.1", Qt.EditRole)
    assert model.setData(model.index(0, 1), "8.2", Qt.EditRole)
    _select(view, model, (0, 0), (0, 1))

    assert view.clear_selection() == 2
    assert model.cell_value(0, 0) == ""
    assert view.undo() == 2
    assert model.cell_value(0, 0) == "7.1"
    assert model.cell_value(0, 1) == "8.2"


def test_tab_shift_tab_enter_and_shift_enter_navigation():
    _session, model, view = _table()
    _select(view, model, (0, 0))

    _send_key(view, Qt.Key_Tab)
    assert view.currentIndex() == model.index(0, 1)
    _send_key(view, Qt.Key_Backtab, modifiers=Qt.ShiftModifier)
    assert view.currentIndex() == model.index(0, 0)
    _send_key(view, Qt.Key_Return)
    assert view.currentIndex() == model.index(1, 0)
    _send_key(view, Qt.Key_Return, modifiers=Qt.ShiftModifier)
    assert view.currentIndex() == model.index(0, 0)


def test_type_replace_overwrites_active_cell_whole_value():
    _session, model, view = _table()
    index = model.index(0, 0)
    assert model.setData(index, "123", Qt.EditRole)
    _select(view, model, (0, 0))

    _send_key(view, Qt.Key_9, "9")

    assert model.cell_value(0, 0) == "9"
    assert view.undo() == 1
    assert model.cell_value(0, 0) == "123"


def test_selected_range_fill_paste_and_readonly_skip():
    _session, model, view = _table()
    result_col = _column_index(model, "cooling_power")
    _select(view, model, (0, 0), (1, 1))

    assert view.paste_tsv_at_selection("x") == 4
    assert model.cell_value(0, 0) == "x"
    assert model.cell_value(1, 1) == "x"
    _select(view, model, (0, result_col))
    assert view.paste_tsv_at_selection("changed") == 0
    assert model.cell_value(0, result_col) == ""


def test_one_row_paste_repeats_down_matching_selection_width():
    _session, model, view = _table()
    _select(view, model, (0, 0), (1, 1))

    assert view.paste_tsv_at_selection("7.1\t8.2\n") == 4
    assert model.cell_value(0, 0) == "7.1"
    assert model.cell_value(1, 0) == "7.1"
    assert model.cell_value(1, 1) == "8.2"


def test_result_and_status_copy_included_but_mutation_prevented():
    session, model, view = _table()
    case_id = session.case_order[0]
    session.set_result(
        ResultRow(
            case_id=case_id,
            status="error",
            result_values={"cooling_power": "2.0"},
            message="missing model",
        )
    )
    power = _column_index(model, "cooling_power")
    status = _column_index(model, "status")
    message = _column_index(model, "message")
    _select(view, model, (0, power), (0, status), (0, message))

    assert view.copy_selection_tsv().endswith("error\tmissing model\n")
    assert view.clear_selection() == 0
    assert view.paste_tsv_at_selection("changed\tchanged\tchanged\n") == 0
    assert model.cell_value(0, power) == "2.0"
    assert model.cell_value(0, status) == "error"
