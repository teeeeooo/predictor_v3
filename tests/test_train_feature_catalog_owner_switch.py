"""Train Feature Catalog legacy compatibility surface tests."""

from __future__ import annotations

import os

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from apps.train.controllers.feature_catalog_controller import FeatureCatalogController
from apps.train.ui.feature_catalog import FeatureCatalogPanel
from core.ml.feature_catalog import REQUIRED_HEADERS


def _app() -> QApplication:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    return QApplication.instance() or QApplication([])


def test_feature_catalog_controller_marks_surface_legacy_compatibility():
    controller = FeatureCatalogController()

    state = controller.refresh()

    assert state.status == "ready"
    assert "legacy compatibility" in state.message
    assert "Data Definition is the canonical" in state.message


def test_feature_catalog_controller_blocks_default_save_as_legacy_surface():
    controller = FeatureCatalogController()
    state = controller.refresh()
    assert state.snapshot is not None

    save_state = controller.save_records(state.snapshot.rows)

    assert save_state.status == "error"
    assert save_state.result is not None
    assert not save_state.result.saved
    assert "Feature Catalog canonical save is disabled" in save_state.message


def test_feature_catalog_panel_shows_legacy_warning_and_save_block():
    app = _app()
    panel = FeatureCatalogPanel()
    try:
        app.processEvents()
        label_col = REQUIRED_HEADERS.index("label")

        assert "legacy compatibility" in panel.validation_value.text()
        assert panel.table_model.setData(
            panel.table_model.index(0, label_col),
            "Blocked Canonical Label",
            Qt.EditRole,
        )
        assert panel.save_button.isEnabled()

        panel._save_catalog()

        assert "Feature Catalog canonical save is disabled" in panel.validation_value.text()
        assert "Data Definition" in panel.messages.toPlainText()
    finally:
        panel.close()
        panel.deleteLater()
        app.processEvents()
