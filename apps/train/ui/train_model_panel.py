"""Train / Model visual panel."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from apps.common.ui import style
from core.ml.artifacts import MODEL_FILE, TRAIN_DATA_FILE


class TrainModelPanel(QWidget):
    """Visual Train / Model admin surface without execution wiring."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("TrainModelPanel")

        layout = QGridLayout(self)
        layout.setContentsMargins(
            style.spacing("space.outer"),
            style.spacing("space.outer"),
            style.spacing("space.outer"),
            style.spacing("space.outer"),
        )
        layout.setSpacing(style.spacing("space.sm"))
        layout.addWidget(self._build_training_config_panel(), 0, 0, 2, 1)
        layout.addWidget(self._build_progress_panel(), 0, 1, 1, 1)
        layout.addWidget(self._build_summary_panel(), 0, 2, 1, 1)
        layout.addWidget(self._build_log_panel(), 1, 1, 1, 2)
        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 2)
        layout.setColumnStretch(2, 2)
        layout.setRowStretch(1, 1)

    def _build_training_config_panel(self) -> QFrame:
        panel, body = _panel("학습 설정")
        dataset = _readonly_line(TRAIN_DATA_FILE)
        model_path = _readonly_line(MODEL_FILE)
        train_button = QPushButton("학습 실행")
        train_button.setObjectName("PrimaryButton")
        train_button.setEnabled(False)
        train_button.setToolTip("Trainer execution foundation은 후속 Arc에서 구현됩니다.")
        stop_button = QPushButton("중지")
        stop_button.setEnabled(False)

        body.addWidget(QLabel("데이터 파일 경로"))
        body.addWidget(dataset)
        body.addWidget(QLabel("model.pkl 저장 위치"))
        body.addWidget(model_path)
        body.addSpacing(style.spacing("space.sm"))
        actions = QHBoxLayout()
        actions.addWidget(train_button)
        actions.addWidget(stop_button)
        actions.addStretch(1)
        body.addLayout(actions)
        body.addStretch(1)
        return panel

    def _build_progress_panel(self) -> QFrame:
        panel, body = _panel("학습 진행 상황")
        body.addWidget(_status_line("전체 진행률", "대기 중", "neutral"))
        body.addWidget(_status_line("현재 단계", "Trainer execution deferred", "missing"))
        body.addWidget(_status_line("대상 타겟", "5 targets", "ready"))
        return panel

    def _build_summary_panel(self) -> QFrame:
        panel, body = _panel("Training Summary")
        body.addWidget(_status_line("모델 파일", "found" if Path(MODEL_FILE).exists() else "missing", "ready" if Path(MODEL_FILE).exists() else "missing"))
        body.addWidget(_status_line("학습 데이터", "found" if Path(TRAIN_DATA_FILE).exists() else "missing", "ready" if Path(TRAIN_DATA_FILE).exists() else "missing"))
        body.addWidget(_status_line("실행 상태", "not running", "neutral"))
        body.addStretch(1)
        return panel

    def _build_log_panel(self) -> QFrame:
        panel, body = _panel("Training Log")
        log = QTextEdit()
        log.setObjectName("TrainingLog")
        log.setReadOnly(True)
        log.setPlainText(
            "Trainer execution is intentionally deferred.\n"
            "This surface reserves the log/status area for Arc 11."
        )
        body.addWidget(log)
        return panel


def _panel(title: str) -> tuple[QFrame, QVBoxLayout]:
    panel = QFrame()
    panel.setObjectName("Panel")
    panel.setStyleSheet(style.panel_stylesheet())
    layout = QVBoxLayout(panel)
    layout.setContentsMargins(
        style.spacing("space.panel"),
        style.spacing("space.panel"),
        style.spacing("space.panel"),
        style.spacing("space.panel"),
    )
    layout.setSpacing(style.spacing("space.sm"))
    heading = QLabel(title)
    heading.setObjectName("PanelTitle")
    heading.setFont(style.qfont("font.panel_title"))
    layout.addWidget(heading)
    return panel, layout


def _readonly_line(value: str) -> QLineEdit:
    line = QLineEdit(value)
    line.setReadOnly(True)
    return line


def _status_line(label: str, value: str, kind: str) -> QLabel:
    item = QLabel(f"{label}: {value}")
    item.setStyleSheet(style.status_badge_stylesheet(kind))
    return item
