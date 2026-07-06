"""Small status widgets for the Predict workspace."""

from __future__ import annotations

from html import escape

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QWidget

from apps.common.ui import style


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
        return "model.pkl loaded", "ready"
    if status.status == "exists":
        return "model.pkl exists", "ready"
    if status.status == "load-error":
        return "model load error", "error"
    return "model.pkl missing", "missing"


def mapping_status_badge_state(status) -> tuple[str, str]:  # noqa: ANN001
    """Return badge text/kind for MappingResourceStatus-like objects."""
    if status.status == "loaded":
        return "loaded", "ready"
    if status.status == "exists":
        return "available", "ready"
    if status.status == "invalid":
        return "invalid", "error"
    return "missing", "missing"


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
