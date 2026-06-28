"""Train / Model visual panel."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QProgressBar,
    QPushButton,
    QTableView,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from apps.common.ui import style
from apps.train.ui.models.static_table_model import StaticTableModel
from core.ml.artifacts import MODEL_FILE, TRAIN_DATA_FILE


TARGETS = ("Cooling Power", "Heating Power", "Ref Qty", "Cooling Hz", "Heating Hz")


class TrainModelPanel(QWidget):
    """Visual Train / Model admin surface without execution wiring."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("TrainModelPanel")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            style.spacing("space.outer"),
            style.spacing("space.outer"),
            style.spacing("space.outer"),
            style.spacing("space.outer"),
        )
        layout.setSpacing(style.spacing("space.sm"))
        layout.addWidget(self._build_command_bar())

        content = QGridLayout()
        content.setSpacing(style.spacing("space.sm"))
        content.addWidget(self._build_training_config_panel(), 0, 0, 2, 1)
        content.addWidget(self._build_progress_panel(), 0, 1, 1, 1)
        content.addWidget(self._build_summary_panel(), 0, 2, 1, 1)
        content.addWidget(self._build_log_panel(), 1, 1, 1, 1)
        content.addWidget(self._build_info_panel(), 1, 2, 1, 1)
        content.setColumnStretch(0, 1)
        content.setColumnStretch(1, 2)
        content.setColumnStretch(2, 2)
        content.setRowStretch(1, 1)
        layout.addLayout(content, 1)

    def _build_command_bar(self) -> QFrame:
        panel = QFrame(self)
        panel.setObjectName("Panel")
        panel.setStyleSheet(style.panel_stylesheet())
        layout = QHBoxLayout(panel)
        layout.setContentsMargins(
            style.spacing("space.panel"),
            style.spacing("space.sm"),
            style.spacing("space.panel"),
            style.spacing("space.sm"),
        )
        layout.setSpacing(style.spacing("space.md"))
        for button in (
            _disabled_button("학습 데이터 선택"),
            _disabled_button("학습 실행", primary=True),
            _disabled_button("중지"),
            _disabled_button("모델 열기"),
            _disabled_button("로그 저장"),
        ):
            layout.addWidget(button)
        layout.addStretch(1)
        return panel

    def _build_training_config_panel(self) -> QFrame:
        panel, body = _panel("학습 설정")
        body.addWidget(QLabel("데이터 파일 경로"))
        body.addWidget(_readonly_line(TRAIN_DATA_FILE))
        body.addWidget(QLabel("model.pkl 저장 위치"))
        body.addWidget(_readonly_line(MODEL_FILE))
        body.addWidget(QLabel("preprocess version"))
        body.addWidget(_readonly_line("v1.0"))
        body.addWidget(QLabel(f"모델/타겟 목록 ({len(TARGETS)})"))
        for index, target in enumerate(TARGETS, start=1):
            body.addWidget(_target_row(index, target))
        body.addStretch(1)
        return panel

    def _build_progress_panel(self) -> QFrame:
        panel, body = _panel("학습 진행 상황")
        body.addWidget(QLabel("전체 진행률"))
        progress = QProgressBar()
        progress.setRange(0, 100)
        progress.setValue(0)
        progress.setFormat("0%")
        body.addWidget(progress)
        body.addWidget(_status_label("현재 단계", "Trainer execution deferred", "missing"))
        cards = QHBoxLayout()
        cards.addWidget(_metric_tile("완료", "0", "targets", "ready"))
        cards.addWidget(_metric_tile("진행 중", "0", "target", "running"))
        cards.addWidget(_metric_tile("대기 중", str(len(TARGETS)), "targets", "missing"))
        body.addLayout(cards)
        body.addStretch(1)
        return panel

    def _build_summary_panel(self) -> QFrame:
        panel, body = _panel("Training Summary")
        body.addWidget(_summary_table())
        return panel

    def _build_log_panel(self) -> QFrame:
        panel, body = _panel("Training Log")
        log = QTextEdit()
        log.setObjectName("TrainingLog")
        log.setReadOnly(True)
        log.setPlainText(
            "Trainer execution is intentionally deferred.\n"
            "This surface reserves command, progress, summary, and log areas for Arc 11."
        )
        body.addWidget(log)
        return panel

    def _build_info_panel(self) -> QFrame:
        panel, body = _panel("학습 정보 요약")
        grid = QGridLayout()
        grid.setSpacing(style.spacing("space.sm"))
        values = (
            ("총 데이터 행 수", "0"),
            ("특성 수", "0"),
            ("타겟 수", str(len(TARGETS))),
            ("CV 폴드 수", "5"),
            ("Optuna Trials", "30"),
            ("예상 남은 시간", "--:--"),
        )
        for index, (label, value) in enumerate(values):
            grid.addWidget(_metric_tile(label, value, "", "neutral"), index // 3, index % 3)
        body.addLayout(grid)
        body.addStretch(1)
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


def _disabled_button(text: str, primary: bool = False) -> QPushButton:
    button = QPushButton(text)
    if primary:
        button.setObjectName("PrimaryButton")
    button.setEnabled(False)
    button.setToolTip("Trainer execution foundation은 후속 Arc에서 구현됩니다.")
    return button


def _status_label(label: str, value: str, kind: str) -> QLabel:
    item = QLabel(f"{label}: {value}" if label else value)
    item.setStyleSheet(style.status_badge_stylesheet(kind))
    return item


def _target_row(index: int, target: str) -> QFrame:
    row = QFrame()
    row.setObjectName("MetricTile")
    row.setStyleSheet(_tile_stylesheet("neutral"))
    layout = QHBoxLayout(row)
    layout.setContentsMargins(
        style.spacing("space.sm"),
        style.spacing("space.xs"),
        style.spacing("space.sm"),
        style.spacing("space.xs"),
    )
    number = QLabel(str(index))
    number.setAlignment(Qt.AlignCenter)
    number.setMinimumWidth(24)
    layout.addWidget(number)
    layout.addWidget(QLabel(target), 1)
    layout.addWidget(_status_label("", "활성", "ready"))
    return row


def _metric_tile(label: str, value: str, detail: str, kind: str) -> QFrame:
    tile = QFrame()
    tile.setObjectName("MetricTile")
    tile.setStyleSheet(_tile_stylesheet(kind))
    layout = QVBoxLayout(tile)
    layout.setContentsMargins(
        style.spacing("space.sm"),
        style.spacing("space.sm"),
        style.spacing("space.sm"),
        style.spacing("space.sm"),
    )
    label_widget = QLabel(label)
    label_widget.setFont(style.qfont("font.caption"))
    value_widget = QLabel(value)
    value_widget.setAlignment(Qt.AlignCenter)
    value_widget.setFont(style.qfont("font.window_title"))
    layout.addWidget(label_widget)
    layout.addWidget(value_widget)
    if detail:
        layout.addWidget(QLabel(detail))
    return tile


def _summary_table() -> QTableView:
    rows = tuple(
        (str(row + 1), target, "대기 중", "-", "-")
        for row, target in enumerate(TARGETS)
    )
    table = QTableView()
    table.setModel(StaticTableModel(("#", "Target", "Status", "CV Mean", "Time"), rows))
    table.verticalHeader().setVisible(False)
    table.setEditTriggers(QAbstractItemView.NoEditTriggers)
    table.setSelectionMode(QAbstractItemView.SingleSelection)
    table.setMinimumHeight(230)
    table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    return table


def _tile_stylesheet(kind: str) -> str:
    role = {
        "ready": "table.result",
        "running": "table.selected",
        "missing": "table.warning",
        "neutral": "surface.header",
    }.get(kind, "surface.header")
    return (
        "QFrame#MetricTile {"
        f"background: {style.color(role)};"
        f"border: 1px solid {style.color('border.default')};"
        f"border-radius: {style.radius('radius.cell')}px;"
        "}"
    )
