"""Train Feature Catalog viewer tests."""

from __future__ import annotations

from pathlib import Path
import os
import shutil

import pytest
from PySide6.QtCore import QItemSelectionModel, Qt
from PySide6.QtWidgets import QApplication, QMessageBox

from apps.train.adapters.feature_catalog import FeatureCatalogFileAdapter
from apps.train.application.feature_catalog import FeatureCatalogDraftRequest, FeatureCatalogService
from apps.train.controllers.feature_catalog_controller import FeatureCatalogController
from apps.train.ui.feature_catalog import FeatureCatalogPanel
from apps.train.ui.feature_catalog.help_dialog import HELP_TEXT, FeatureCatalogHelpDialog
from apps.train.ui.feature_catalog.row_dialog import FeatureCatalogRowDialog
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
    assert model.headerData(0, Qt.Horizontal, Qt.DisplayRole) == "순서"
    assert model.canonical_header(0) == "order"
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
    assert model.setData(model.index(0, label_col), snapshot.rows[0].value_at(label_col))
    assert not model.is_dirty
    assert not model.setData(model.index(0, ml_name_col), "Blocked", Qt.EditRole)

    assert model.setData(model.index(0, active_col), "yes", Qt.EditRole)
    assert model.is_invalid_cell(0, active_col)


def test_feature_catalog_table_model_exposes_dropdown_options():
    snapshot = FeatureCatalogService().load_snapshot()
    model = FeatureCatalogTableModel(snapshot)

    assert model.dropdown_options(0, REQUIRED_HEADERS.index("active")) == ("true", "false")
    assert "mode_missing_allowed" in model.dropdown_options(
        0, REQUIRED_HEADERS.index("zero_fill_policy")
    )
    assert "auto" in model.dropdown_options(0, REQUIRED_HEADERS.index("role"))
    assert "idu" in model.dropdown_options(0, REQUIRED_HEADERS.index("source"))
    assert "ID Volume" in model.dropdown_options(0, REQUIRED_HEADERS.index("mapping_key"))
    assert "refrigerant" in model.dropdown_options(
        0, REQUIRED_HEADERS.index("one_hot_group")
    )


def test_feature_catalog_service_builds_draft_record_with_generated_order_and_ui_key():
    service = FeatureCatalogService()
    snapshot = service.load_snapshot()
    request = FeatureCatalogDraftRequest(
        ml_name="New Feature",
        role="input",
        label="New Feature Label",
        zero_fill_policy="disallow",
    )

    record = service.build_draft_record(snapshot.rows, request)
    values = dict(zip(REQUIRED_HEADERS, record.values, strict=True))

    assert values["order"] == "290"
    assert values["ml_name"] == "New Feature"
    assert values["ui_key"] == "new_feature"
    assert values["active"] == "true"


def test_feature_catalog_service_generates_unique_ui_key_for_draft_record():
    service = FeatureCatalogService()
    snapshot = service.load_snapshot()
    request = FeatureCatalogDraftRequest(
        ml_name="Cooling Capa",
        role="input",
        label="Cooling Capa Copy",
    )

    record = service.build_draft_record(snapshot.rows, request)
    values = dict(zip(REQUIRED_HEADERS, record.values, strict=True))

    assert values["ui_key"] == "cooling_capa_2"


def test_feature_catalog_table_model_add_and_remove_rows_tracks_baseline_dirty():
    snapshot = FeatureCatalogService().load_snapshot()
    model = FeatureCatalogTableModel(snapshot)
    service = FeatureCatalogService()
    record = service.build_draft_record(
        model.records(),
        FeatureCatalogDraftRequest(
            ml_name="Draft Feature",
            role="input",
            label="Draft Feature",
        ),
    )
    original_count = model.rowCount()

    model.add_record(record)

    assert model.rowCount() == original_count + 1
    assert model.is_dirty
    assert model.remove_rows((original_count,)) == 1
    assert model.rowCount() == original_count
    assert not model.is_dirty


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


def test_feature_catalog_controller_exports_current_unsaved_records(tmp_path):
    _app()
    controller = FeatureCatalogController()
    state = controller.refresh()
    assert state.snapshot is not None
    model = FeatureCatalogTableModel(state.snapshot)
    label_col = REQUIRED_HEADERS.index("label")
    assert model.setData(model.index(0, label_col), "Pending Export Label", Qt.EditRole)

    export_state = controller.export_records(
        model.records(),
        state.snapshot,
        tmp_path / "export.csv",
    )

    assert export_state.result is not None
    assert export_state.status == "ready"
    assert "Pending Export Label" in (tmp_path / "export.csv").read_text(
        encoding="utf-8-sig"
    )


def test_feature_catalog_row_dialog_returns_draft_request():
    snapshot = FeatureCatalogService().load_snapshot()
    dialog = FeatureCatalogRowDialog(snapshot.field_options)
    dialog.ml_name.setText("Dialog Feature")
    dialog.label.setText("Dialog Label")
    dialog.role.setEditText("auto")
    dialog.source.setEditText("idu")
    dialog.mapping_key.setEditText("ID Volume")

    request = dialog.request()

    assert request.ml_name == "Dialog Feature"
    assert request.role == "auto"
    assert request.source == "idu"
    assert request.mapping_key == "ID Volume"


def test_feature_catalog_panel_delete_removes_selected_draft_row(monkeypatch):
    _app()
    panel = FeatureCatalogPanel()
    original_count = panel.table_model.rowCount()
    panel.table.selectRow(0)
    monkeypatch.setattr(
        QMessageBox,
        "question",
        lambda *args, **kwargs: QMessageBox.Yes,
    )

    panel._delete_selected_features()

    assert panel.table_model.rowCount() == original_count - 1
    assert panel.table_model.is_dirty
    assert panel.save_button.isEnabled()


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


def test_feature_catalog_help_dialog_contains_user_terms():
    _app()
    dialog = FeatureCatalogHelpDialog()

    assert "학습 데이터 컬럼명(ml_name)" in dialog.text.toPlainText()
    assert "one-hot" in dialog.text.toPlainText()
    assert HELP_TEXT in dialog.text.toPlainText()
