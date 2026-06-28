"""Predict workspace command bar."""

from __future__ import annotations

from PySide6.QtWidgets import QFrame, QHBoxLayout, QPushButton, QWidget

from apps.common.ui import style


class PredictCommandBar(QFrame):
    """Grouped command surface for the Predict workflow."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("Panel")
        self.setStyleSheet(style.panel_stylesheet())

        self.run_button = QPushButton("예측 실행", self)
        self.run_button.setObjectName("PrimaryButton")
        self.reset_button = QPushButton("초기화", self)
        self.add_row_button = QPushButton("행 추가", self)
        self.delete_row_button = QPushButton("행 삭제", self)
        self.paste_button = QPushButton("입력 붙여넣기", self)
        self.copy_results_button = QPushButton("결과 복사", self)
        self.export_button = QPushButton("Export CSV", self)

        self.export_button.setEnabled(False)
        self.export_button.setToolTip("후속 export UX slice에서 활성화됩니다.")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(
            style.spacing("space.panel"),
            style.spacing("space.sm"),
            style.spacing("space.panel"),
            style.spacing("space.sm"),
        )
        layout.setSpacing(style.spacing("space.sm"))
        layout.addWidget(self.run_button)
        layout.addWidget(self.reset_button)
        layout.addSpacing(style.spacing("space.md"))
        layout.addWidget(self.add_row_button)
        layout.addWidget(self.delete_row_button)
        layout.addSpacing(style.spacing("space.md"))
        layout.addWidget(self.paste_button)
        layout.addWidget(self.copy_results_button)
        layout.addWidget(self.export_button)
        layout.addStretch(1)
