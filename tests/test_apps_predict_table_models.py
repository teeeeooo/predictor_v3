"""Predict app table model schema recovery tests."""

import os

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from apps.predict.schema.column_schema_adapter import (
    build_input_column_schema,
    build_result_column_schema,
)
from apps.predict.schema.case_table_schema_adapter import build_case_table_column_schema
from apps.predict.state.predict_session import PredictSession
from apps.predict.state.result_row import ResultRow
from apps.predict.ui.tables.input_table_model import InputTableModel
from apps.predict.ui.tables.result_table_model import ResultTableModel
from apps.predict.ui.workspace import PredictWorkspace
from core.predictor_schema.columns import AUTO_COLS, INPUT_COLS, RESULT_COLS


def _app() -> QApplication:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    return QApplication.instance() or QApplication([])


def _session_with_rows(count: int = 2) -> PredictSession:
    session = PredictSession()
    session.case_store.append_empty_rows(count)
    return session


def test_input_table_model_uses_core_schema_adapter():
    _app()
    session = _session_with_rows()
    model = InputTableModel(session)

    assert model.columnCount() == len(INPUT_COLS) + len(AUTO_COLS)
    assert model.columnCount() == len(build_input_column_schema())
    assert model.headerData(0, Qt.Horizontal, Qt.DisplayRole) == "냉방능력"
    assert model.headerData(0, Qt.Vertical, Qt.DisplayRole) == 1


def test_input_table_model_editability_follows_schema_group():
    _app()
    session = _session_with_rows()
    model = InputTableModel(session)
    editable_index = model.index(0, 0)
    auto_index = model.index(0, len(INPUT_COLS))

    assert model.flags(editable_index) & Qt.ItemIsEditable
    assert not (model.flags(auto_index) & Qt.ItemIsEditable)
    assert model.setData(editable_index, "3500", Qt.EditRole)
    assert session.case_store.get_case_at(0).input_values["cooling_capa"] == "3500"
    assert not model.setData(auto_index, "0.1", Qt.EditRole)


def test_result_table_model_uses_core_result_schema_and_case_id_lookup():
    _app()
    session = _session_with_rows()
    first_case_id = session.case_order[0]
    second_case_id = session.case_order[1]
    session.set_result(
        ResultRow(case_id=second_case_id, status="complete", result_values={"ref_qty": "1.25"})
    )
    model = ResultTableModel(session)
    ref_qty_column = RESULT_COLS.index("ref_qty")

    assert model.columnCount() == len(RESULT_COLS)
    assert model.columnCount() == len(build_result_column_schema())
    assert model.headerData(ref_qty_column, Qt.Horizontal, Qt.DisplayRole) == "냉매량"
    assert model.data(model.index(0, ref_qty_column), Qt.DisplayRole) == ""
    assert model.data(model.index(1, ref_qty_column), Qt.DisplayRole) == "1.25"
    assert session.result_for_case(first_case_id).case_id == first_case_id


def test_predict_workspace_schema_smoke_and_row_lifecycle():
    app = _app()
    workspace = PredictWorkspace()
    assert app is not None

    initial_rows = workspace.case_model.rowCount()
    assert workspace.case_model.columnCount() == len(build_case_table_column_schema())

    workspace._append_row()
    assert workspace.case_model.rowCount() == initial_rows + 1
    workspace._delete_selected_or_last_row()
    assert workspace.case_model.rowCount() == initial_rows
    workspace._reset_rows()
    assert workspace.case_model.rowCount() == 3


def test_predict_workspace_result_badge_reflects_error_state():
    _app()
    workspace = PredictWorkspace()
    case_id = workspace.session.case_order[0]
    workspace.session.set_result(ResultRow(case_id=case_id, status="error", message="x"))

    workspace._refresh_after_row_change()

    assert "오류" in workspace.result_badge.text()
