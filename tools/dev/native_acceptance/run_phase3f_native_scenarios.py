"""Capture Slice 3F table-first correction states with synthetic providers."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from PySide6.QtCore import QEventLoop, QPoint, Qt, QTimer
from PySide6.QtGui import QPainter, QPixmap
from PySide6.QtWidgets import QApplication, QHeaderView, QMainWindow, QSplitter, QTabWidget

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
from apps.train.ui.data_definition_details_dialog import DataDefinitionDetailsDialog  # noqa: E402
from apps.train.ui.data_definition_panel import DataDefinitionPanel  # noqa: E402
from apps.train.ui.data_mapping_panel import DataMappingPanel  # noqa: E402
from core.data_definition import AddDefinitionIntent, EditDefinitionIntent  # noqa: E402
from core.predictor_schema.catalog_v2 import DEFAULT_SCHEMA_PATH  # noqa: E402

RUNTIME_MAPPING_FIXTURE = ROOT / "tests/fixtures/mapping/mapping_runtime_equivalent.json"
NORMAL_SIZE = (1280, 820)
COMPACT_SIZE = (900, 640)
CORRECTION_EVIDENCE_NOTE = (
    "Earlier Slice 3F evidence remains historical and is superseded for the "
    "default composition by this table-first correction."
)


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
        window.setWindowTitle("Phase 3F Table-first Definition Manager — Synthetic Data")
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
        window.activateWindow()
        _settle(app)

        captures: list[dict[str, object]] = []
        _assert_default_layout(definition_panel, compact=False)
        _capture(
            window,
            args.output,
            "01-clean-table-first-normal.png",
            "clean normal table-first workspace",
            "Loaded the synthetic schema and selected the canonical first inventory row.",
            captures,
        )
        _capture_details_dialog(definition_panel, app, args.output, captures)

        definition_panel._apply_edit_intent(EditDefinitionIntent(
            ("schema_row", "idu"),
            (("label", "Indoor Unit — Native Review"),),
        ))
        _settle(app)
        _capture(
            window,
            args.output,
            "03-dirty-saveable-banner.png",
            "dirty saveable conditional surface",
            "Applied one supported controlled Edit command; Review changes remained conditional.",
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
            "04-blocked-save-banner.png",
            "blocked conditional surface",
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
            notes="Synthetic Phase 3F table-first native acceptance",
        ))
        if not accepted:
            raise RuntimeError(message)
        definition_panel._save_schema()
        _settle(app)
        _assert_single_saved_handoff(definition_panel)
        _capture(
            window,
            args.output,
            "05-saved-mapping-next-step.png",
            "single saved Mapping Requirement next-step conditional surface",
            (
                "Saved one Mapping Requirement to the temporary schema copy; the direct "
                "next step showed no selector and retained the table-first Inventory."
            ),
            captures,
        )

        definition_panel._reset_draft()
        window.resize(*COMPACT_SIZE)
        _settle(app)
        _assert_default_layout(definition_panel, compact=True)
        _capture(
            window,
            args.output,
            "06-clean-table-first-compact.png",
            "clean compact table-first workspace",
            "Reset the draft, resized to 900x640, and kept diagnostics collapsed.",
            captures,
        )

        manifest = {
            "commit_sha": _git_sha(),
            "native_onscreen": window.isVisible(),
            "capture_source": "visible cocoa window and QDialog native backing-store capture",
            "fixture_provider": (
                "repository synthetic schema/mapping fixtures copied to a temporary "
                "provider; canonical and runtime fixtures are read-only"
            ),
            "programmatic_interaction": True,
            "computer_use_interaction": False,
            "physical_interaction": False,
            "actual_interaction": "programmatic Qt public panel/controller actions",
            "protected_runtime_fixture_changed": (
                RUNTIME_MAPPING_FIXTURE.read_bytes() != runtime_fixture_before
            ),
            "protected_schema_fixture_changed": (
                DEFAULT_SCHEMA_PATH.read_bytes() != schema_fixture_before
            ),
            "known_accessibility_table_path_used": False,
            "superseded_historical_evidence": CORRECTION_EVIDENCE_NOTE,
            "captures": captures,
        }
        (args.output / "native_manifest.json").write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(json.dumps(manifest, indent=2, ensure_ascii=False))
        window.close()
        _settle(app, 20)
    return 0


def _assert_default_layout(panel: DataDefinitionPanel, *, compact: bool) -> None:
    if panel.findChildren(QSplitter):
        raise RuntimeError("Data Definition still contains a splitter")
    if panel.inventory_table.horizontalScrollBar().maximum() != 0:
        raise RuntimeError("Definition Inventory requires horizontal scrolling")
    header = panel.inventory_table.horizontalHeader()
    if header.stretchLastSection():
        raise RuntimeError("Definition Inventory last-section stretch is enabled")
    model = panel.inventory_table.model()
    expected = {0, 1, 2, 3, 4, 7} if compact else set(range(model.columnCount()))
    visible = {
        column
        for column in range(model.columnCount())
        if not panel.inventory_table.isColumnHidden(column)
    }
    if visible != expected:
        raise RuntimeError(f"Unexpected Inventory columns: {visible!r}")
    if any(
        header.sectionResizeMode(column) != QHeaderView.Interactive
        for column in visible
    ):
        raise RuntimeError("Inventory uses an unbounded column resize mode")
    if panel.inventory_view.height() <= panel.height() // 2:
        raise RuntimeError("Inventory is not the primary vertical stretch owner")
    if hasattr(panel, "summary_card"):
        raise RuntimeError("Selected Definition Summary Card remains in production path")
    if not panel.impact_view.isHidden():
        raise RuntimeError("Conditional impact surface is visible in clean state")
    if not panel.handoff_panel.isHidden():
        raise RuntimeError("Saved handoff surface is visible before a saved requirement")
    if not panel.diagnostics.tabs.isHidden():
        raise RuntimeError("Advanced Diagnostics is expanded in the default workspace")


def _assert_single_saved_handoff(panel: DataDefinitionPanel) -> None:
    requests = panel._state.saved_mapping_handoffs
    if len(requests) != 1:
        raise RuntimeError(f"Expected one saved Mapping Requirement, got {len(requests)}")
    if panel.handoff_panel.isHidden():
        raise RuntimeError("Single saved Mapping Requirement handoff is hidden")
    if not panel.handoff_panel.selector.isHidden():
        raise RuntimeError("Single saved Mapping Requirement still shows a selector")
    if not panel.handoff_panel.open_button.isEnabled():
        raise RuntimeError("Single saved Mapping Requirement action is disabled")
    detail = panel.handoff_panel.detail.text()
    for expected in ("Cond Inner Area", "odu_cond_specs", "Required"):
        if expected not in detail:
            raise RuntimeError(f"Single saved handoff detail is missing {expected!r}")
    if panel.inventory_view.height() <= panel.height() // 2:
        raise RuntimeError("Inventory lost primary vertical ownership in saved handoff state")


def _capture_details_dialog(
    panel: DataDefinitionPanel,
    app: QApplication,
    output: Path,
    captures: list[dict[str, object]],
) -> None:
    errors: list[str] = []

    def inspect() -> None:
        dialog = app.activeModalWidget()
        try:
            if not isinstance(dialog, DataDefinitionDetailsDialog):
                raise RuntimeError("Details action did not open the read-only modal")
            dialog.technical_toggle.click()
            app.processEvents()
            _capture_widget(
                dialog,
                output,
                "02-details-modal-technical-expanded.png",
                "on-demand read-only Details modal",
                "Opened Details from the selected row, expanded Technical details, then closed.",
                captures,
            )
        except Exception as error:  # pragma: no cover - native runner failure path
            errors.append(str(error))
        finally:
            if dialog is not None and dialog.isVisible():
                dialog.reject()

    QTimer.singleShot(0, inspect)
    panel.details_action.trigger()
    _settle(app)
    if errors:
        raise RuntimeError(errors[0])


def _settle(app: QApplication, milliseconds: int = 140) -> None:
    loop = QEventLoop()
    QTimer.singleShot(milliseconds, loop.quit)
    loop.exec()
    app.processEvents()


def _capture(
    widget: QMainWindow,
    output: Path,
    name: str,
    state: str,
    actual_interaction: str,
    captures: list[dict[str, object]],
) -> None:
    _capture_widget(widget, output, name, state, actual_interaction, captures)


def _capture_widget(
    widget,
    output: Path,
    name: str,
    state: str,
    actual_interaction: str,
    captures: list[dict[str, object]],
) -> None:  # noqa: ANN001
    screen = widget.screen()
    if screen is None or not widget.isVisible():
        raise RuntimeError(f"Visible native widget is unavailable for {name}.")
    pixmap = screen.grabWindow(int(widget.winId()))
    capture_method = "QScreen.grabWindow"
    if pixmap.isNull():
        ratio = widget.devicePixelRatioF()
        pixmap = QPixmap(round(widget.width() * ratio), round(widget.height() * ratio))
        pixmap.setDevicePixelRatio(ratio)
        pixmap.fill(Qt.white)
        painter = QPainter(pixmap)
        widget.render(painter, QPoint())
        painter.end()
        capture_method = "visible QWidget.render target capture"
    if pixmap.isNull() or not pixmap.save(str(output / name), "PNG"):
        raise RuntimeError(f"Unable to save native screenshot: {name}")
    captures.append({
        "file": name,
        "state": state,
        "logical_size": [widget.width(), widget.height()],
        "pixel_size": [pixmap.width(), pixmap.height()],
        "device_pixel_ratio": pixmap.devicePixelRatio(),
        "capture_source": capture_method,
        "actual_interaction": actual_interaction,
    })


def _git_sha() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


if __name__ == "__main__":
    raise SystemExit(main())
