"""Minimal Trainer shell."""

from html import escape
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from apps.common.ui import style
from apps.predict.ui.status_widgets import model_status_badge_state
from apps.predict.ui.workspace import PredictWorkspace
from apps.train.ui.data_mapping_panel import DataMappingPanel
from apps.train.ui.train_model_panel import TrainModelPanel
from core.mapping.paths import MAPPING_JSON_FILE
from core.ml.artifacts import MODEL_FILE, TRAIN_DATA_FILE


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
        self.status_badges: dict[str, QLabel] = {}
        layout.addWidget(self._build_status_strip())
        tabs = QTabWidget(self)
        self.predict_workspace = PredictWorkspace(
            tabs,
            show_title=False,
            show_status_strip=False,
        )
        self.train_model_panel = TrainModelPanel(
            tabs,
            on_model_status_changed=self.refresh_status_strip,
        )
        tabs.addTab(
            self.predict_workspace,
            self.tab_names[0],
        )
        tabs.addTab(self.train_model_panel, self.tab_names[1])
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
        for key, label, value, kind in self._status_values():
            badge = _badge(label, value, kind)
            self.status_badges[key] = badge
            layout.addWidget(badge)
        layout.addStretch(1)
        return strip

    def refresh_status_strip(self) -> None:
        """Refresh Trainer and embedded Predict resource status badges."""
        for key, label, value, kind in self._status_values():
            badge = self.status_badges.get(key)
            if badge is not None:
                _set_badge(badge, label, value, kind)
        model_text, model_kind = model_status_badge_state(
            self.predict_workspace.prediction_controller.model_status()
        )
        self.predict_workspace.model_badge.set_status(model_text, model_kind)

    def _status_values(self) -> tuple[tuple[str, str, str, str], ...]:
        model_exists = Path(MODEL_FILE).exists()
        train_data_exists = Path(TRAIN_DATA_FILE).exists()
        mapping_exists = Path(MAPPING_JSON_FILE).exists()
        return (
            (
                "model",
                "모델 상태",
                "model.pkl loaded" if model_exists else "model.pkl missing",
                "ready" if model_exists else "missing",
            ),
            ("preprocess", "preprocess", "v1.0", "ready"),
            (
                "train_data",
                "학습 데이터",
                "found" if train_data_exists else "missing",
                "ready" if train_data_exists else "missing",
            ),
            (
                "mapping",
                "mapping",
                "loaded" if mapping_exists else "missing",
                "ready" if mapping_exists else "missing",
            ),
        )


def _badge(label: str, value: str, kind: str) -> QLabel:
    badge = QLabel()
    badge.setObjectName("StatusBadge")
    badge.setTextFormat(Qt.RichText)
    _set_badge(badge, label, value, kind)
    return badge


def _set_badge(badge: QLabel, label: str, value: str, kind: str) -> None:
    resolved = style.status_style(kind)
    badge.setText(
        f"<span style='color:{resolved.foreground};'>●</span> "
        f"<span style='color:{style.color('text.default')};'>{escape(label)}: {escape(value)}</span>"
    )
    badge.setStyleSheet(style.status_badge_stylesheet(kind))
