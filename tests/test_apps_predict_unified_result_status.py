"""Unified Predict result/status table integration tests."""

import os

import pytest
from PySide6.QtCore import QItemSelectionModel, Qt
from PySide6.QtWidgets import QApplication

from apps.predict.application.prediction_usecase import PredictionRunSummary
from apps.predict.application.models import PredictionModelStatus
from apps.predict.ports.prediction_execution_port import PredictionProgress
from apps.predict.state.predict_session import PredictSession
from apps.predict.state.result_row import ResultRow
from apps.predict.ui.tables.case_table_model import CaseTableModel
from apps.predict.ui.tables.case_table_view import CaseTableView
from apps.predict.ui.status_widgets import prediction_summary_text
from apps.predict.ui.workspace import PredictWorkspace


def _app() -> QApplication:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    return QApplication.instance() or QApplication([])


def test_terminal_summary_exposes_partial_and_unresolved_dispositions():
    text = prediction_summary_text(
        PredictionRunSummary(
            total=3,
            complete=1,
            partial=1,
            error=0,
            invalid=0,
            unresolved=1,
        )
    )

    assert "일부 결과 1건" in text
    assert "미반영 1건" in text


@pytest.fixture(autouse=True)
def _cleanup_qt_widgets():
    yield
    app = QApplication.instance()
    if app is None:
        return
    for widget in QApplication.topLevelWidgets():
        widget.close()
        widget.deleteLater()
    app.processEvents()


def _session_with_rows(count: int = 2) -> PredictSession:
    session = PredictSession()
    session.case_store.append_empty_rows(count)
    return session


def _column_index(model: CaseTableModel, key: str) -> int:
    return next(index for index, column in enumerate(model.columns) if column.key == key)


def test_complete_result_displays_result_status_and_message_columns():
    _app()
    session = _session_with_rows()
    case_id = session.case_order[0]
    session.set_result(
        ResultRow(
            case_id=case_id,
            status="complete",
            result_values={"cooling_power": "2.06", "eer": "3.45"},
            message="done",
        )
    )
    model = CaseTableModel(session)

    assert model.cell_value(0, _column_index(model, "cooling_power")) == "2.06"
    assert model.cell_value(0, _column_index(model, "eer")) == "3.45"
    assert model.cell_value(0, _column_index(model, "status")) == "complete"
    assert model.data(
        model.index(0, _column_index(model, "status")), Qt.DisplayRole
    ) == "완료"
    assert model.cell_value(0, _column_index(model, "message")) == "done"


def test_error_invalid_and_partial_status_render_background_and_tooltip():
    _app()
    session = _session_with_rows(3)
    statuses = (
        ("error", "model missing"),
        ("invalid", "bad input"),
        ("partial", "missing target"),
    )
    for row, (status, message) in enumerate(statuses):
        session.set_result(
            ResultRow(case_id=session.case_order[row], status=status, message=message)
        )
    model = CaseTableModel(session)
    status_col = _column_index(model, "status")

    for row, (status, message) in enumerate(statuses):
        index = model.index(row, status_col)
        assert model.cell_value(row, status_col) == status
        assert model.data(index, Qt.ToolTipRole) == message
        assert model.data(index, Qt.BackgroundRole).isValid()


def test_summary_counts_and_workspace_badge_include_partial_warnings():
    _app()
    session = _session_with_rows()
    session.set_result(
        ResultRow(case_id=session.case_order[0], status="partial", message="missing target")
    )
    workspace = PredictWorkspace(session=session)

    workspace._refresh_after_row_change()

    assert session.summary_counts()["warnings"] == 1
    assert "경고 1건" in workspace.summary_label.text()
    assert "경고" in workspace.result_badge.text()


def test_cancelled_status_counts_and_renders_as_warning():
    _app()
    session = _session_with_rows()
    session.set_result(
        ResultRow(
            case_id=session.case_order[0],
            status="cancelled",
            message="Prediction cancelled.",
        )
    )
    model = CaseTableModel(session)
    workspace = PredictWorkspace(session=session)
    status_col = _column_index(model, "status")

    workspace._refresh_after_row_change()

    assert session.summary_counts()["cancelled"] == 1
    assert session.summary_counts()["warnings"] == 1
    assert model.data(model.index(0, status_col), Qt.BackgroundRole).isValid()
    assert "취소 1건" in workspace.summary_label.text()


def test_running_callbacks_keep_progress_summary_badge_and_terminal_projection_aligned(
    monkeypatch,
):
    _app()
    session = _session_with_rows(3)
    workspace = PredictWorkspace(session=session)
    workspace.prediction_controller._service.model_status = (
        lambda: PredictionModelStatus("fake", "loaded")
    )
    workspace._refresh_prediction_command_state()
    first, second, invalid = session.case_order
    callbacks = {}

    def start_all(**received_callbacks):
        callbacks.update(received_callbacks)
        workspace.prediction_controller._is_running = True
        for result in (
            ResultRow(case_id=first, status="running"),
            ResultRow(case_id=second, status="running"),
            ResultRow(case_id=invalid, status="invalid", message="bad input"),
        ):
            session.set_result(result)
            received_callbacks["result_callback"](result)
        return PredictionRunSummary(
            total=3,
            complete=0,
            error=0,
            invalid=1,
        )

    monkeypatch.setattr(workspace.prediction_controller, "start_all", start_all)

    workspace._run_prediction()

    assert not workspace.command_bar.run_button.isEnabled()
    assert workspace.command_bar.cancel_button.isEnabled()
    assert "실행 중 2건" in workspace.summary_label.text()
    assert "입력 확인 1건" in workspace.summary_label.text()
    assert "실행 중 2건" in workspace.result_badge.text()
    assert workspace.status_label.text() == "예측 실행 중..."

    session.set_result(ResultRow(case_id=first, status="complete"))
    callbacks["result_callback"](session.result_for_case(first))
    callbacks["progress_callback"](
        PredictionProgress(
            run_id="run-projection",
            completed=1,
            total=2,
            current_case_id=first,
        )
    )

    assert "예측 완료 1건" in workspace.summary_label.text()
    assert "실행 중 1건" in workspace.summary_label.text()
    assert "실행 중 1건" in workspace.result_badge.text()
    assert "1/2" in workspace.status_label.text()
    assert session.result_for_case(invalid).status == "invalid"

    session.set_result(ResultRow(case_id=second, status="error", message="row failed"))
    callbacks["result_callback"](session.result_for_case(second))
    callbacks["progress_callback"](
        PredictionProgress(
            run_id="run-projection",
            completed=2,
            total=2,
            current_case_id=second,
        )
    )
    workspace.prediction_controller._is_running = False
    callbacks["finished_callback"](
        PredictionRunSummary(
            total=3,
            complete=1,
            error=1,
            invalid=1,
        )
    )

    counts = session.summary_counts()
    assert (counts["completed"], counts["running"], counts["errors"]) == (1, 0, 1)
    assert "실행 중 0건" in workspace.summary_label.text()
    assert "오류 1건" in workspace.result_badge.text()
    assert "완료 1건" in workspace.status_label.text()
    assert workspace.command_bar.run_button.isEnabled()
    assert not workspace.command_bar.cancel_button.isEnabled()


def test_copy_includes_selected_result_status_values_and_mutation_is_blocked():
    _app()
    session = _session_with_rows()
    case_id = session.case_order[0]
    session.set_result(
        ResultRow(
            case_id=case_id,
            status="error",
            result_values={"cooling_power": "2.0"},
            message="missing model",
        )
    )
    model = CaseTableModel(session)
    view = CaseTableView()
    view.setModel(model)
    power = _column_index(model, "cooling_power")
    status = _column_index(model, "status")
    message = _column_index(model, "message")
    selection = view.selectionModel()
    selection.setCurrentIndex(model.index(0, power), QItemSelectionModel.ClearAndSelect)
    selection.select(model.index(0, status), QItemSelectionModel.Select)
    selection.select(model.index(0, message), QItemSelectionModel.Select)

    assert view.copy_selection_tsv().endswith("error\tmissing model\n")
    assert view.clear_selection() == 0
    assert view.paste_tsv_at_selection("changed\tchanged\tchanged\n") == 0
    assert model.cell_value(0, power) == "2.0"
    assert model.cell_value(0, status) == "error"


def test_refresh_case_id_emits_row_refresh_for_result_status_change():
    _app()
    session = _session_with_rows()
    model = CaseTableModel(session)
    case_id = session.case_order[0]
    calls: list[tuple[int, int]] = []
    model.dataChanged.connect(
        lambda top_left, bottom_right, _roles: calls.append(
            (top_left.row(), bottom_right.column())
        )
    )
    session.set_result(ResultRow(case_id=case_id, status="complete"))

    model.refresh_case_id(case_id)

    assert calls == [(0, model.columnCount() - 1)]
