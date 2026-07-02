"""Train Feature Catalog viewer tests."""

from __future__ import annotations

from pathlib import Path
import os
import shutil

import pytest
from PySide6.QtCore import QItemSelectionModel, Qt
from PySide6.QtWidgets import QApplication

from apps.train.adapters.feature_catalog import FeatureCatalogFileAdapter
from apps.train.application.feature_catalog import FeatureCatalogService
from apps.train.controllers.feature_catalog_controller import FeatureCatalogController
from apps.train.ui.feature_catalog.table_model import FeatureCatalogTableModel
from apps.train.ui.feature_catalog.table_view import FeatureCatalogTableView
from core.ml.feature_catalog import DEFAULT_CATALOG_PATH, REQUIRED_HEADERS


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


def test_feature_catalog_service_loads_valid_default_catalog():
    service = FeatureCatalogService()

    snapshot = service.load_snapshot()

    assert snapshot.path == Path(DEFAULT_CATALOG_PATH)
    assert snapshot.headers == REQUIRED_HEADERS
    assert snapshot.row_count > 0
    assert snapshot.active_count > 0
    assert snapshot.catalog_validation.ok
    assert snapshot.project_validation is not None
    assert snapshot.project_validation.ok
    assert "Catalog validation: OK" in snapshot.validation_messages()


def test_feature_catalog_controller_returns_controlled_load_error(tmp_path):
    controller = FeatureCatalogController(
        service=FeatureCatalogService(tmp_path / "missing.csv")
    )

    state = controller.refresh()

    assert state.snapshot is None
    assert state.status == "error"
    assert "Feature Catalog load failed" in state.message


def test_feature_catalog_table_model_is_read_only():
    snapshot = FeatureCatalogService().load_snapshot()
    model = FeatureCatalogTableModel(snapshot)

    assert model.rowCount() == snapshot.row_count
    assert model.columnCount() == len(REQUIRED_HEADERS)
    assert model.headerData(0, Qt.Horizontal, Qt.DisplayRole) == "order"
    assert model.headerData(0, Qt.Vertical, Qt.DisplayRole) == 1
    assert model.data(model.index(0, 2), Qt.DisplayRole)
    assert model.data(model.index(0, REQUIRED_HEADERS.index("active")), Qt.DisplayRole) in {
        "true",
        "false",
    }
    assert not (model.flags(model.index(0, 0)) & Qt.ItemIsEditable)
    assert model.cell_value(-1, 0) == ""


def test_feature_catalog_table_model_editability_and_dirty_state():
    snapshot = FeatureCatalogService().load_snapshot()
    model = FeatureCatalogTableModel(snapshot)
    label_col = REQUIRED_HEADERS.index("label")
    ml_name_col = REQUIRED_HEADERS.index("ml_name")
    active_col = REQUIRED_HEADERS.index("active")

    assert model.flags(model.index(0, label_col)) & Qt.ItemIsEditable
    assert not (model.flags(model.index(0, ml_name_col)) & Qt.ItemIsEditable)
    assert model.setData(model.index(0, label_col), "Edited Label", Qt.EditRole)
    assert model.is_dirty
    assert model.cell_value(0, label_col) == "Edited Label"
    assert not model.setData(model.index(0, ml_name_col), "Blocked", Qt.EditRole)

    assert model.setData(model.index(0, active_col), "yes", Qt.EditRole)
    assert model.is_invalid_cell(0, active_col)


def test_feature_catalog_table_view_copy_paste_clear_and_undo():
    _app()
    snapshot = FeatureCatalogService().load_snapshot()
    model = FeatureCatalogTableModel(snapshot)
    view = FeatureCatalogTableView()
    view.setModel(model)
    label_col = REQUIRED_HEADERS.index("label")
    index = model.index(0, label_col)
    view.selectionModel().setCurrentIndex(index, QItemSelectionModel.ClearAndSelect)

    assert view.paste_tsv_at_selection("Edited Label") == 1
    assert model.cell_value(0, label_col) == "Edited Label"
    assert view.copy_selection_tsv() == "Edited Label\n"
    assert view.clear_selection() == 1
    assert model.cell_value(0, label_col) == ""
    assert view.undo() == 1
    assert model.cell_value(0, label_col) == "Edited Label"
    assert view.undo() == 1
    assert model.cell_value(0, label_col) == snapshot.rows[0].value_at(label_col)


def test_feature_catalog_export_writes_excel_safe_csv(tmp_path):
    service = FeatureCatalogService(export_writer=FeatureCatalogFileAdapter())
    snapshot = service.load_snapshot()
    export_path = tmp_path / "feature_catalog.csv"

    result = service.export_snapshot(snapshot, export_path)

    assert result.path == export_path
    assert result.row_count == snapshot.row_count
    assert result.validation_status == "ok"
    assert export_path.read_bytes().startswith(b"\xef\xbb\xbf")
    lines = export_path.read_text(encoding="utf-8-sig").splitlines()
    assert lines[0] == ",".join(REQUIRED_HEADERS)


def test_feature_catalog_controller_reports_export_result(tmp_path):
    controller = FeatureCatalogController()
    state = controller.refresh()
    assert state.snapshot is not None

    export_state = controller.export_csv(state.snapshot, tmp_path / "export.csv")

    assert export_state.result is not None
    assert export_state.status == "ready"
    assert "validation OK" in export_state.message


def test_feature_catalog_controller_returns_controlled_export_error(tmp_path):
    controller = FeatureCatalogController()
    state = controller.refresh()
    assert state.snapshot is not None

    export_state = controller.export_csv(state.snapshot, tmp_path)

    assert export_state.result is None
    assert export_state.status == "error"
    assert "Feature Catalog export failed" in export_state.message


def test_feature_catalog_save_persists_valid_edit_without_bom(tmp_path):
    catalog_path = tmp_path / "features.csv"
    shutil.copyfile(DEFAULT_CATALOG_PATH, catalog_path)
    service = FeatureCatalogService(
        catalog_path=catalog_path,
        export_writer=FeatureCatalogFileAdapter(),
    )
    snapshot = service.load_snapshot()
    label_col = REQUIRED_HEADERS.index("label")
    rows = [list(record.values) for record in snapshot.rows]
    rows[0][label_col] = "Edited Label"
    records = tuple(type(snapshot.rows[0])(values=tuple(row)) for row in rows)

    result = service.save_records(records)

    assert result.saved
    assert result.snapshot is not None
    assert result.snapshot.rows[0].value_at(label_col) == "Edited Label"
    assert not catalog_path.read_bytes().startswith(b"\xef\xbb\xbf")


def test_feature_catalog_save_blocks_invalid_active_and_preserves_file(tmp_path):
    catalog_path = tmp_path / "features.csv"
    shutil.copyfile(DEFAULT_CATALOG_PATH, catalog_path)
    original = catalog_path.read_bytes()
    service = FeatureCatalogService(
        catalog_path=catalog_path,
        export_writer=FeatureCatalogFileAdapter(),
    )
    snapshot = service.load_snapshot()
    active_col = REQUIRED_HEADERS.index("active")
    rows = [list(record.values) for record in snapshot.rows]
    rows[0][active_col] = "yes"
    records = tuple(type(snapshot.rows[0])(values=tuple(row)) for row in rows)

    result = service.save_records(records)

    assert not result.saved
    assert any("invalid active 'yes'" in error for error in result.errors)
    assert catalog_path.read_bytes() == original


def test_feature_catalog_controller_returns_controlled_save_error(tmp_path):
    service = FeatureCatalogService(tmp_path / "missing-writer.csv")
    controller = FeatureCatalogController(service=service)

    save_state = controller.save_records(())

    assert save_state.result is None
    assert save_state.status == "error"
    assert "Feature Catalog save failed" in save_state.message
