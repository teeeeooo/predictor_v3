"""Feature Catalog help dialog."""

from __future__ import annotations

from PySide6.QtWidgets import QDialog, QDialogButtonBox, QTextEdit, QVBoxLayout, QWidget

from apps.common.ui import style


HELP_TEXT = """Feature Catalog는 ML 학습과 예측에 사용할 항목 목록입니다.

핵심 규칙
- 학습 데이터 컬럼명(ml_name)은 catalog row의 primary identity입니다.
- 학습 CSV/Excel 헤더는 active row의 ml_name과 일치해야 합니다.
- 화면 항목 키(ui_key)는 Predict/Train 화면 컬럼 키이며 ml_name과 역할이 다릅니다.
- catalog 변경은 모델 재학습이 필요할 수 있습니다.

Feature 유형
- input: 사용자가 직접 입력하는 ML feature입니다. 화면 항목 키와 표시명이 필요합니다.
- auto: 매핑 데이터에서 자동으로 채우는 feature입니다. 데이터 출처와 매핑 키가 필요합니다.
- result: 모델 target/result입니다. 모델 registry와 일치해야 합니다.
- one_hot: 냉매/팽창장치처럼 그룹 안에서 생성되는 one-hot feature입니다.
- derived: 코드에서 계산되는 feature입니다. CSV에서 수식은 관리하지 않습니다.
- hidden: 화면에 직접 표시하지 않는 내부 feature입니다.

누락값 처리
- disallow: 값이 없으면 검증 또는 예측 전에 실패합니다.
- mode_missing_allowed: 지정된 용량/소비전력 항목에만 허용됩니다.

작업 예시
- 단순 input feature는 학습 데이터 컬럼명, 화면 표시명, 화면 항목 키를 맞춰야 합니다.
- auto feature는 데이터 출처와 매핑 키를 함께 지정해야 합니다.
- one-hot category는 기존 One-hot 그룹 안에 추가하는 방식이 안전합니다.

검증 오류가 있으면 저장은 차단됩니다. CSV 내보내기는 현재 화면의 미저장 편집 상태를 검토용 파일로 저장합니다.
"""


class FeatureCatalogHelpDialog(QDialog):
    """Read-only help dialog for Feature Catalog Manager terms and rules."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Feature Catalog 도움말")
        self.setModal(True)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            style.spacing("space.panel"),
            style.spacing("space.panel"),
            style.spacing("space.panel"),
            style.spacing("space.panel"),
        )
        layout.setSpacing(style.spacing("space.sm"))

        self.text = QTextEdit(self)
        self.text.setReadOnly(True)
        self.text.setPlainText(HELP_TEXT)
        self.text.setMinimumSize(560, 420)
        layout.addWidget(self.text)

        buttons = QDialogButtonBox(QDialogButtonBox.Close, self)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
