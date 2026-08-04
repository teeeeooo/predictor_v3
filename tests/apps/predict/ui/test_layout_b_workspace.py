"""Shared Predict Layout B composition and command routing tests."""

import csv
import os

import pytest
from PySide6.QtCore import QItemSelectionModel, Qt
from PySide6.QtWidgets import QApplication

from apps.predict.application.models import PredictionModelStatus
from apps.predict.application.prediction_usecase import PredictionRunSummary
from apps.predict.application.workspace_state import WorkspaceSurface
from apps.predict.composition import build_predict_workspace_composition
from apps.predict.state.result_row import ResultRow
from apps.predict.ui.result_review import csv_export as result_review_csv_export
from apps.predict.ui.workspace import PredictWorkspace
from tests.helpers.predict_results import accept_result_fixtures


class _LoadedPredictionService:
    def model_status(self):
        return PredictionModelStatus("fake", "loaded")


def _app() -> QApplication:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    return QApplication.instance() or QApplication([])


def _workspace() -> PredictWorkspace:
    return PredictWorkspace(
        composition=build_predict_workspace_composition(
            prediction_service=_LoadedPredictionService(),
        )
    )


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


def test_layout_b_starts_on_input_and_both_models_read_one_session():
    _app()
    workspace = _workspace()

    assert workspace.workspace_state.current_surface is WorkspaceSurface.INPUT
    assert workspace.surface_host.stack.currentIndex() == 0
    assert workspace.case_model._session is workspace.session
    assert workspace.result_review_model.projection.session is workspace.session
    assert workspace.result_review_model.rowCount() == workspace.case_model.rowCount()


def test_stable_current_case_transfers_but_surface_selections_remain_local():
    _app()
    workspace = _workspace()
    input_selection = workspace.case_table.selectionModel()
    input_selection.setCurrentIndex(
        workspace.case_model.index(1, 2),
        QItemSelectionModel.ClearAndSelect,
    )
    input_selection.select(
        workspace.case_model.index(2, 3),
        QItemSelectionModel.Select,
    )
    input_selected = {(index.row(), index.column()) for index in input_selection.selectedIndexes()}

    workspace._switch_surface(WorkspaceSurface.RESULT)
    result_selection = workspace.result_review_table.selectionModel()

    assert result_selection.currentIndex().row() == 1
    assert workspace.workspace_state.selected_case_id == workspace.session.case_order[1]
    result_selection.setCurrentIndex(
        workspace.result_review_model.index(0, 0),
        QItemSelectionModel.NoUpdate,
    )
    result_selection.select(
        workspace.result_review_model.index(0, 0),
        QItemSelectionModel.Select | QItemSelectionModel.Rows,
    )
    assert {(index.row(), index.column()) for index in input_selection.selectedIndexes()} == input_selected

    workspace._switch_surface(WorkspaceSurface.INPUT)
    assert input_selection.currentIndex().row() == 0
    assert result_selection.selectedRows()


def test_surfaces_keep_independent_horizontal_scroll_with_result_anchor():
    _app()
    workspace = _workspace()
    input_scroll = workspace.case_table.horizontalScrollBar()
    result_scroll = workspace.result_review_table.horizontalScrollBar()
    input_scroll.setRange(0, 80)
    result_scroll.setRange(0, 120)
    input_scroll.setValue(21)
    result_scroll.setValue(73)

    workspace._switch_surface(WorkspaceSurface.RESULT)
    workspace._switch_surface(WorkspaceSurface.INPUT)

    assert input_scroll is not result_scroll
    assert input_scroll.value() == 21
    assert result_scroll.value() == 73
    assert workspace.surface_host.stack.count() == 2


def test_deleted_selected_case_is_reconciled_without_dangling_identity():
    _app()
    workspace = _workspace()
    deleted_case_id = workspace.session.case_order[1]
    selection = workspace.case_table.selectionModel()
    selection.setCurrentIndex(
        workspace.case_model.index(1, 0),
        QItemSelectionModel.ClearAndSelect,
    )

    workspace._delete_selected_or_last_row()

    assert deleted_case_id not in workspace.session.case_order
    assert workspace.workspace_state.selected_case_id in workspace.session.case_order
    assert workspace.result_review_model.rowCount() == workspace.case_model.rowCount()


def test_result_surface_blocks_authoring_and_routes_full_row_copy():
    _app()
    workspace = _workspace()
    initial_rows = workspace.case_model.rowCount()
    workspace._switch_surface(WorkspaceSurface.RESULT)
    selection = workspace.result_review_table.selectionModel()
    selection.select(
        workspace.result_review_model.index(0, 0),
        QItemSelectionModel.Select | QItemSelectionModel.Rows,
    )

    workspace._append_row()
    workspace._delete_selected_or_last_row()
    workspace._reset_rows()
    workspace._copy_results_selection()

    copied = QApplication.clipboard().text()
    assert workspace.case_model.rowCount() == initial_rows
    assert copied.splitlines()[0].split("\t")[:10] == [
        "Case", "상태", "냉방능력", "난방능력", "사양 요약",
        "EER", "COP", "냉방 주파수", "난방 주파수", "냉매량",
    ]
    assert "stable case identity" in copied.splitlines()[0].split("\t")[10:]
    assert workspace.command_bar.copy_results_button.text() == "결과 전체 행 복사"


def test_input_copy_keeps_selected_cell_behavior():
    _app()
    workspace = _workspace()
    index = workspace.case_model.index(0, 0)
    workspace.case_table.selectionModel().setCurrentIndex(
        index,
        QItemSelectionModel.ClearAndSelect,
    )

    workspace._copy_results_selection()

    assert QApplication.clipboard().text() == workspace.case_table.copy_selection_tsv()
    assert workspace.command_bar.copy_results_button.text() == "선택 셀 복사"
    assert not workspace.command_bar.export_results_button.isEnabled()


def test_progressive_result_refreshes_visible_readonly_projection_without_switching():
    _app()
    workspace = _workspace()
    workspace._switch_surface(WorkspaceSurface.RESULT)
    case_id = workspace.session.case_order[0]
    result = ResultRow(case_id=case_id, status="error", message="bounded issue")
    accept_result_fixtures(workspace.session, result)

    workspace._refresh_result_row(result)

    assert workspace.workspace_state.current_surface is WorkspaceSurface.RESULT
    assert workspace.result_review_model.data(
        workspace.result_review_model.index(0, 1), Qt.DisplayRole
    ) != "대기"
    assert workspace.session.result_for_case(case_id).message == "bounded issue"


def test_run_surface_policy_is_shared_with_workspace_callbacks(monkeypatch):
    _app()
    workspace = _workspace()
    callbacks = {}

    def start_all(**received):
        callbacks.update(received)
        return PredictionRunSummary(total=3, complete=0, error=0, invalid=0)

    monkeypatch.setattr(workspace.prediction_controller, "start_all", start_all)
    workspace._switch_surface(WorkspaceSurface.RESULT)
    workspace._run_prediction()

    assert workspace.workspace_state.run_start_surface is WorkspaceSurface.RESULT
    assert workspace.workspace_state.current_surface is WorkspaceSurface.RESULT
    workspace._switch_surface(WorkspaceSurface.INPUT)
    callbacks["finished_callback"](
        PredictionRunSummary(total=3, complete=1, partial=0, error=0, invalid=0)
    )
    assert workspace.workspace_state.current_surface is WorkspaceSurface.INPUT

    workspace._run_prediction()
    callbacks["finished_callback"](
        PredictionRunSummary(total=3, complete=0, partial=1, error=0, invalid=0)
    )
    assert workspace.workspace_state.current_surface is WorkspaceSurface.RESULT


def test_runtime_rebind_preserves_workspace_state_and_replaces_both_models():
    _app()
    workspace = _workspace()
    original_state = workspace.workspace_state
    selected_case_id = workspace.session.case_order[1]
    workspace.workspace_state.select_case(selected_case_id, workspace.session.case_order)
    workspace._switch_surface(WorkspaceSurface.RESULT)
    replacement = build_predict_workspace_composition(
        session=workspace.session,
        initial_empty_rows=0,
        prediction_service=_LoadedPredictionService(),
    )

    workspace.apply_runtime_composition(replacement)

    assert workspace.workspace_state is original_state
    assert workspace.workspace_state.current_surface is WorkspaceSurface.RESULT
    assert workspace.workspace_state.selected_case_id == selected_case_id
    assert workspace.case_model.columns == replacement.columns
    assert workspace.result_review_model.projection is replacement.result_review_projection


def test_runtime_rebind_retains_result_anchor_widths_scroll_and_shared_selection():
    app = _app()
    workspace = PredictWorkspace(
        composition=build_predict_workspace_composition(
            initial_empty_rows=30,
            prediction_service=_LoadedPredictionService(),
        )
    )
    workspace.resize(720, 520)
    workspace.show()
    workspace._switch_surface(WorkspaceSurface.RESULT)
    app.processEvents()
    table = workspace.result_review_table
    table.setColumnWidth(0, 78)
    table.setColumnWidth(1, 126)
    table.setRowHeight(1, 47)
    table.horizontalScrollBar().setValue(table.horizontalScrollBar().maximum())
    prior_scroll = table.horizontalScrollBar().value()
    table.verticalScrollBar().setValue(8)
    selected_case_id = workspace.session.case_order[1]
    table.selectionModel().setCurrentIndex(
        workspace.result_review_model.index(1, 1),
        QItemSelectionModel.ClearAndSelect | QItemSelectionModel.Rows,
    )
    replacement = build_predict_workspace_composition(
        session=workspace.session,
        initial_empty_rows=0,
        prediction_service=_LoadedPredictionService(),
    )

    workspace.apply_runtime_composition(replacement)
    app.processEvents()

    assert table.pinned_columns_active
    assert table.pinned_anchor_view.columnWidth(0) == 78
    assert table.pinned_anchor_view.columnWidth(1) == 126
    assert table.horizontalScrollBar().value() == min(
        prior_scroll, table.horizontalScrollBar().maximum()
    )
    assert table.pinned_anchor_view.verticalScrollBar().value() == (
        table.verticalScrollBar().value()
    )
    assert table.rowHeight(1) == 47
    assert table.pinned_anchor_view.rowHeight(1) == 47
    assert table.pinned_anchor_view.model() is workspace.result_review_model
    assert table.pinned_anchor_view.selectionModel() is table.selectionModel()
    assert workspace.workspace_state.selected_case_id == selected_case_id
    assert table.selectionModel().currentIndex().row() == 1


@pytest.mark.parametrize(
    ("selected_rows", "expected_cases"),
    (((1,), ["2"]), ((2, 0), ["1", "3"])),
)
def test_result_csv_action_exports_selected_rows_in_canonical_order(
    tmp_path, monkeypatch, selected_rows, expected_cases
):
    _app()
    workspace = _workspace()
    destination = tmp_path / "selected.csv"
    workspace._switch_surface(WorkspaceSurface.RESULT)
    selection = workspace.result_review_table.selectionModel()
    for row in selected_rows:
        selection.select(
            workspace.result_review_model.index(row, 0),
            QItemSelectionModel.Select | QItemSelectionModel.Rows,
        )
    monkeypatch.setattr(
        result_review_csv_export.QFileDialog,
        "getSaveFileName",
        lambda *args, **kwargs: (str(destination), "CSV files (*.csv)"),
    )

    workspace.command_bar.export_results_button.click()

    with destination.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.reader(handle))
    assert [row[0] for row in rows[1:]] == expected_cases
    assert "stable case identity" in rows[0][10:]
    assert workspace.command_bar.export_results_button.isEnabled()
    assert "저장 완료" in workspace.status_label.text()


def test_result_csv_without_selection_does_not_open_dialog_or_publish(monkeypatch):
    _app()
    workspace = _workspace()
    workspace._switch_surface(WorkspaceSurface.RESULT)

    def unexpected_dialog(*args, **kwargs):  # noqa: ANN002, ANN003
        pytest.fail("save dialog must not open without selected Result Review rows")

    monkeypatch.setattr(
        result_review_csv_export.QFileDialog,
        "getSaveFileName",
        unexpected_dialog,
    )

    workspace.command_bar.export_results_button.click()

    assert "선택" in workspace.status_label.text()
    assert workspace.result_review_table.selected_row_indexes() == []


def test_result_csv_cancel_preserves_canonical_state_and_selection(monkeypatch):
    _app()
    workspace = _workspace()
    workspace._switch_surface(WorkspaceSurface.RESULT)
    selection = workspace.result_review_table.selectionModel()
    selection.select(
        workspace.result_review_model.index(1, 0),
        QItemSelectionModel.Select | QItemSelectionModel.Rows,
    )
    before_revision = workspace.session.revision
    before_results = dict(workspace.session.results_by_case_id)
    before_selected = workspace.result_review_table.selected_row_indexes()
    monkeypatch.setattr(
        result_review_csv_export.QFileDialog,
        "getSaveFileName",
        lambda *args, **kwargs: ("", ""),
    )

    workspace.command_bar.export_results_button.click()

    assert workspace.session.revision == before_revision
    assert dict(workspace.session.results_by_case_id) == before_results
    assert workspace.result_review_table.selected_row_indexes() == before_selected
    assert "취소" in workspace.status_label.text()


def test_result_csv_publication_failure_preserves_state_and_selection(monkeypatch):
    _app()
    workspace = _workspace()
    workspace._switch_surface(WorkspaceSurface.RESULT)
    selection = workspace.result_review_table.selectionModel()
    selection.select(
        workspace.result_review_model.index(0, 0),
        QItemSelectionModel.Select | QItemSelectionModel.Rows,
    )
    before_revision = workspace.session.revision
    before_results = dict(workspace.session.results_by_case_id)
    before_selected = workspace.result_review_table.selected_row_indexes()
    monkeypatch.setattr(
        result_review_csv_export.QFileDialog,
        "getSaveFileName",
        lambda *args, **kwargs: ("/unwritable/result.csv", "CSV files (*.csv)"),
    )

    def fail_publication(*args, **kwargs):  # noqa: ANN002, ANN003
        raise OSError("publication denied")

    monkeypatch.setattr(
        result_review_csv_export,
        "publish_result_review_csv",
        fail_publication,
    )

    workspace.command_bar.export_results_button.click()

    assert workspace.session.revision == before_revision
    assert dict(workspace.session.results_by_case_id) == before_results
    assert workspace.result_review_table.selected_row_indexes() == before_selected
    assert "문제가" in workspace.status_label.text()
