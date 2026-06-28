"""Predict workspace unified case table integration tests."""

import os
from pathlib import Path

import pytest
from PySide6.QtCore import QItemSelectionModel, Qt
from PySide6.QtWidgets import QApplication, QFrame

from apps.predict.schema.case_table_schema_adapter import build_case_table_column_schema
from apps.predict.state.result_row import ResultRow
from apps.predict.ui.tables.case_table_view import CaseTableView
from apps.predict.ui.tables.group_header import TableLinkedGroupHeader
from apps.predict.ui.tables.input_table_view import InputTableView
from apps.predict.ui.tables.result_table_view import ResultTableView
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
    assert not workspace.findChildren(InputTableView)
    assert not workspace.findChildren(ResultTableView)
    assert not hasattr(workspace, "table_sync")


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
