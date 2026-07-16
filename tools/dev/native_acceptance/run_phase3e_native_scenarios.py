"""Capture Phase 3 Slice 3E native macOS states with synthetic providers."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
from pathlib import Path

from PySide6.QtCore import QEventLoop, QTimer
from PySide6.QtWidgets import QApplication, QMainWindow, QTabWidget

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from apps.common.ui import style  # noqa: E402
from apps.train.controllers.data_definition_controller import (  # noqa: E402
    DataDefinitionController,
)
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
    parser.add_argument("--hold-seconds", type=int, default=0)
    args = parser.parse_args()
    app = QApplication.instance() or QApplication([])
    if app.platformName() != "cocoa":
        raise RuntimeError(
            f"Native evidence requires the cocoa platform, got {app.platformName()!r}."
        )
    args.output.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="predictor-v3-phase3e-") as temp_dir:
        temp = Path(temp_dir)
        schema_path = temp / "schema.csv"
        mapping_path = temp / "mapping.json"
        shutil.copyfile(DEFAULT_SCHEMA_PATH, schema_path)
        shutil.copyfile(RUNTIME_MAPPING_FIXTURE, mapping_path)

        definition_controller = DataDefinitionController(
            DataDefinitionService(schema_path=schema_path)
        )
        mapping_controller = DataMappingController(DataMappingService(
            RuntimeMappingCatalogProvider(str(mapping_path)),
            DataDefinitionMappingRequirementProvider(schema_path),
        ))
        window = QMainWindow()
        window.setObjectName("Phase3ESyntheticNativeAcceptance")
        window.setWindowTitle("Phase 3E Native Acceptance — Synthetic Data")
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
        window.raise_()
        window.activateWindow()
        _settle(app)

        captures: list[dict[str, object]] = []
        _capture(window, args.output, "01-clean-definition-normal.png", captures)

        definition_panel._apply_edit_intent(EditDefinitionIntent(
            ("schema_row", "idu"),
            (("label", "Indoor Unit — Native Review"),),
        ))
        _settle(app)
        _capture(window, args.output, "02-dirty-saveable-impact.png", captures)

        definition_panel._reset_draft()
        definition_panel._apply_edit_intent(EditDefinitionIntent(
            ("schema_row", "cooling_capa"),
            (("ml_name", "Cooling Capacity Native Blocked"),),
        ))
        _settle(app)
        _capture(window, args.output, "03-blocked-compatibility.png", captures)

        definition_panel._reset_draft()
        accepted, message = definition_panel._apply_add_intent(AddDefinitionIntent(
            "mapping_attribute",
            "Native Keyboard Attribute",
            "native_keyboard_attribute",
            "number",
            required=True,
            mapping_entity="idu",
            mapping_attribute="Native Keyboard Attribute",
            trigger_column="idu",
            notes="Synthetic Phase 3E native acceptance",
        ))
        if not accepted:
            raise RuntimeError(message)
        definition_panel._save_schema()
        _settle(app)
        _capture(window, args.output, "04-saved-mapping-handoff.png", captures)

        definition_panel.handoff_panel.selector.setCurrentIndex(0)
        definition_panel.handoff_panel._open()
        _settle(app)
        _capture(window, args.output, "05-data-mapping-exact-coverage.png", captures)

        tabs.setCurrentWidget(definition_panel)
        window.resize(*COMPACT_SIZE)
        _settle(app)
        _capture(window, args.output, "06-definition-compact.png", captures)

        definition_panel.search_input.setText("no-native-definition-matches")
        _settle(app)
        _capture(window, args.output, "07-no-match-recovery.png", captures)

        print(json.dumps({
            "platform": app.platformName(),
            "runtime_fixture_changed": False,
            "schema_fixture_changed": False,
            "captures": captures,
        }, indent=2))
        if args.hold_seconds > 0:
            _settle(app, args.hold_seconds * 1000)
        window.close()
        _settle(app, 20)
    return 0


def _settle(app: QApplication, milliseconds: int = 120) -> None:
    loop = QEventLoop()
    QTimer.singleShot(milliseconds, loop.quit)
    loop.exec()
    app.processEvents()


def _capture(
    window: QMainWindow,
    output: Path,
    name: str,
    captures: list[dict[str, object]],
) -> None:
    screen = window.screen()
    if screen is None or not window.isVisible():
        raise RuntimeError("Native window is not visible on a screen.")
    pixmap = screen.grabWindow(int(window.winId()))
    capture_method = "QScreen.grabWindow"
    if pixmap.isNull():
        pixmap = window.grab()
        capture_method = "visible QWidget.grab native backing store"
    if pixmap.isNull() or not pixmap.save(str(output / name), "PNG"):
        raise RuntimeError(f"Unable to save native screenshot: {name}")
    captures.append({
        "file": name,
        "logical_window_size": [window.width(), window.height()],
        "capture_size": [pixmap.width(), pixmap.height()],
        "device_pixel_ratio": pixmap.devicePixelRatio(),
        "capture_method": capture_method,
    })


if __name__ == "__main__":
    raise SystemExit(main())
