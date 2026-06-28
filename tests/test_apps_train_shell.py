"""Train shell visual foundation tests."""

import os

from PySide6.QtWidgets import QApplication, QPushButton, QTextEdit

from apps.predict.ui.workspace import PredictWorkspace
from apps.train.ui.data_mapping_panel import DataMappingPanel
from apps.train.ui.shell import TrainShell
from apps.train.ui.train_model_panel import TrainModelPanel


def _app() -> QApplication:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    return QApplication.instance() or QApplication([])


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


def test_train_model_panel_is_visual_only_with_log_area():
    _app()
    panel = TrainModelPanel()

    assert panel.objectName() == "TrainModelPanel"
    log = panel.findChild(QTextEdit, "TrainingLog")
    assert log is not None
    assert "deferred" in log.toPlainText()
    train_button = next(
        button for button in panel.findChildren(QPushButton) if button.text() == "학습 실행"
    )
    assert not train_button.isEnabled()


def test_data_mapping_panel_is_visual_only_with_log_area():
    _app()
    panel = DataMappingPanel()

    assert panel.objectName() == "DataMappingPanel"
    log = panel.findChild(QTextEdit, "MappingLog")
    assert log is not None
    assert "deferred" in log.toPlainText()
    update_button = next(
        button for button in panel.findChildren(QPushButton) if button.text() == "매핑 업데이트"
    )
    assert not update_button.isEnabled()
