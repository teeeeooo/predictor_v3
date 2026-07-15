"""Capture Phase 3 Slice 3F native macOS states with synthetic providers."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
from pathlib import Path

from PySide6.QtCore import QEventLoop, QPoint, Qt, QTimer
from PySide6.QtGui import QPainter, QPixmap
from PySide6.QtWidgets import QApplication, QMainWindow, QSplitter, QTabWidget

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from apps.common.ui import style  # noqa: E402
from apps.train.controllers.data_definition_controller import DataDefinitionController  # noqa: E402
from apps.train.controllers.data_mapping_controller import DataMappingController  # noqa: E402
from apps.train.services.data_definition_service import DataDefinitionService  # noqa: E402
from apps.train.services.data_mapping_service import (  # noqa: E402
    DataDefinitionMappingRequirementProvider,
    DataMappingService,
    RuntimeMappingCatalogProvider,
)
from apps.train.ui.data_definition_panel import DataDefinitionPanel  # noqa: E402
from apps.train.ui.data_mapping_panel import DataMappingPanel  # noqa: E402
from core.data_definition import AddDefinitionIntent, EditDefinitionIntent  # noqa: E402
from core.predictor_schema.catalog_v2 import DEFAULT_SCHEMA_PATH  # noqa: E402

RUNTIME_MAPPING_FIXTURE = ROOT / "tests/fixtures/mapping/mapping_runtime_equivalent.json"
NORMAL_SIZE = (1280, 820)
COMPACT_SIZE = (900, 640)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    app = QApplication.instance() or QApplication([])
    if app.platformName() != "cocoa":
        raise RuntimeError(
            f"Native evidence requires the cocoa platform, got {app.platformName()!r}."
        )
    args.output.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="predictor-v3-phase3f-") as temp_dir:
        temp = Path(temp_dir)
        schema_path = temp / "schema.csv"
        mapping_path = temp / "mapping.json"
        shutil.copyfile(DEFAULT_SCHEMA_PATH, schema_path)
        shutil.copyfile(RUNTIME_MAPPING_FIXTURE, mapping_path)
        schema_fixture_before = DEFAULT_SCHEMA_PATH.read_bytes()
        runtime_fixture_before = RUNTIME_MAPPING_FIXTURE.read_bytes()

        definition_controller = DataDefinitionController(
            DataDefinitionService(schema_path=schema_path)
        )
        mapping_controller = DataMappingController(DataMappingService(
            RuntimeMappingCatalogProvider(str(mapping_path)),
            DataDefinitionMappingRequirementProvider(schema_path),
        ))
        window = QMainWindow()
        window.setWindowTitle("Phase 3F Definition Workspace — Synthetic Data")
        window.setStyleSheet(style.app_stylesheet())
        tabs = QTabWidget(window)
        mapping_panel = DataMappingPanel(tabs, controller=mapping_controller)

        def open_mapping(request):  # noqa: ANN001, ANN202
            tabs.setCurrentWidget(mapping_panel)
            return mapping_panel.open_requirement(request)

        definition_panel = DataDefinitionPanel(
            tabs,
            controller=definition_controller,
            on_open_data_mapping=open_mapping,
        )
        tabs.addTab(definition_panel, "Data Definition")
        tabs.addTab(mapping_panel, "Data Mapping")
        tabs.setCurrentWidget(definition_panel)
        window.setCentralWidget(tabs)
        window.resize(*NORMAL_SIZE)
        window.show()
        _settle(app)
        captures: list[dict[str, object]] = []
        _assert_default_layout(definition_panel)
        _capture(
            window,
            args.output,
            "01-clean-full-width-inventory-summary.png",
            "clean full-width Inventory and Selected Summary",
            "Loaded the synthetic schema and selected the canonical first definition.",
            captures,
        )
        definition_panel._apply_edit_intent(EditDefinitionIntent(
            ("schema_row", "idu"),
            (("label", "Indoor Unit — Native Review"),),
        ))
        _settle(app)
        _capture(
            window,
            args.output,
            "02-dirty-saveable-concise-state.png",
            "dirty saveable concise change state",
            "Applied one supported controlled Edit command; did not expand detailed impact.",
            captures,
        )
        definition_panel._reset_draft()
        definition_panel._apply_edit_intent(EditDefinitionIntent(
            ("schema_row", "cooling_capa"),
            (("ml_name", "Cooling Capacity Native Blocked"),),
        ))
        _settle(app)
        _capture(
            window,
            args.output,
            "03-blocked-actionable-state.png",
            "blocked actionable state",
            "Applied a controlled compatibility-impacting Edit; Save remained disabled.",
            captures,
        )
        definition_panel._reset_draft()
        accepted, message = definition_panel._apply_add_intent(AddDefinitionIntent(
            "mapping_attribute",
            "Cond Inner Area",
            "cond_inner_area",
            "number",
            required=True,
            mapping_entity="cond_specs",
            mapping_attribute="Cond Inner Area",
            trigger_column="odu",
            rule_id="cond_specs_lookup",
            notes="Synthetic Phase 3F native acceptance",
        ))
        if not accepted:
            raise RuntimeError(message)
        definition_panel._save_schema()
        _settle(app)
        definition_panel.content_scroll.verticalScrollBar().setValue(
            definition_panel.content_scroll.verticalScrollBar().maximum()
        )
        _settle(app)
        _capture(
            window,
            args.output,
            "04-saved-mapping-next-step.png",
            "saved Mapping next-step state",
            "Executed the guarded schema Save against the temporary schema copy.",
            captures,
        )
        definition_panel._reset_draft()
        definition_panel.content_scroll.verticalScrollBar().setValue(0)
        window.resize(*COMPACT_SIZE)
        _settle(app)
        _assert_default_layout(definition_panel)
        _capture(
            window,
            args.output,
            "05-compact-task-workspace.png",
            "compact task-oriented workspace",
            "Reset draft, resized to 900x640, and kept diagnostics collapsed.",
            captures,
        )

        print(json.dumps({
            "platform": app.platformName(),
            "native_onscreen": window.isVisible(),
            "fixture_provider": "repository synthetic fixtures with temporary schema/mapping copies",
            "state_preparation": "programmatic Qt public panel/controller calls",
            "interaction_kind": "programmatic",
            "computer_use_actions": (
                "attempted list_apps only; macOS was locked, so no app state, "
                "Qt table hierarchy, or click was used"
            ),
            "physical_interaction": False,
            "known_accessibility_table_path_used": False,
            "runtime_fixture_changed": (
                RUNTIME_MAPPING_FIXTURE.read_bytes() != runtime_fixture_before
            ),
            "schema_fixture_changed": DEFAULT_SCHEMA_PATH.read_bytes() != schema_fixture_before,
            "captures": captures,
        }, indent=2))
        window.close()
        _settle(app, 20)
    return 0


def _assert_default_layout(panel: DataDefinitionPanel) -> None:
    if panel.findChildren(QSplitter):
        raise RuntimeError("Data Definition still contains a splitter")
    if panel.inventory_table.horizontalScrollBar().maximum() != 0:
        raise RuntimeError("Definition Inventory requires horizontal scrolling")
    if panel.inventory_table.horizontalHeader().stretchLastSection():
        raise RuntimeError("Definition Inventory last-section stretch is enabled")
    if not panel.impact_view.details_container.isHidden():
        raise RuntimeError("Detailed impact is expanded in the default workspace")
    if not panel.diagnostics.tabs.isHidden():
        raise RuntimeError("Advanced Diagnostics is expanded in the default workspace")


def _settle(app: QApplication, milliseconds: int = 140) -> None:
    loop = QEventLoop()
    QTimer.singleShot(milliseconds, loop.quit)
    loop.exec()
    app.processEvents()


def _capture(
    window: QMainWindow,
    output: Path,
    name: str,
    state: str,
    actual_interaction: str,
    captures: list[dict[str, object]],
) -> None:
    screen = window.screen()
    if screen is None or not window.isVisible():
        raise RuntimeError("Native window is not visible on a screen.")
    pixmap = screen.grabWindow(int(window.winId()))
    capture_method = "QScreen.grabWindow"
    if pixmap.isNull():
        ratio = window.devicePixelRatioF()
        pixmap = QPixmap(
            round(window.width() * ratio),
            round(window.height() * ratio),
        )
        pixmap.setDevicePixelRatio(ratio)
        pixmap.fill(Qt.white)
        painter = QPainter(pixmap)
        window.render(painter, QPoint())
        painter.end()
        capture_method = "visible QWidget.render target capture"
    if pixmap.isNull() or not pixmap.save(str(output / name), "PNG"):
        raise RuntimeError(f"Unable to save native screenshot: {name}")
    captures.append({
        "file": name,
        "state": state,
        "logical_window_size": [window.width(), window.height()],
        "capture_size": [pixmap.width(), pixmap.height()],
        "device_pixel_ratio": pixmap.devicePixelRatio(),
        "capture_method": capture_method,
        "actual_interaction": actual_interaction,
    })


if __name__ == "__main__":
    raise SystemExit(main())
