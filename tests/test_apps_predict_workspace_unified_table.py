"""Predict workspace unified case table integration tests."""

import os
from pathlib import Path

import pytest
from PySide6.QtCore import QItemSelectionModel, Qt
from PySide6.QtWidgets import QApplication, QFrame

from apps.common.ui.tables.clipboard import format_tsv, parse_tsv
from apps.predict.schema.case_table_schema_adapter import build_case_table_column_schema
from apps.predict.controllers.table_edit_controller import TableEditController
from apps.predict.controllers.prediction_controller import PredictionRunSummary
from apps.predict.state.predict_session import PredictSession
from apps.predict.state.result_row import ResultRow
from apps.predict.ports.prediction_execution_port import PredictionProgress
from apps.predict.ui.tables.case_table_view import CaseTableView
from apps.predict.ui.tables.group_header import TableLinkedGroupHeader
from apps.predict.ui.workspace import PredictWorkspace


def _app() -> QApplication:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    return QApplication.instance() or QApplication([])


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


def _column_index(workspace: PredictWorkspace, key: str) -> int:
    return next(
        index for index, column in enumerate(workspace.case_model.columns) if column.key == key
    )


def test_workspace_uses_one_unified_case_table_without_split_sync():
    _app()
    workspace = PredictWorkspace()

    assert isinstance(workspace.case_table, CaseTableView)
    assert workspace.case_table.model() is workspace.case_model
    assert workspace.findChildren(CaseTableView) == [workspace.case_table]
    assert not hasattr(workspace, "table_sync")


def test_predict_tsv_helpers_normalize_and_format_table_payloads():
    assert parse_tsv("a\tb\r\nc\td\r\n") == [["a", "b"], ["c", "d"]]
    assert parse_tsv("a\tb\rc\td") == [["a", "b"], ["c", "d"]]
    assert parse_tsv("") == []
    assert format_tsv([["a", None], [1, "b"]]) == "a\t\n1\tb\n"


def test_workspace_unified_table_schema_and_readonly_result_status_columns():
    _app()
    workspace = PredictWorkspace()

    assert workspace.case_model.rowCount() == 3
    assert workspace.case_model.columnCount() == len(build_case_table_column_schema())

    for key in ("cooling_power", "status", "message"):
        index = workspace.case_model.index(0, _column_index(workspace, key))
        assert workspace.case_model.flags(index) & Qt.ItemIsSelectable
        assert not (workspace.case_model.flags(index) & Qt.ItemIsEditable)


def test_workspace_copy_includes_selected_result_and_status_cells():
    _app()
    workspace = PredictWorkspace()
    case_id = workspace.session.case_order[0]
    workspace.session.set_result(
        ResultRow(
            case_id=case_id,
            status="complete",
            result_values={"cooling_power": "2.06"},
            message="ok",
        )
    )
    workspace.case_model.refresh_case_id(case_id)

    power = workspace.case_model.index(0, _column_index(workspace, "cooling_power"))
    status = workspace.case_model.index(0, _column_index(workspace, "status"))
    message = workspace.case_model.index(0, _column_index(workspace, "message"))
    selection = workspace.case_table.selectionModel()
    selection.setCurrentIndex(power, QItemSelectionModel.ClearAndSelect)
    selection.select(status, QItemSelectionModel.Select)
    selection.select(message, QItemSelectionModel.Select)

    assert workspace.case_table.copy_selection_tsv() == "2.06\t\t\t\t\t\t\t\t\tcomplete\tok\n"


def test_workspace_row_lifecycle_updates_unified_model():
    _app()
    workspace = PredictWorkspace()

    initial_rows = workspace.case_model.rowCount()
    workspace._append_row()
    assert workspace.case_model.rowCount() == initial_rows + 1
    workspace._delete_selected_or_last_row()
    assert workspace.case_model.rowCount() == initial_rows
    workspace._reset_rows()
    assert workspace.case_model.rowCount() == 3


def test_table_edit_controller_owns_row_lifecycle_and_result_clearing():
    session = PredictSession()
    controller = TableEditController(session)
    controller.ensure_initial_rows(2)
    case_id = session.case_order[0]
    session.set_result(ResultRow(case_id=case_id, status="complete"))

    assert controller.append_row_span(1) == (2, 2)
    controller.append_empty_rows(1)
    assert len(session.case_store) == 3

    group = controller.removal_groups_for_indexes([0])[0]
    assert group.first_row == 0
    assert group.last_row == 0
    assert group.case_ids == (case_id,)
    assert controller.remove_case_ids(group.case_ids) == [case_id]
    assert session.result_for_case(case_id).status == "pending"


def test_workspace_does_not_directly_mutate_case_store_rows():
    source = Path("apps/predict/ui/workspace.py").read_text(encoding="utf-8")

    assert "case_store.append_empty_rows" not in source
    assert "case_store.remove_rows" not in source


def test_workspace_reset_clears_table_undo_history():
    _app()
    workspace = PredictWorkspace()
    cooling = _column_index(workspace, "cooling_capa")
    index = workspace.case_model.index(0, cooling)
    workspace.case_table.selectionModel().setCurrentIndex(
        index,
        QItemSelectionModel.ClearAndSelect,
    )

    assert workspace.case_table.replace_current_cell("7.1")
    assert workspace.case_model.cell_value(0, cooling) == "7.1"
    workspace._reset_rows()

    assert workspace.case_table.undo() == 0
    assert workspace.case_model.cell_value(0, cooling) == ""


@pytest.mark.parametrize(
    ("result_status", "summary", "terminal_text"),
    (
        (
            "complete",
            PredictionRunSummary(total=3, complete=1, error=0, invalid=0),
            "예측 완료",
        ),
        (
            "invalid",
            PredictionRunSummary(total=3, complete=0, error=0, invalid=1),
            "입력 확인 1건",
        ),
        (
            "error",
            PredictionRunSummary(total=3, complete=0, error=1, invalid=0),
            "오류 1건",
        ),
        (
            "cancelled",
            PredictionRunSummary(
                total=3,
                complete=0,
                error=0,
                invalid=0,
                cancelled=1,
            ),
            "예측 취소",
        ),
    ),
)
def test_workspace_reset_reprojects_terminal_session_as_idle(
    result_status: str,
    summary: PredictionRunSummary,
    terminal_text: str,
):
    _app()
    workspace = PredictWorkspace()
    model_status = workspace.model_badge.text()
    case_id = workspace.session.case_order[0]
    workspace.session.set_result(
        ResultRow(case_id=case_id, status=result_status, message="terminal")
    )
    workspace.case_model.refresh_case_id(case_id)
    workspace._set_running_state(True)
    workspace._handle_prediction_progress(
        PredictionProgress(
            run_id="run-reset",
            completed=1,
            total=3,
            current_case_id=case_id,
        )
    )
    workspace._handle_prediction_finished(summary)

    assert terminal_text in workspace.status_label.text()

    workspace._reset_rows()

    counts = workspace.session.summary_counts()
    assert counts == {
        "total": 3,
        "completed": 0,
        "errors": 0,
        "running": 0,
        "invalid": 0,
        "cancelled": 0,
        "warnings": 0,
        "dirty": 0,
    }
    assert all(
        workspace.session.result_for_case(case_id).status == "pending"
        for case_id in workspace.session.case_order
    )
    assert "실행 중 0건" in workspace.summary_label.text()
    assert "예측 완료 0건" in workspace.summary_label.text()
    assert "취소 0건" in workspace.summary_label.text()
    assert "대기" in workspace.result_badge.text()
    assert workspace.status_label.text() == "대기 중"
    assert workspace.command_bar.run_button.isEnabled()
    assert not workspace.command_bar.cancel_button.isEnabled()
    assert workspace.command_bar.reset_button.isEnabled()
    assert workspace.model_badge.text() == model_status


def test_workspace_reset_allows_new_input_and_next_prediction(monkeypatch):
    _app()
    workspace = PredictWorkspace()
    case_id = workspace.session.case_order[0]
    workspace.session.set_result(ResultRow(case_id=case_id, status="complete"))
    workspace._handle_prediction_finished(
        PredictionRunSummary(total=3, complete=1, error=0, invalid=0)
    )
    workspace._reset_rows()

    cooling = _column_index(workspace, "cooling_capa")
    index = workspace.case_model.index(0, cooling)
    workspace.case_table.selectionModel().setCurrentIndex(
        index,
        QItemSelectionModel.ClearAndSelect,
    )
    assert workspace.case_table.replace_current_cell("3500")

    calls = []

    def start_all(**callbacks):
        calls.append(tuple(callbacks))
        callbacks["finished_callback"](
            PredictionRunSummary(total=3, complete=1, error=0, invalid=0)
        )

    monkeypatch.setattr(workspace.prediction_controller, "start_all", start_all)

    workspace._run_prediction()

    assert len(calls) == 1
    assert workspace.case_model.cell_value(0, cooling) == "3500"
    assert "예측 완료" in workspace.status_label.text()
    assert workspace.command_bar.run_button.isEnabled()
    assert not workspace.command_bar.cancel_button.isEnabled()


def test_workspace_start_failure_hides_technical_detail_and_allows_retry(monkeypatch):
    _app()
    workspace = PredictWorkspace()
    calls = []

    def fail_start(**_callbacks):
        calls.append("failed")
        raise RuntimeError("internal worker path /tmp/worker.py\ntraceback")

    monkeypatch.setattr(workspace.prediction_controller, "start_all", fail_start)

    workspace._run_prediction()

    assert calls == ["failed"]
    assert workspace.status_label.text() == (
        "예측 실행 중 오류가 발생했습니다. 입력을 확인한 뒤 다시 시도해 주세요."
    )
    assert "/tmp/worker.py" not in workspace.status_label.text()
    assert workspace.command_bar.run_button.isEnabled()
    assert not workspace.command_bar.cancel_button.isEnabled()


def test_workspace_command_bar_running_state_disables_row_mutation():
    _app()
    workspace = PredictWorkspace()

    workspace._set_running_state(True)

    assert not workspace.command_bar.run_button.isEnabled()
    assert workspace.command_bar.cancel_button.isEnabled()
    assert not workspace.command_bar.reset_button.isEnabled()
    assert not workspace.command_bar.add_row_button.isEnabled()
    assert not workspace.command_bar.delete_row_button.isEnabled()
    assert not workspace.command_bar.paste_button.isEnabled()

    workspace._set_running_state(False)

    assert workspace.command_bar.run_button.isEnabled()
    assert not workspace.command_bar.cancel_button.isEnabled()
    assert workspace.command_bar.add_row_button.isEnabled()


def test_workspace_row_mutation_commands_are_guarded_while_controller_running():
    _app()
    workspace = PredictWorkspace()
    workspace.prediction_controller._is_running = True
    initial_rows = workspace.case_model.rowCount()

    workspace._append_row()
    workspace._delete_selected_or_last_row()
    workspace._reset_rows()

    assert workspace.case_model.rowCount() == initial_rows
    assert "행 변경" in workspace.status_label.text()


def test_workspace_progress_and_finished_callbacks_update_status():
    _app()
    workspace = PredictWorkspace()
    workspace._set_running_state(True)

    workspace._handle_prediction_progress(
        PredictionProgress(
            run_id="run-1",
            completed=1,
            total=4,
            current_case_id="case-0001",
        )
    )

    assert "1/4" in workspace.status_label.text()
    assert "25%" in workspace.status_label.text()

    workspace._handle_prediction_finished(
        PredictionRunSummary(total=4, complete=1, error=0, invalid=0, cancelled=3)
    )

    assert workspace.command_bar.run_button.isEnabled()
    assert not workspace.command_bar.cancel_button.isEnabled()
    assert "취소 3건" in workspace.status_label.text()


def test_workspace_no_direct_model_file_status_owner():
    source = Path("apps/predict/ui/workspace.py").read_text(encoding="utf-8")

    assert "MODEL_FILE" not in source
    assert "core.ml.artifacts" not in source


def test_workspace_delegates_concrete_dependency_composition():
    source = Path("apps/predict/ui/workspace.py").read_text(encoding="utf-8")

    assert "build_predict_workspace_composition" in source
    assert "PySidePredictionRunner" not in source
    assert "PredictMappingRepository()" not in source
    assert "PredictionController(" not in source


def test_unified_group_header_is_table_linked_not_detached_band():
    _app()
    workspace = PredictWorkspace()

    assert isinstance(workspace.group_header, TableLinkedGroupHeader)
    assert workspace.findChildren(QFrame, "ColumnGroupBand") == []

    source = Path("apps/predict/ui/workspace.py").read_text(encoding="utf-8")
    assert "ColumnGroupBand" not in source


def test_unified_group_header_tracks_horizontal_scroll():
    app = _app()
    workspace = PredictWorkspace()
    workspace.resize(640, 420)
    workspace.show()
    app.processEvents()

    scroll_bar = workspace.case_table.horizontalScrollBar()
    assert scroll_bar.maximum() > 0
    before = workspace.group_header.group_rects()["auto"].x()

    scroll_bar.setValue(scroll_bar.maximum())
    app.processEvents()

    assert workspace.group_header.group_rects()["auto"].x() < before


def test_unified_group_header_tracks_section_resize():
    app = _app()
    workspace = PredictWorkspace()
    workspace.resize(900, 420)
    workspace.show()
    app.processEvents()

    input_width = workspace.group_header.group_column_rects()["input"].width()
    column_width = workspace.case_table.columnWidth(0)
    workspace.case_table.setColumnWidth(0, column_width + 40)
    app.processEvents()

    assert workspace.group_header.group_column_rects()["input"].width() == input_width + 40
