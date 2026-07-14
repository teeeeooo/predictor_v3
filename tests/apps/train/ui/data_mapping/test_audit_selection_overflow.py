"""Audit correction regression for paste bounds and rectangle selection."""

from __future__ import annotations

import os
from pathlib import Path

import pytest
from PySide6.QtCore import QItemSelection, QItemSelectionModel, Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QAbstractItemView

from apps.train.controllers.data_mapping_controller import DataMappingController
from apps.train.services.data_mapping_service import (
    DataMappingService,
    RuntimeMappingCatalogProvider,
)
from apps.train.ui.data_mapping_panel import DataMappingPanel
from apps.train.ui.data_mapping.table_view import PASTE_OVERFLOW_MESSAGE

RUNTIME_FIXTURE = Path("tests/fixtures/mapping/mapping_runtime_equivalent.json")


def _app() -> QApplication:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    return QApplication.instance() or QApplication([])


@pytest.fixture(autouse=True)
def _cleanup_widgets():
    yield
    app = QApplication.instance()
    if app is not None:
        for widget in QApplication.topLevelWidgets():
            widget.close()
            widget.deleteLater()
        app.processEvents()


def _panel() -> tuple[DataMappingPanel, DataMappingService]:
    _app()
    service = DataMappingService(RuntimeMappingCatalogProvider(str(RUNTIME_FIXTURE)))
    panel = DataMappingPanel(controller=DataMappingController(service))
    panel.show()
    QApplication.processEvents()
    return panel, service


def _select_rect(
    panel: DataMappingPanel,
    top: int,
    left: int,
    bottom: int,
    right: int,
) -> None:
    view = panel.row_table
    model = view.model()
    selection = QItemSelection(model.index(top, left), model.index(bottom, right))
    view.selectionModel().select(selection, QItemSelectionModel.ClearAndSelect)
    view.selectionModel().setCurrentIndex(model.index(top, left), QItemSelectionModel.NoUpdate)


@pytest.mark.parametrize("edge", ("right", "bottom", "both"))
def test_paste_overflow_blocks_atomically_without_history_or_selection_change(edge):
    panel, service = _panel()
    model = panel.row_table.model()
    last_row = model.rowCount() - 1
    last_column = model.columnCount() - 1
    if edge == "right":
        anchor, text = (0, last_column), "x\ty"
    elif edge == "bottom":
        anchor, text = (last_row, 0), "x\ny"
    else:
        anchor, text = (last_row, last_column), "x\ty\nz\tw"
    _select_rect(panel, *anchor, *anchor)
    before = service.current_snapshot()
    shape = (model.rowCount(), model.columnCount())

    assert panel.row_table.paste_tsv_at_selection(text) == 0

    after = service.current_snapshot()
    assert after.draft == before.draft
    assert after.dirty == before.dirty
    assert (panel.row_table.model().rowCount(), panel.row_table.model().columnCount()) == shape
    assert (panel.row_table.currentIndex().row(), panel.row_table.currentIndex().column()) == anchor
    assert panel.status_label.text() == PASTE_OVERFLOW_MESSAGE
    _snapshot, undo = service.undo()
    assert undo.applied == 0


def test_semantically_equal_numeric_tsv_paste_stays_clean_and_canonical():
    panel, service = _panel()
    _select_rect(panel, 0, 1, 0, 1)

    assert panel.row_table.paste_tsv_at_selection("54.0") == 0

    snapshot = service.current_snapshot()
    value = snapshot.draft.group("idu").rows[0].value_for("ID Volume")
    assert value == 54
    assert type(value) is int
    assert not snapshot.dirty


def test_contiguous_selection_supports_shift_rectangle_and_rejects_ctrl_multirange():
    panel, _service = _panel()
    view = panel.row_table
    model = view.model()
    assert view.selectionMode() == QAbstractItemView.ContiguousSelection

    first = model.index(0, 1)
    opposite = model.index(1, 2)
    QTest.mouseClick(view.viewport(), Qt.LeftButton, Qt.NoModifier, view.visualRect(first).center())
    QTest.mouseClick(
        view.viewport(),
        Qt.LeftButton,
        Qt.ShiftModifier,
        view.visualRect(opposite).center(),
    )
    selected = {(index.row(), index.column()) for index in view.selectionModel().selectedIndexes()}
    assert selected == {(0, 1), (0, 2), (1, 1), (1, 2)}

    distant = model.index(2, 0)
    QTest.mouseClick(
        view.viewport(),
        Qt.LeftButton,
        Qt.ControlModifier,
        view.visualRect(distant).center(),
    )
    selected = {(index.row(), index.column()) for index in view.selectionModel().selectedIndexes()}
    rows = {row for row, _column in selected}
    columns = {column for _row, column in selected}
    assert len(selected) == len(rows) * len(columns)


def test_copy_and_clear_normalize_the_same_complete_rectangle():
    panel, service = _panel()
    view = panel.row_table
    model = view.model()
    selection = view.selectionModel()
    selection.select(model.index(0, 1), QItemSelectionModel.ClearAndSelect)
    selection.select(model.index(1, 2), QItemSelectionModel.Select)
    selection.setCurrentIndex(model.index(0, 1), QItemSelectionModel.NoUpdate)

    assert view.copy_selection_tsv() == "54\t1\n60\t2\n"
    assert view.clear_selection() == 4
    updated_model = view.model()
    assert [updated_model.cell_value(row, column) for row in (0, 1) for column in (1, 2)] == [
        "",
        "",
        "",
        "",
    ]

    restored, undo = service.undo()
    assert undo.applied == 1
    assert not restored.dirty


def test_in_bounds_pfc_target_stays_partial_non_shifting_and_grouped():
    panel, service = _panel()
    group_row = panel._group_keys.index("odu_cond_specs")
    panel.entity_table.setCurrentIndex(panel.entity_table.model().index(group_row, 0))
    QApplication.processEvents()
    model = panel.row_table.model()
    original_pi = model.cell_value(4, 2)
    original_row = model.cell_value(4, 3)
    _select_rect(panel, 4, 2, 4, 2)

    assert panel.row_table.paste_tsv_at_selection("99\t2") == 1
    assert panel._current_state.operation_blocked == 1
    assert panel.row_table.model().cell_value(4, 2) == original_pi
    assert panel.row_table.model().cell_value(4, 3) == "2"

    restored, undo = service.undo()
    assert undo.applied == 1
    row = restored.draft.group("odu_cond_specs").rows[4]
    assert row.value_for("Pi") == original_pi
    assert str(row.value_for("Row")) == original_row
