"""Minimal Trainer shell."""

from apps.predict.ui.workspace import PredictWorkspace
from apps.train.ui.data_mapping_panel import DataMappingPanel
from apps.train.ui.train_model_panel import TrainModelPanel
from PySide6.QtWidgets import QMainWindow, QTabWidget


class TrainShell(QMainWindow):
    """Minimal shell for the PySide6 Trainer window."""

    tab_names = ("Predict", "Train / Model", "Data Mapping")

    def __init__(self, parent: QMainWindow | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("HVAC V3 Trainer")
        self.resize(1280, 820)

        tabs = QTabWidget(self)
        tabs.addTab(PredictWorkspace(tabs), self.tab_names[0])
        tabs.addTab(TrainModelPanel(tabs), self.tab_names[1])
        tabs.addTab(DataMappingPanel(tabs), self.tab_names[2])
        self.setCentralWidget(tabs)
        self.tabs = tabs
