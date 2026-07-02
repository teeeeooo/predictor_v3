"""Feature Catalog row add/duplicate dialog."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from apps.common.ui import style
from apps.train.application.feature_catalog import (
    FeatureCatalogDraftRequest,
    FeatureCatalogFieldOptions,
)


class FeatureCatalogRowDialog(QDialog):
    """Collect user-facing fields for a new Feature Catalog row."""

    def __init__(
        self,
        field_options: FeatureCatalogFieldOptions,
        parent: QWidget | None = None,
        initial: FeatureCatalogDraftRequest | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Feature 추가")
        self.setModal(True)
        self._field_options = field_options

        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            style.spacing("space.panel"),
            style.spacing("space.panel"),
            style.spacing("space.panel"),
            style.spacing("space.panel"),
        )
        layout.setSpacing(style.spacing("space.sm"))

        form = QFormLayout()
        form.setSpacing(style.spacing("space.sm"))
        self.role = _combo(field_options.values_for("role"))
        self.ml_name = QLineEdit()
        self.label = QLineEdit()
        self.source = _combo(field_options.values_for("source"))
        self.mapping_key = _combo(field_options.values_for("mapping_key"))
        self.one_hot_group = _combo(field_options.values_for("one_hot_group"))
        self.zero_fill_policy = _combo(field_options.values_for("zero_fill_policy"))
        self.active = QCheckBox("사용")
        self.notes = QTextEdit()
        self.notes.setFixedHeight(84)

        form.addRow("Feature 유형", self.role)
        form.addRow("학습 데이터 컬럼명", self.ml_name)
        form.addRow("화면 표시명", self.label)
        form.addRow("데이터 출처", self.source)
        form.addRow("매핑 키", self.mapping_key)
        form.addRow("One-hot 그룹", self.one_hot_group)
        form.addRow("누락값 처리", self.zero_fill_policy)
        form.addRow("사용 여부", self.active)
        form.addRow("메모", self.notes)
        layout.addLayout(form)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)
        self._apply_initial(initial)

    def request(self) -> FeatureCatalogDraftRequest:
        """Return a DTO for the user-entered row fields."""
        return FeatureCatalogDraftRequest(
            ml_name=self.ml_name.text(),
            role=self.role.currentText(),
            label=self.label.text(),
            source=self.source.currentText(),
            mapping_key=self.mapping_key.currentText(),
            one_hot_group=self.one_hot_group.currentText(),
            zero_fill_policy=self.zero_fill_policy.currentText(),
            active=self.active.isChecked(),
            notes=self.notes.toPlainText(),
        )

    def _apply_initial(self, initial: FeatureCatalogDraftRequest | None) -> None:
        request = initial or FeatureCatalogDraftRequest(
            ml_name="",
            role=_first_or_default(self._field_options.values_for("role"), "input"),
            label="",
            zero_fill_policy=_first_or_default(
                self._field_options.values_for("zero_fill_policy"),
                "disallow",
            ),
        )
        _set_combo_text(self.role, request.role)
        self.ml_name.setText(request.ml_name)
        self.label.setText(request.label)
        _set_combo_text(self.source, request.source)
        _set_combo_text(self.mapping_key, request.mapping_key)
        _set_combo_text(self.one_hot_group, request.one_hot_group)
        _set_combo_text(self.zero_fill_policy, request.zero_fill_policy)
        self.active.setChecked(request.active)
        self.notes.setPlainText(request.notes)


def _combo(values: tuple[str, ...]) -> QComboBox:
    combo = QComboBox()
    combo.setEditable(True)
    combo.setInsertPolicy(QComboBox.NoInsert)
    combo.addItems(values)
    return combo


def _set_combo_text(combo: QComboBox, value: str) -> None:
    found = combo.findText(value)
    if found >= 0:
        combo.setCurrentIndex(found)
        return
    combo.setEditText(value)


def _first_or_default(values: tuple[str, ...], default: str) -> str:
    return values[0] if values else default
