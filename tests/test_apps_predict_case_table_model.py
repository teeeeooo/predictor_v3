"""Unified Predict case table model tests."""

import inspect
import os

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from apps.predict.schema.case_table_schema_adapter import (
    auto_columns,
    build_case_table_column_schema,
    result_columns,
    status_columns,
)
from apps.predict.state.predict_session import PredictSession
from apps.predict.state.result_row import ResultRow
from apps.predict.ui.tables import case_table_model
from apps.predict.ui.tables.case_table_model import CaseTableModel


def _app() -> QApplication:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    return QApplication.instance() or QApplication([])


def _session_with_rows(count: int = 2) -> PredictSession:
    session = PredictSession()
    session.case_store.append_empty_rows(count)
    return session


def _column_index(model: CaseTableModel, key: str) -> int:
    return next(index for index, column in enumerate(model.columns) if column.key == key)


def test_case_table_model_uses_unified_schema_columns():
    _app()
    session = _session_with_rows()
    model = CaseTableModel(session)

    assert model.rowCount() == 2
    assert model.columnCount() == len(build_case_table_column_schema())
    assert [column.key for column in model.columns][-2:] == ["status", "message"]
    assert "case_id" not in {column.key for column in model.columns}
    assert model.headerData(0, Qt.Vertical, Qt.DisplayRole) == 1


def test_case_table_model_group_rendering_and_result_status_display():
    _app()
    session = _session_with_rows()
    case = session.case_store.get_case_at(0)
    case.input_values["cooling_capa"] = "7.1"
    case.autofill_values["id_volume"] = "1.2"
    session.set_result(
        ResultRow(
            case_id=case.case_id,
            status="complete",
            result_values={"cooling_power": "2.06"},
            message="ok",
        )
    )
    model = CaseTableModel(session)

    assert model.cell_value(0, _column_index(model, "cooling_capa")) == "7.1"
    assert model.cell_value(0, _column_index(model, "id_volume")) == "1.2"
    assert model.cell_value(0, _column_index(model, "cooling_power")) == "2.06"
    assert model.cell_value(0, _column_index(model, "status")) == "complete"
    assert model.cell_value(0, _column_index(model, "message")) == "ok"
    assert model.data(model.index(0, _column_index(model, "status")), Qt.BackgroundRole).isValid()


def test_case_table_model_edit_updates_case_store_and_callback():
    _app()
    session = _session_with_rows()
    calls: list[tuple[str, str]] = []
    model = CaseTableModel(session, edit_callback=lambda case_id, key: calls.append((case_id, key)))
    index = model.index(0, _column_index(model, "cooling_capa"))

    assert model.flags(index) & Qt.ItemIsEditable
    assert model.setData(index, "7.1", Qt.EditRole)

    case = session.case_store.get_case_at(0)
    assert case.input_values["cooling_capa"] == "7.1"
    assert calls == [(case.case_id, "cooling_capa")]

    assert model.setData(index, "7.1", Qt.EditRole)
    assert calls == [(case.case_id, "cooling_capa")]


def test_case_table_model_prevents_auto_result_and_status_mutation():
    _app()
    session = _session_with_rows()
    case = session.case_store.get_case_at(0)
    session.set_result(
        ResultRow(case_id=case.case_id, status="error", result_values={"cooling_power": "2.0"})
    )
    model = CaseTableModel(session)

    for column in auto_columns() + result_columns() + status_columns():
        index = model.index(0, _column_index(model, column.key))
        assert not (model.flags(index) & Qt.ItemIsEditable)
        assert model.is_readonly_cell(0, index.column())
        assert not model.setData(index, "changed", Qt.EditRole)

    assert case.autofill_values == {}
    assert session.result_for_case(case.case_id).result_values["cooling_power"] == "2.0"
    assert session.result_for_case(case.case_id).status == "error"


def test_case_table_model_invalid_numeric_tooltip_and_background():
    _app()
    session = _session_with_rows()
    model = CaseTableModel(session)
    index = model.index(0, _column_index(model, "cooling_capa"))

    assert model.setData(index, "not-number", Qt.EditRole)
    assert model.is_invalid(0, index.column())
    assert model.data(index, Qt.ToolTipRole) == "냉방능력: 숫자로 입력해 주세요."
    assert "cooling_capa" not in model.data(index, Qt.ToolTipRole)
    assert model.data(index, Qt.BackgroundRole).isValid()


def test_case_table_model_import_boundary_excludes_services_and_mapping():
    source = inspect.getsource(case_table_model)

    forbidden = (
        "core.mapping",
        "core.ml",
        "prediction_service",
        "PredictionService",
        "mapping_repository",
        "calculator",
        "training",
    )
    for text in forbidden:
        assert text not in source
