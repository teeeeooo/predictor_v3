"""Candidate/Active review surface backed only by Qt-free projections."""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableView,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from apps.common.ui import style
from apps.train.application.model_management import (
    CandidateReview,
    ModelManagementSnapshot,
    PromotionOutcome,
)
from apps.train.ui.models.static_table_model import StaticTableModel
from apps.train.ui.model_management_text import (
    comparison_value,
    display_value,
    promotion_failure_message,
)


class ModelManagementPanel(QFrame):
    """Render model lifecycle state and issue guarded promotion commands."""

    def __init__(
        self,
        controller,
        parent: QWidget | None = None,
        *,
        confirm: Callable[[str, str], bool] | None = None,
        notify: Callable[[str, str, bool], None] | None = None,
        on_snapshot_changed: Callable[[ModelManagementSnapshot], None] | None = None,
    ) -> None:  # noqa: ANN001
        super().__init__(parent)
        self.setObjectName("ModelManagementPanel")
        self.setStyleSheet(style.panel_stylesheet())
        self._controller = controller
        self._confirm = confirm or self._confirm_dialog
        self._notify = notify or self._notify_dialog
        self._on_snapshot_changed = on_snapshot_changed
        self._snapshot = ModelManagementSnapshot("empty")
        self._candidate_ids: tuple[str, ...] = ()
        self._selected_candidate_id = ""
        self._training_running = False
        self._build()
        self.refresh()

    def _build(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            style.spacing("space.panel"),
            style.spacing("space.panel"),
            style.spacing("space.panel"),
            style.spacing("space.panel"),
        )
        layout.setSpacing(style.spacing("space.sm"))
        heading = QHBoxLayout()
        title = QLabel("모델 관리")
        title.setFont(style.qfont("font.panel_title"))
        heading.addWidget(title)
        heading.addStretch(1)
        self.refresh_button = QPushButton("새로고침")
        self.refresh_button.clicked.connect(self.refresh)
        heading.addWidget(self.refresh_button)
        layout.addLayout(heading)

        self.active_label = QLabel()
        self.state_label = QLabel()
        self.state_label.setWordWrap(True)
        layout.addWidget(self.active_label)
        layout.addWidget(self.state_label)

        self.candidate_table = QTableView()
        self.candidate_table.setObjectName("CandidateTable")
        self.candidate_table.verticalHeader().setVisible(False)
        self.candidate_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.candidate_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.candidate_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.candidate_table.setMinimumHeight(150)
        layout.addWidget(self.candidate_table)

        self.selection_label = QLabel("학습 결과를 선택하세요.")
        self.selection_label.setWordWrap(True)
        layout.addWidget(self.selection_label)
        self.metrics_table = QTableView()
        self.metrics_table.setObjectName("CandidateMetricsTable")
        self.metrics_table.verticalHeader().setVisible(False)
        self.metrics_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.metrics_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.metrics_table.setMinimumHeight(150)
        layout.addWidget(self.metrics_table)

        action_row = QHBoxLayout()
        self.promotion_message = QLabel()
        self.promotion_message.setWordWrap(True)
        action_row.addWidget(self.promotion_message, 1)
        self.promote_button = QPushButton("이 모델 사용")
        self.promote_button.setObjectName("PrimaryButton")
        self.promote_button.clicked.connect(self._promote_selected)
        action_row.addWidget(self.promote_button)
        layout.addLayout(action_row)

        self.advanced_button = QPushButton("고급 정보 보기")
        self.advanced_button.setCheckable(True)
        self.advanced_button.toggled.connect(self._toggle_advanced)
        layout.addWidget(self.advanced_button)
        self.advanced_text = QTextEdit()
        self.advanced_text.setObjectName("CandidateAdvancedDetails")
        self.advanced_text.setReadOnly(True)
        self.advanced_text.setVisible(False)
        self.advanced_text.setMaximumHeight(190)
        layout.addWidget(self.advanced_text)

    def refresh(self) -> None:
        previous = self._selected_candidate_id
        inspect_models = getattr(self._controller, "inspect_models", None)
        snapshot = inspect_models() if inspect_models is not None else None
        self._snapshot = snapshot or ModelManagementSnapshot(
            "unavailable",
            message="모델 lifecycle 구성이 연결되지 않았습니다.",
        )
        self.active_label.setText(
            "현재 사용 모델: "
            + (
                self._snapshot.active_candidate_id
                if self._snapshot.active_candidate_id
                else "선택되지 않음"
            )
        )
        self.state_label.setText(self._state_message())
        self._candidate_ids = tuple(
            item.candidate_id for item in self._snapshot.candidates
        )
        rows = tuple(
            (
                item.candidate_id,
                item.created_at,
                item.run_id,
                "사용 중" if item.is_active else (
                    "사용 가능" if item.promotion_eligible else "사용 불가"
                ),
            )
            for item in self._snapshot.candidates
        )
        self.candidate_table.setModel(
            StaticTableModel(
                ("학습 결과", "생성 시각", "Training run", "상태"),
                rows,
            )
        )
        self.candidate_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )
        self.candidate_table.selectionModel().selectionChanged.connect(
            self._candidate_selection_changed
        )
        selected = previous if previous in self._candidate_ids else (
            self._candidate_ids[0] if self._candidate_ids else ""
        )
        if selected:
            self.candidate_table.selectRow(self._candidate_ids.index(selected))
        else:
            self._selected_candidate_id = ""
            self._render_candidate(None)
        if self._on_snapshot_changed is not None:
            self._on_snapshot_changed(self._snapshot)

    def set_training_running(self, running: bool) -> None:
        self._training_running = running
        self.refresh_button.setEnabled(not running)
        self._update_promotion_action(self._selected())

    def _candidate_selection_changed(self) -> None:
        indexes = self.candidate_table.selectionModel().selectedRows()
        if not indexes:
            return
        row = indexes[0].row()
        if row >= len(self._candidate_ids):
            return
        self._selected_candidate_id = self._candidate_ids[row]
        self._render_candidate(self._selected())

    def _selected(self) -> CandidateReview | None:
        return next(
            (
                item for item in self._snapshot.candidates
                if item.candidate_id == self._selected_candidate_id
            ),
            None,
        )

    def _render_candidate(self, candidate: CandidateReview | None) -> None:
        if candidate is None:
            self.selection_label.setText("표시할 학습 결과가 없습니다.")
            self.metrics_table.setModel(StaticTableModel((), ()))
            self.advanced_text.clear()
            self._update_promotion_action(None)
            return
        baseline = {
            "fair": "현재 사용 모델과 공정 비교",
            "unfair": "현재 사용 모델과 비교할 수 없음",
            "no_baseline": "비교 기준 없음 (Bootstrap)",
            "unavailable": "비교 정보 없음",
        }.get(candidate.baseline_kind, "비교 정보 없음")
        self.selection_label.setText(
            f"선택한 학습 결과: {candidate.candidate_id} · {baseline}"
            + (f" · {candidate.baseline_reason}" if candidate.baseline_reason else "")
        )
        rows = tuple(
            (
                item.name,
                display_value(item.r2),
                display_value(item.mae),
                display_value(item.rmse),
                comparison_value(item),
                item.blocking_reason or item.unavailable_reason,
            )
            for item in candidate.targets
        )
        self.metrics_table.setModel(
            StaticTableModel(
                ("Target", "R²", "MAE", "RMSE", "기준 대비", "상태/사유"),
                rows,
            )
        )
        self.metrics_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )
        advanced = []
        if candidate.analysis_reason:
            advanced.append(f"분석 정보: {candidate.analysis_reason}")
        for section in candidate.advanced_sections:
            advanced.append(section.title)
            advanced.extend(f"• {name}: {value}" for name, value in section.rows)
        self.advanced_text.setPlainText("\n".join(advanced) or "고급 정보가 없습니다.")
        self._update_promotion_action(candidate)

    def _update_promotion_action(
        self,
        candidate: CandidateReview | None,
    ) -> None:
        visible = bool(
            candidate
            and candidate.promotion_eligible
            and not candidate.is_active
        )
        self.promote_button.setVisible(visible)
        self.promote_button.setEnabled(visible and not self._training_running)
        if candidate is None:
            message = ""
        elif candidate.is_active:
            message = "현재 사용 중인 모델입니다."
        elif not candidate.promotion_eligible:
            reason = " · ".join(candidate.blocking_reasons)
            message = "현재 상태에서는 적용할 수 없습니다."
            if reason:
                message += f" {reason}"
        elif self._training_running:
            message = "학습 실행 중에는 사용 모델을 변경할 수 없습니다."
        else:
            message = "확인 후 이 학습 결과를 현재 사용 모델로 변경할 수 있습니다."
        self.promotion_message.setText(message)

    def _promote_selected(self) -> None:
        candidate = self._selected()
        if candidate is None or not candidate.promotion_eligible or candidate.is_active:
            return
        current = self._snapshot.active_candidate_id or "선택되지 않음"
        if not self._confirm(candidate.candidate_id, current):
            return
        outcome = self._controller.promote_candidate(
            candidate.candidate_id,
            expected_revision=self._snapshot.active_revision,
        )
        self._apply_promotion_outcome(outcome)

    def _apply_promotion_outcome(self, outcome: PromotionOutcome) -> None:
        success = outcome.status == "active"
        self._selected_candidate_id = outcome.candidate_id
        self.refresh()
        message = (
            "현재 사용 모델을 변경했습니다."
            if success
            else promotion_failure_message(outcome)
        )
        self._notify("모델 변경", message, success)

    def _state_message(self) -> str:
        if self._snapshot.status == "corrupt":
            return (
                "모델 lifecycle 상태를 안전하게 읽을 수 없습니다. "
                "모델을 변경하지 않았습니다. 진단 로그를 확인하세요. "
                + self._snapshot.message
            )
        return self._snapshot.message

    def _toggle_advanced(self, checked: bool) -> None:
        self.advanced_text.setVisible(checked)
        self.advanced_button.setText(
            "고급 정보 닫기" if checked else "고급 정보 보기"
        )

    def _confirm_dialog(self, candidate_id: str, current: str) -> bool:
        return QMessageBox.question(
            self,
            "현재 사용 모델 변경",
            f"선택한 학습 결과: {candidate_id}\n현재 사용 모델: {current}\n\n"
            "선택한 모델을 사용하시겠습니까?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        ) == QMessageBox.Yes

    def _notify_dialog(self, title: str, message: str, success: bool) -> None:
        dialog = QMessageBox.information if success else QMessageBox.warning
        dialog(self, title, message)
