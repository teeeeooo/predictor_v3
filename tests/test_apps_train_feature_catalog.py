"""Train Feature Catalog viewer tests."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt

from apps.train.application.feature_catalog import FeatureCatalogService
from apps.train.controllers.feature_catalog_controller import FeatureCatalogController
from apps.train.ui.feature_catalog.table_model import FeatureCatalogTableModel
from core.ml.feature_catalog import DEFAULT_CATALOG_PATH, REQUIRED_HEADERS


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
    assert model.data(model.index(0, 10), Qt.DisplayRole) in {"true", "false"}
    assert not (model.flags(model.index(0, 0)) & Qt.ItemIsEditable)
    assert model.cell_value(-1, 0) == ""
