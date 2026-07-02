"""Train shell visual foundation tests."""

import os
from pathlib import Path

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QProgressBar,
    QPushButton,
    QTableView,
    QTextEdit,
)

from apps.predict.ui.shell import PredictShell
from apps.predict.ui.workspace import PredictWorkspace
from apps.train.state.training_run_state import (
    TrainingLogEvent,
    TrainingProgress,
    TrainingResourceStatus,
    TrainingResult,
)
from apps.train.ui.data_mapping_panel import DataMappingPanel
from apps.train.ui.feature_catalog import FeatureCatalogPanel
from apps.train.ui.shell import TrainShell
from apps.train.ui.train_model_panel import TrainModelPanel


def _app() -> QApplication:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    return QApplication.instance() or QApplication([])


class FakeTrainController:
    def __init__(self, *, finish_immediately: bool = True) -> None:
        self.is_running = False
        self.finish_immediately = finish_immediately
        self.started_request = None
        self.cancel_called = False
        self.last_result = None

    def resource_status(self, data_path=None, model_output_path=None):  # noqa: ANN001
        return TrainingResourceStatus(
            data_path=str(data_path or ""),
            model_path=str(model_output_path or ""),
            data_status="exists",
            model_status="missing",
        )

    def start(
        self,
        request,
        *,
        status_callback=None,
        log_callback=None,
        progress_callback=None,
        finished_callback=None,
        failed_callback=None,
        cancelled_callback=None,
    ):
        self.started_request = request
        self.is_running = True
        if status_callback is not None:
            status_callback("fake training")
        if log_callback is not None:
            log_callback(TrainingLogEvent(request.run_id, "fake log"))
        if progress_callback is not None:
            progress_callback(
                TrainingProgress(
                    request.run_id,
                    completed=1,
                    total=3,
                    message="fake progress",
                    indeterminate=False,
                )
            )
        if not self.finish_immediately:
            return None
        self.is_running = False
        result = TrainingResult(
            run_id=request.run_id,
            status="complete",
            summary="fake summary",
            model_path=request.model_output_path,
            message="fake complete",
        )
        self.last_result = result
        if finished_callback is not None:
            finished_callback(result)
        return None

    def cancel(self) -> bool:
        self.cancel_called = True
        self.is_running = False
        return True


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


def test_train_shell_tabs_and_predict_workspace_reuse():
    _app()
    shell = TrainShell()

    assert shell.tabs.count() == 4
    assert [shell.tabs.tabText(index) for index in range(3)] == [
        "Predict",
        "Train / Model",
        "Data Mapping",
    ]
    assert shell.tabs.tabText(3) == "Feature Catalog"
    assert isinstance(shell.tabs.widget(0), PredictWorkspace)
    assert isinstance(shell.tabs.widget(3), FeatureCatalogPanel)


def test_predict_shell_keeps_standalone_title_and_status_strip():
    _app()
    shell = PredictShell()
    workspace = shell.workspace

    assert workspace.findChild(QLabel, "PredictWorkspaceTitle") is not None
    assert workspace.status_strip.parent() is workspace


def test_train_embedded_predict_workspace_hides_duplicate_title_and_status_strip():
    _app()
    shell = TrainShell()
    workspace = shell.tabs.widget(0)

    assert isinstance(workspace, PredictWorkspace)
    assert workspace.findChild(QLabel, "PredictWorkspaceTitle") is None
    assert workspace.status_strip.parent() is None


def test_train_model_panel_initial_state_with_and_without_data(tmp_path):
    _app()
    panel = TrainModelPanel(controller=FakeTrainController())

    assert panel.objectName() == "TrainModelPanel"
    log = panel.findChild(QTextEdit, "TrainingLog")
    assert log is not None
    assert panel.findChild(QProgressBar) is not None
    table = panel.findChild(QTableView)
    assert table is not None
    assert table.model().rowCount() == 5
    assert table.model().headerData(1, Qt.Horizontal, Qt.DisplayRole) == "Target"

    buttons = {button.text(): button for button in panel.findChildren(QPushButton)}
    panel.set_data_path(str(tmp_path / "missing.csv"))
    assert buttons["학습 데이터 선택"].isEnabled()
    assert not buttons["학습 실행"].isEnabled()
    assert not buttons["중지"].isEnabled()

    data_path = tmp_path / "train.csv"
    data_path.write_text("x\n1\n", encoding="utf-8")
    panel.set_data_path(str(data_path))
    assert buttons["학습 실행"].isEnabled()
    assert not buttons["모델 열기"].isEnabled()
    assert not buttons["로그 저장"].isEnabled()


def test_train_model_panel_start_updates_progress_log_and_summary(tmp_path):
    _app()
    controller = FakeTrainController()
    panel = TrainModelPanel(controller=controller)
    data_path = tmp_path / "train.csv"
    data_path.write_text("x\n1\n", encoding="utf-8")
    panel.set_data_path(str(data_path))

    panel.run_button.click()

    assert controller.started_request is not None
    assert controller.started_request.data_path == str(data_path)
    assert "fake log" in panel.log.toPlainText()
    assert "fake summary" in panel.log.toPlainText()
    assert panel.progress_bar.value() == 100
    model = panel.summary_table.model()
    assert model.data(model.index(0, 2)) == "완료"


def test_train_model_panel_cancel_button_calls_controller(tmp_path):
    _app()
    controller = FakeTrainController(finish_immediately=False)
    panel = TrainModelPanel(controller=controller)
    data_path = tmp_path / "train.csv"
    data_path.write_text("x\n1\n", encoding="utf-8")
    panel.set_data_path(str(data_path))

    panel.run_button.click()
    assert panel.cancel_button.isEnabled()
    panel.cancel_button.click()

    assert controller.cancel_called


def test_data_mapping_panel_is_visual_only_with_log_area():
    _app()
    panel = DataMappingPanel()

    assert panel.objectName() == "DataMappingPanel"
    log = panel.findChild(QTextEdit, "MappingLog")
    assert log is not None
    assert "deferred" in log.toPlainText()
    table = panel.findChild(QTableView)
    assert table is not None
    assert table.model().rowCount() == 3
    assert table.model().data(table.model().index(1, 1)) == "deferred"
    assert (
        table.model().data(table.model().index(2, 2))
        == "DropdownOptionAdapter / core mapping owner"
    )
    assert "DropdownOptionAdapter" in log.toPlainText()

    buttons = {button.text(): button for button in panel.findChildren(QPushButton)}
    for text in ("매핑 Excel 선택", "매핑 업데이트", "상태 새로고침"):
        assert not buttons[text].isEnabled()


def test_feature_catalog_panel_loads_readonly_catalog():
    _app()
    panel = FeatureCatalogPanel()

    assert panel.objectName() == "FeatureCatalogPanel"
    assert panel.table.model().rowCount() > 0
    assert panel.table.model().columnCount() == 12
    assert panel.table.model().headerData(2, Qt.Horizontal, Qt.DisplayRole) == "ml_name"
    assert "validation OK" in panel.validation_value.text()
    assert "Catalog validation: OK" in panel.messages.toPlainText()
    assert panel.export_button.isEnabled()
    assert panel.export_value.text() == "No export yet"


def test_train_ui_widgets_do_not_import_core_execution_foundations():
    sources = (
        Path("apps/train/ui/shell.py"),
        Path("apps/train/ui/train_model_panel.py"),
        Path("apps/train/ui/data_mapping_panel.py"),
        Path("apps/train/ui/feature_catalog/panel.py"),
        Path("apps/train/ui/feature_catalog/table_model.py"),
    )
    forbidden = (
        "from core.training",
        "from apps.train.services",
        "import optuna",
        "import sklearn",
        "import subprocess",
        ".fit(",
        "load_workbook",
    )

    for source in sources:
        text = source.read_text(encoding="utf-8")
        assert not any(token in text for token in forbidden)


def test_train_ui_uses_model_views_not_qtablewidget():
    sources = (
        Path("apps/train/ui/train_model_panel.py"),
        Path("apps/train/ui/data_mapping_panel.py"),
        Path("apps/train/ui/feature_catalog/panel.py"),
        Path("apps/train/ui/feature_catalog/table_model.py"),
    )

    for source in sources:
        text = source.read_text(encoding="utf-8")
        assert "QTableWidget" not in text
        assert "QTableWidgetItem" not in text
