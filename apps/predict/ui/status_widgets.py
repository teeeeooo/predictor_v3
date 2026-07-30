"""Small status widgets for the Predict workspace."""

from __future__ import annotations

from html import escape

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QWidget

from apps.common.ui import style


_TARGET_BADGE_LABEL_LIMIT = 24


class StatusBadge(QLabel):
    """Non-clickable status badge using semantic visual roles."""

    def __init__(
        self,
        label: str,
        value: str,
        kind: str = "neutral",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._label = label
        self.setObjectName("StatusBadge")
        self.setAlignment(Qt.AlignCenter)
        self.setTextFormat(Qt.RichText)
        self.set_status(value, kind)

    def set_status(self, value: str, kind: str = "neutral") -> None:
        """Update badge text and visual status kind."""
        resolved = style.status_style(kind)
        text = f"{escape(self._label)}: {escape(value)}"
        self.setText(
            f"<span style='color:{resolved.foreground};'>●</span> "
            f"<span style='color:{style.color('text.default')};'>{text}</span>"
        )
        self.setStyleSheet(style.status_badge_stylesheet(kind))


class StatusStrip(QFrame):
    """Horizontal strip for high-level Predict environment status."""

    def __init__(
        self,
        badges: tuple[StatusBadge, ...],
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("Panel")
        self.setStyleSheet(style.panel_stylesheet())
        layout = QHBoxLayout(self)
        layout.setContentsMargins(
            style.spacing("space.panel"),
            style.spacing("space.sm"),
            style.spacing("space.panel"),
            style.spacing("space.sm"),
        )
        layout.setSpacing(style.spacing("space.sm"))
        for badge in badges:
            layout.addWidget(badge)
        layout.addStretch(1)


def model_status_badge_state(status) -> tuple[str, str]:  # noqa: ANN001
    """Return badge text/kind for PredictionModelStatus-like objects."""
    if status.status == "loaded":
        return "로드됨", "ready"
    if status.status == "exists":
        return "사용 가능", "ready"
    if status.status == "load-error":
        return "모델 로드 오류", "error"
    return "없음", "missing"


def target_status_badge_state(
    active_targets,
    target_result_keys,
    columns,
) -> tuple[str, str, str]:  # noqa: ANN001
    """Return concise text, kind, and full ordered Target tooltip."""
    result_key_by_target = dict(target_result_keys)
    label_by_result_key = {
        column.key: column.header
        for column in columns
        if column.group == "result"
    }
    labels = tuple(
        label_by_result_key.get(result_key_by_target.get(target, ""), target)
        for target in active_targets
    )
    if not labels:
        return "없음", "missing", "현재 활성 예측 Target이 없습니다."
    first_label = _compact_target_label(labels[0])
    value = (
        first_label
        if len(labels) == 1
        else f"{first_label} 외 {len(labels) - 1}개"
    )
    tooltip = f"현재 예측 Target ({len(labels)}): {', '.join(labels)}"
    return value, "ready", tooltip


def render_target_badge(badge, runtime_snapshot, columns) -> None:  # noqa: ANN001
    """Render committed runtime Targets without querying registry infrastructure."""
    value, kind, tooltip = target_status_badge_state(
        runtime_snapshot.active_targets,
        runtime_snapshot.target_result_keys,
        columns,
    )
    badge.set_status(value, kind)
    badge.setToolTip(tooltip)


def _compact_target_label(label: str) -> str:
    if len(label) <= _TARGET_BADGE_LABEL_LIMIT:
        return label
    return f"{label[:_TARGET_BADGE_LABEL_LIMIT - 1]}…"


def mapping_status_badge_state(status) -> tuple[str, str]:  # noqa: ANN001
    """Return badge text/kind for MappingResourceStatus-like objects."""
    if status.status == "loaded":
        return "로드됨", "ready"
    if status.status == "exists":
        return "사용 가능", "ready"
    if status.status == "invalid":
        return "유효하지 않음", "error"
    return "없음", "missing"


def prediction_summary_text(summary) -> str:  # noqa: ANN001
    """Return final prediction status text for workspace display."""
    if summary.cancelled:
        return (
            "예측 취소: 전체 {total}건 | 완료 {complete}건 | 오류 {error}건 | "
            "입력 확인 {invalid}건 | 취소 {cancelled}건"
        ).format(
            total=summary.total,
            complete=summary.complete,
            error=summary.error,
            invalid=summary.invalid,
            cancelled=summary.cancelled,
        )
    return (
        "예측 완료: 전체 {total}건 | 완료 {complete}건 | 오류 {error}건 | "
        "입력 확인 {invalid}건"
    ).format(
        total=summary.total,
        complete=summary.complete,
        error=summary.error,
        invalid=summary.invalid,
    )
