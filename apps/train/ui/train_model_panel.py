"""Train / Model visual panel."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from uuid import uuid4

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFileDialog,
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
from apps.train.controllers.train_controller import TrainController
from apps.train.state.training_run_state import TrainingLogEvent, TrainingProgress, TrainingRequest, TrainingResult
from apps.train.ui.models.static_table_model import StaticTableModel
from core.ml.artifacts import MODEL_FILE, TRAIN_DATA_FILE


# Compatibility-only golden. Production instances render controller.registry_snapshot().
TARGETS = ("Cooling Power", "Heating Power", "Ref Qty", "Cooling Hz", "Heating Hz")


class TrainModelPanel(QWidget):
    """Train / Model admin surface wired to TrainController."""

    def __init__(
        self,
        parent: QWidget | None = None,
        controller: TrainController | None = None,
        on_model_status_changed: Callable[[], None] | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("TrainModelPanel")
        self.training_controller = controller or TrainController()
        self.targets = (
            self.training_controller.registry_snapshot().active_target_names
            if hasattr(self.training_controller, "registry_snapshot") else TARGETS
        )
        self._on_model_status_changed = on_model_status_changed

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
        self._update_control_state()

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
        self.select_button = _command_button("학습 데이터 선택")
        self.run_button = _command_button("학습 실행", primary=True)
        self.cancel_button = _command_button("중지")
        self.select_button.clicked.connect(self._select_training_data)
        self.run_button.clicked.connect(self._run_training)
        self.cancel_button.clicked.connect(self._cancel_training)
        for button in (
            self.select_button,
            self.run_button,
            self.cancel_button,
        ):
            layout.addWidget(button)
        layout.addStretch(1)
        return panel

    def _build_training_config_panel(self) -> QFrame:
        panel, body = _panel("학습 설정")
        body.addWidget(QLabel("데이터 파일 경로"))
        self.data_path_line = _readonly_line(TRAIN_DATA_FILE)
        body.addWidget(self.data_path_line)
        body.addWidget(QLabel("model.pkl 저장 위치"))
        self.model_path_line = _readonly_line(MODEL_FILE)
        body.addWidget(self.model_path_line)
        body.addWidget(QLabel("preprocess version"))
        body.addWidget(_readonly_line("v1.0"))
        body.addWidget(QLabel(f"모델/타겟 목록 ({len(self.targets)})"))
        self.target_list_layout = QVBoxLayout()
        body.addLayout(self.target_list_layout)
        self._render_target_list()
        body.addStretch(1)
        return panel

    def refresh_runtime_registry(self) -> None:
        """Reflect the active process generation without changing a running request."""
        self.targets = self.training_controller.registry_snapshot().active_target_names
        self._render_target_list()
        running = self.training_controller.active_request
        if running is not None:
            active = self.training_controller.registry_snapshot().generation_id
            self._set_status_text(
                f"Running generation {running.generation_id}; process active {active}."
            )

    def _render_target_list(self) -> None:
        while self.target_list_layout.count():
            item = self.target_list_layout.takeAt(0)
            if item.widget() is not None:
                item.widget().deleteLater()
        for index, target in enumerate(self.targets, start=1):
            self.target_list_layout.addWidget(_target_row(index, target))

    def _build_progress_panel(self) -> QFrame:
        panel, body = _panel("학습 진행 상황")
        body.addWidget(QLabel("전체 진행률"))
        progress = QProgressBar()
        progress.setRange(0, 100)
        progress.setValue(0)
        progress.setFormat("0%")
        self.progress_bar = progress
        body.addWidget(progress)
        self.status_label = _status_label("현재 단계", "대기", "neutral")
        body.addWidget(self.status_label)
        cards = QHBoxLayout()
        cards.addWidget(_metric_tile("완료", "0", "targets", "ready"))
        cards.addWidget(_metric_tile("진행 중", "0", "target", "running"))
        cards.addWidget(_metric_tile("대기 중", str(len(self.targets)), "targets", "missing"))
        body.addLayout(cards)
        body.addStretch(1)
        return panel

    def _build_summary_panel(self) -> QFrame:
        panel, body = _panel("Training Summary")
        self.summary_table = _summary_table(self.targets)
        body.addWidget(self.summary_table)
        return panel

    def _build_log_panel(self) -> QFrame:
        panel, body = _panel("Training Log")
        log = QTextEdit()
        log.setObjectName("TrainingLog")
        log.setReadOnly(True)
        log.setPlainText("Training execution ready.")
        self.log = log
        body.addWidget(log)
        return panel

    def _build_info_panel(self) -> QFrame:
        panel, body = _panel("학습 정보 요약")
        grid = QGridLayout()
        grid.setSpacing(style.spacing("space.sm"))
        values = (
            ("총 데이터 행 수", "0"), ("특성 수", "0"), ("타겟 수", str(len(self.targets))),
            ("CV 폴드 수", "5"), ("Optuna Trials", "30"), ("예상 남은 시간", "--:--"),
        )
        for index, (label, value) in enumerate(values):
            grid.addWidget(_metric_tile(label, value, "", "neutral"), index // 3, index % 3)
        body.addLayout(grid)
        body.addStretch(1)
        return panel

    def set_data_path(self, data_path: str) -> None:
        """Set training data path without depending on a file dialog."""
        self.data_path_line.setText(data_path)
        callback = getattr(self, "_data_selection_changed", None)
        if callback is not None:
            callback()
        self._update_control_state()

    def set_data_selection_changed_callback(self, callback) -> None:  # noqa: ANN001
        self._data_selection_changed = callback

    def _select_training_data(self) -> None:
        selected, _ = QFileDialog.getOpenFileName(
            self, "학습 데이터 선택", str(Path(self.data_path_line.text()).parent),
            "CSV files (*.csv);;All files (*)",
        )
        if selected:
            self.set_data_path(selected)

    def _run_training(self) -> None:
        request = TrainingRequest(
            run_id=f"train-ui-{uuid4().hex}",
            data_path=self.data_path_line.text(),
            model_output_path=self.model_path_line.text(),
        )
        self._set_running(True)
        self.log.clear()
        self._append_log_text("Training run starting.")
        self._set_summary_state("진행 중")
        try:
            self.training_controller.start(
                request,
                status_callback=self._set_status_text,
                log_callback=self._handle_log_event,
                progress_callback=self._handle_progress,
                finished_callback=self._handle_finished,
                failed_callback=self._handle_failed,
                cancelled_callback=self._handle_cancelled,
            )
        except RuntimeError as exc:
            self._handle_failed(TrainingResult(
                run_id=request.run_id,
                status="error",
                model_path=request.model_output_path,
                message=str(exc),
            )
            )

    def _cancel_training(self) -> None:
        if self.training_controller.cancel():
            self._set_status_text("Cancellation requested.")

    def _handle_log_event(self, event: TrainingLogEvent) -> None:
        self._append_log_text(event.message)

    def _handle_progress(self, progress: TrainingProgress) -> None:
        if progress.indeterminate:
            self.progress_bar.setRange(0, 0)
        else:
            total = max(progress.total, 1)
            self.progress_bar.setRange(0, total)
            self.progress_bar.setValue(min(progress.completed, total))
            self.progress_bar.setFormat(f"{progress.completed} / {total}")
        if progress.message:
            self._set_status_text(progress.message)

    def _handle_finished(self, result: TrainingResult) -> None:
        self._set_terminal_result(result, "완료", "Training complete.", 100)

    def _handle_failed(self, result: TrainingResult) -> None:
        message = result.message or "Training failed."
        self._set_terminal_result(result, "오류", message, 0)

    def _handle_cancelled(self, result: TrainingResult) -> None:
        message = result.message or "Training cancelled."
        self._set_terminal_result(result, "취소", message, 0)

    def _set_terminal_result(self, result: TrainingResult, status: str, message: str, progress_value: int) -> None:
        self._set_running(False)
        self._set_status_text(message)
        if result.summary:
            self._append_log_text(result.summary)
        if result.message:
            self._append_log_text(result.message)
        self._set_summary_state(status)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(progress_value)
        self.progress_bar.setFormat(f"{progress_value}%")
        if self._on_model_status_changed is not None:
            self._on_model_status_changed()

    def _set_running(self, running: bool) -> None:
        self.run_button.setEnabled(False)
        self.cancel_button.setEnabled(running)
        self.select_button.setEnabled(not running)
        if not running:
            self._update_control_state()

    def _update_control_state(self) -> None:
        running = self.training_controller.is_running
        resources = self.training_controller.resource_status(
            self.data_path_line.text(),
            self.model_path_line.text(),
        )
        data_exists = resources.data_status == "exists"
        self.run_button.setEnabled(data_exists and not running)
        self.cancel_button.setEnabled(running)
        self.select_button.setEnabled(not running)

    def _set_status_text(self, message: str) -> None:
        self.status_label.setText(f"현재 단계: {message}")
        kind = "running" if self.training_controller.is_running else "neutral"
        self.status_label.setStyleSheet(style.status_badge_stylesheet(kind))

    def _append_log_text(self, message: str) -> None:
        if message:
            self.log.append(message)

    def _set_summary_state(self, status: str) -> None:
        rows = tuple(
            (str(row + 1), target, status, "-", "-") for row, target in enumerate(self.targets)
        )
        self.summary_table.setModel(
            StaticTableModel(("#", "Target", "Status", "CV Mean", "Time"), rows)
        )
        self.summary_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)


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


def _command_button(text: str, primary: bool = False) -> QPushButton:
    button = QPushButton(text)
    if primary:
        button.setObjectName("PrimaryButton")
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


def _summary_table(targets: tuple[str, ...]) -> QTableView:
    rows = tuple((str(row + 1), target, "대기 중", "-", "-") for row, target in enumerate(targets))
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
