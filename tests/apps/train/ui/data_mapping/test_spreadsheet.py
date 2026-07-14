"""Spreadsheet interaction regression for the Train Data Mapping table."""

from __future__ import annotations

import os
from pathlib import Path

import pytest
from PySide6.QtCore import QEvent, QItemSelection, QItemSelectionModel, Qt
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QApplication, QAbstractItemView

from apps.train.controllers.data_mapping_controller import DataMappingController
from apps.train.services.data_mapping_service import DataMappingService, RuntimeMappingCatalogProvider
from apps.train.ui.data_mapping_panel import DataMappingPanel
from apps.train.ui.data_mapping.table_view import DataMappingTableView
from core.data_definition.model import MappingRequirement

RUNTIME_FIXTURE = Path("tests/fixtures/mapping/mapping_runtime_equivalent.json")


class RequirementProvider:
    def load_mapping_requirements(self):
        return (
            MappingRequirement(
                column_key="fan_diameter",
                ml_name="Fan_Diameter",
                mapping_entity="idu",
                mapping_attribute="Fan Diameter",
                trigger_column="idu",
                data_type="number",
            ),
        )


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


def _panel(*, dynamic: bool = False) -> DataMappingPanel:
    _app()
    service = DataMappingService(
        RuntimeMappingCatalogProvider(str(RUNTIME_FIXTURE)),
        mapping_requirement_provider=RequirementProvider() if dynamic else None,
    )
    panel = DataMappingPanel(controller=DataMappingController(service))
    panel.show()
    QApplication.processEvents()
    return panel


def _select_group(panel: DataMappingPanel, group_key: str) -> None:
    row = panel._group_keys.index(group_key)
    panel.entity_table.setCurrentIndex(panel.entity_table.model().index(row, 0))
    QApplication.processEvents()


def _select_rect(view: DataMappingTableView, top: int, left: int, bottom: int, right: int) -> None:
    model = view.model()
    selection = QItemSelection(model.index(top, left), model.index(bottom, right))
    view.selectionModel().select(selection, QItemSelectionModel.ClearAndSelect)
    view.selectionModel().setCurrentIndex(model.index(top, left), QItemSelectionModel.NoUpdate)


def _send_key(view: DataMappingTableView, key: int, text: str = "", modifiers=Qt.NoModifier):
    QApplication.sendEvent(view, QKeyEvent(QEvent.KeyPress, key, modifiers, text))
    QApplication.processEvents()


def test_primary_table_uses_cell_rectangular_selection_and_visible_tsv_copy():
    panel = _panel()
    assert isinstance(panel.row_table, DataMappingTableView)
    assert panel.row_table.selectionBehavior() == QAbstractItemView.SelectItems
    assert panel.row_table.selectionMode() == QAbstractItemView.ExtendedSelection

    _select_rect(panel.row_table, 0, 0, 1, 1)
    copied = panel.row_table.copy_selection_tsv()

    assert copied == "MOT1\t54\nMOT2\t60\n"
    assert "hidden" not in copied.lower()


def test_rectangular_and_single_column_paste_are_grouped_undo_units():
    panel = _panel()
    before = panel.row_table.copy_selection_tsv()
    _select_rect(panel.row_table, 0, 1, 1, 2)

    assert panel.row_table.paste_tsv_at_selection("1.25\tS-X\n2.5\tS-Y\n") == 4
    assert panel.row_table.model().cell_value(0, 1) == "1.25"
    assert panel.row_table.model().cell_value(1, 2) == "S-Y"
    assert panel.row_table.undo() == 1
    assert panel.row_table.model().cell_value(0, 1) == "54"

    _select_rect(panel.row_table, 0, 1, 0, 1)
    assert panel.row_table.paste_tsv_at_selection("3.5\n4.5\n") == 2
    assert panel.row_table.model().cell_value(1, 1) == "4.5"
    assert before == ""


def test_clear_delete_backspace_and_printable_replace_are_grouped():
    panel = _panel()
    _select_rect(panel.row_table, 0, 1, 0, 2)

    _send_key(panel.row_table, Qt.Key_Delete)
    assert panel.row_table.model().cell_value(0, 1) == ""
    assert panel.row_table.model().cell_value(0, 2) == ""
    assert panel.row_table.undo() == 1
    assert panel.row_table.model().cell_value(0, 1) == "54"

    _select_rect(panel.row_table, 0, 2, 0, 2)
    _send_key(panel.row_table, Qt.Key_X, "X")
    assert panel.row_table.model().cell_value(0, 2) == "X"
    assert panel.row_table.undo() == 1

    _send_key(panel.row_table, Qt.Key_Backspace)
    assert panel.row_table.model().cell_value(0, 2) == ""


def test_tab_and_enter_navigation_keep_spreadsheet_current_cell():
    panel = _panel()
    _select_rect(panel.row_table, 0, 0, 0, 0)

    _send_key(panel.row_table, Qt.Key_Tab)
    assert panel.row_table.currentIndex() == panel.row_table.model().index(0, 1)
    _send_key(panel.row_table, Qt.Key_Backtab, modifiers=Qt.ShiftModifier)
    assert panel.row_table.currentIndex() == panel.row_table.model().index(0, 0)
    _send_key(panel.row_table, Qt.Key_Return)
    assert panel.row_table.currentIndex() == panel.row_table.model().index(1, 0)
    _send_key(panel.row_table, Qt.Key_Return, modifiers=Qt.ShiftModifier)
    assert panel.row_table.currentIndex() == panel.row_table.model().index(0, 0)


def test_pfc_pi_is_read_only_and_paste_does_not_shift_adjacent_value():
    panel = _panel()
    _select_group(panel, "odu_cond_specs")
    pi = panel.row_table.model().header_for_column(2)
    assert pi == "Pi"
    pfc_pi = panel.row_table.model().index(4, 2)
    assert not (panel.row_table.model().flags(pfc_pi) & Qt.ItemIsEditable)
    assert not panel.row_table.model().setData(pfc_pi, "99", Qt.EditRole)

    _select_rect(panel.row_table, 4, 2, 4, 2)
    assert panel.row_table.paste_tsv_at_selection("99\t2") == 1
    assert panel.row_table.model().cell_value(4, 2) == ""
    assert panel.row_table.model().cell_value(4, 3) == "2"


def test_fin_type_to_pfc_clears_pi_and_one_undo_restores_compound_change():
    panel = _panel()
    _select_group(panel, "odu_cond_specs")
    _select_rect(panel.row_table, 0, 1, 0, 1)

    assert panel.row_table.replace_current_cell("PFC")
    assert panel.row_table.model().cell_value(0, 1) == "PFC"
    assert panel.row_table.model().cell_value(0, 2) == ""
    assert panel.row_table.undo() == 1
    assert panel.row_table.model().cell_value(0, 1) == "F&T"
    assert panel.row_table.model().cell_value(0, 2) == "5"


def test_non_pfc_pi_and_dynamic_last_column_support_paste_clear_and_undo():
    panel = _panel(dynamic=True)
    fan = panel.row_table.model().columnCount() - 1
    assert panel.row_table.model().header_for_column(fan) == "Fan Diameter"
    _select_rect(panel.row_table, 0, fan, 0, fan)

    assert panel.row_table.paste_tsv_at_selection("12.5") == 1
    assert panel.row_table.model().cell_value(0, fan) == "12.5"
    assert panel.row_table.clear_selection() == 1
    assert panel.row_table.undo() == 1
    assert panel.row_table.model().cell_value(0, fan) == "12.5"
    assert panel.row_table.undo() == 1
    assert panel.row_table.model().cell_value(0, fan) == ""

    _select_group(panel, "odu_cond_specs")
    non_pfc_pi = panel.row_table.model().index(0, 2)
    assert panel.row_table.model().flags(non_pfc_pi) & Qt.ItemIsEditable


def test_add_duplicate_delete_each_have_service_owned_undo_and_selection():
    panel = _panel()
    initial = panel.row_table.model().rowCount()

    panel._add_row()
    assert panel.row_table.model().rowCount() == initial + 1
    assert panel.row_table.currentIndex().row() == initial
    assert panel.row_table.undo() == 1
    assert panel.row_table.model().rowCount() == initial

    panel._select_row(0)
    panel._duplicate_row()
    assert panel.row_table.model().rowCount() == initial + 1
    assert panel.row_table.currentIndex().row() == 1
    assert panel.row_table.undo() == 1

    panel._select_row(0)
    panel._delete_row()
    assert panel.row_table.model().rowCount() == initial - 1
    assert panel.row_table.currentIndex().row() == 0
    assert panel.row_table.undo() == 1
    assert panel.row_table.model().rowCount() == initial
