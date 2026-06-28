"""Train shell visual foundation tests."""

import os
from pathlib import Path

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QLabel, QProgressBar, QPushButton, QTableView, QTextEdit

from apps.predict.ui.shell import PredictShell
from apps.predict.ui.workspace import PredictWorkspace
from apps.train.ui.data_mapping_panel import DataMappingPanel
from apps.train.ui.shell import TrainShell
from apps.train.ui.train_model_panel import TrainModelPanel


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


def test_train_shell_tabs_and_predict_workspace_reuse():
    _app()
    shell = TrainShell()

    assert shell.tabs.count() == 3
    assert [shell.tabs.tabText(index) for index in range(3)] == [
        "Predict",
        "Train / Model",
        "Data Mapping",
    ]
    assert isinstance(shell.tabs.widget(0), PredictWorkspace)


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


def test_train_model_panel_is_visual_only_with_log_area():
    _app()
    panel = TrainModelPanel()

    assert panel.objectName() == "TrainModelPanel"
    log = panel.findChild(QTextEdit, "TrainingLog")
    assert log is not None
    assert "deferred" in log.toPlainText()
    assert panel.findChild(QProgressBar) is not None
    table = panel.findChild(QTableView)
    assert table is not None
    assert table.model().rowCount() == 5
    assert table.model().headerData(1, Qt.Horizontal, Qt.DisplayRole) == "Target"

    buttons = {button.text(): button for button in panel.findChildren(QPushButton)}
    for text in ("학습 데이터 선택", "학습 실행", "중지", "모델 열기", "로그 저장"):
        assert not buttons[text].isEnabled()


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


def test_train_ui_widgets_do_not_import_execution_foundations():
    sources = (
        Path("apps/train/ui/shell.py"),
        Path("apps/train/ui/train_model_panel.py"),
        Path("apps/train/ui/data_mapping_panel.py"),
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
    )

    for source in sources:
        text = source.read_text(encoding="utf-8")
        assert "QTableWidget" not in text
        assert "QTableWidgetItem" not in text
