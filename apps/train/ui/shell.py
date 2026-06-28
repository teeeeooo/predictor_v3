"""Minimal Trainer shell."""

from pathlib import Path

from apps.common.ui import style
from core.mapping.paths import MAPPING_JSON_FILE
from core.ml.artifacts import MODEL_FILE, TRAIN_DATA_FILE
from apps.predict.ui.workspace import PredictWorkspace
from apps.train.ui.data_mapping_panel import DataMappingPanel
from apps.train.ui.train_model_panel import TrainModelPanel
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QMainWindow, QTabWidget, QVBoxLayout, QWidget


class TrainShell(QMainWindow):
    """Minimal shell for the PySide6 Trainer window."""

    tab_names = ("Predict", "Train / Model", "Data Mapping")

    def __init__(self, parent: QMainWindow | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("HVAC V3 Trainer")
        self.resize(1280, 820)
        self.setStyleSheet(style.app_stylesheet())

        central = QWidget(self)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(
            style.spacing("space.outer"),
            style.spacing("space.outer"),
            style.spacing("space.outer"),
            style.spacing("space.sm"),
        )
        layout.setSpacing(style.spacing("space.sm"))
        layout.addWidget(self._build_status_strip())
        tabs = QTabWidget(self)
        tabs.addTab(PredictWorkspace(tabs), self.tab_names[0])
        tabs.addTab(TrainModelPanel(tabs), self.tab_names[1])
        tabs.addTab(DataMappingPanel(tabs), self.tab_names[2])
        layout.addWidget(tabs, 1)
        self.setCentralWidget(central)
        self.tabs = tabs

    def _build_status_strip(self) -> QFrame:
        strip = QFrame(self)
        strip.setObjectName("Panel")
        strip.setStyleSheet(style.panel_stylesheet())
        layout = QHBoxLayout(strip)
        layout.setContentsMargins(
            style.spacing("space.panel"),
            style.spacing("space.sm"),
            style.spacing("space.panel"),
            style.spacing("space.sm"),
        )
        layout.setSpacing(style.spacing("space.sm"))
        layout.addWidget(_badge("모델 상태", "model.pkl loaded" if Path(MODEL_FILE).exists() else "model.pkl missing", "ready" if Path(MODEL_FILE).exists() else "missing"))
        layout.addWidget(_badge("preprocess", "v1.0", "ready"))
        layout.addWidget(_badge("학습 데이터", "found" if Path(TRAIN_DATA_FILE).exists() else "missing", "ready" if Path(TRAIN_DATA_FILE).exists() else "missing"))
        layout.addWidget(_badge("mapping", "loaded" if Path(MAPPING_JSON_FILE).exists() else "missing", "ready" if Path(MAPPING_JSON_FILE).exists() else "missing"))
        layout.addStretch(1)
        return strip


def _badge(label: str, value: str, kind: str) -> QLabel:
    badge = QLabel(f"{label}: {value}")
    badge.setObjectName("StatusBadge")
    badge.setStyleSheet(style.status_badge_stylesheet(kind))
    return badge
