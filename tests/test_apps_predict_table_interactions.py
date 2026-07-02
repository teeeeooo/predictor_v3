"""Predict table interaction tests."""

import os

from PySide6.QtCore import QItemSelectionModel, Qt
from PySide6.QtWidgets import QApplication

from apps.predict.state.predict_session import PredictSession
from apps.predict.state.result_row import ResultRow
from apps.common.ui.tables.clipboard import format_tsv, parse_tsv
from apps.predict.ui.tables.input_table_model import InputTableModel
from apps.predict.ui.tables.input_table_view import InputTableView
from apps.predict.ui.tables.result_table_model import ResultTableModel
from apps.predict.ui.tables.result_table_view import ResultTableView


def _app() -> QApplication:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    return QApplication.instance() or QApplication([])


def _session_with_rows(count: int = 2) -> PredictSession:
    session = PredictSession()
    session.case_store.append_empty_rows(count)
    return session


def test_parse_tsv_normalizes_line_endings_and_trailing_newline():
    assert parse_tsv("a\tb\r\nc\td\r\n") == [["a", "b"], ["c", "d"]]
    assert parse_tsv("a\tb\rc\td") == [["a", "b"], ["c", "d"]]
    assert parse_tsv("") == []


def test_format_tsv_converts_none_to_empty_string():
    assert format_tsv([["a", None], [1, "b"]]) == "a\t\n1\tb\n"


def test_input_view_copy_and_paste_tsv_anchor():
    _app()
    session = _session_with_rows()
    model = InputTableModel(session)
    view = InputTableView()
    view.setModel(model)

    first = model.index(0, 0)
    view.selectionModel().setCurrentIndex(first, QItemSelectionModel.ClearAndSelect)

    assert view.paste_tsv_at_selection("7.1\t8.2\n5.3\t6.4\n") == 4
    assert model.cell_value(0, 0) == "7.1"
    assert model.cell_value(1, 1) == "6.4"

    view.selectionModel().select(
        model.index(1, 1),
        QItemSelectionModel.Select,
    )
    assert view.copy_selection_tsv() == "7.1\t8.2\n5.3\t6.4\n"


def test_input_view_paste_drops_out_of_bounds_and_skips_auto_cells():
    _app()
    session = _session_with_rows(1)
    model = InputTableModel(session)
    view = InputTableView()
    view.setModel(model)
    auto_col = next(i for i, column in enumerate(model.columns) if column.is_auto)
    view.selectionModel().setCurrentIndex(
        model.index(0, auto_col),
        QItemSelectionModel.ClearAndSelect,
    )

    assert view.paste_tsv_at_selection("x\ty\n") == 0
    assert model.cell_value(0, auto_col) == ""


def test_input_view_clear_selection_only_editable_cells():
    _app()
    session = _session_with_rows()
    model = InputTableModel(session)
    view = InputTableView()
    view.setModel(model)
    assert model.setData(model.index(0, 0), "7.1", Qt.EditRole)
    auto_col = next(i for i, column in enumerate(model.columns) if column.is_auto)
    session.case_store.get_case_at(0).autofill_values[model.columns[auto_col].key] = "auto"

    selection = view.selectionModel()
    selection.setCurrentIndex(model.index(0, 0), QItemSelectionModel.ClearAndSelect)
    selection.select(model.index(0, auto_col), QItemSelectionModel.Select)

    assert view.clear_selection() == 1
    assert model.cell_value(0, 0) == ""
    assert model.cell_value(0, auto_col) == "auto"


def test_invalid_numeric_input_returns_validation_background_and_tooltip():
    _app()
    session = _session_with_rows()
    model = InputTableModel(session)

    assert model.setData(model.index(0, 0), "not-number", Qt.EditRole)

    assert model.is_invalid(0, 0)
    assert model.data(model.index(0, 0), Qt.ToolTipRole)
    assert model.data(model.index(0, 0), Qt.BackgroundRole).isValid()


def test_result_view_copies_selected_cells():
    _app()
    session = _session_with_rows()
    first_case_id = session.case_order[0]
    session.set_result(
        ResultRow(
            case_id=first_case_id,
            status="complete",
            result_values={"cooling_power": "2.1", "eer": "3.4"},
        )
    )
    model = ResultTableModel(session)
    view = ResultTableView()
    view.setModel(model)
    view.selectionModel().setCurrentIndex(
        model.index(0, 0),
        QItemSelectionModel.ClearAndSelect,
    )
    view.selectionModel().select(model.index(0, 1), QItemSelectionModel.Select)

    assert view.copy_selection_tsv() == "2.1\t3.4\n"


def test_result_model_renders_error_status_tooltip_and_background():
    _app()
    session = _session_with_rows()
    first_case_id = session.case_order[0]
    session.set_result(
        ResultRow(
            case_id=first_case_id,
            status="error",
            message="model missing",
        )
    )
    model = ResultTableModel(session)

    assert model.data(model.index(0, 0), Qt.ToolTipRole) == "model missing"
    assert model.data(model.index(0, 0), Qt.BackgroundRole).isValid()
