"""Small intent dialogs for Basic Feature Rename and Duplicate commands."""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from apps.common.ui import style
from apps.train.ui.data_definition.dialog_support import (
    configure_validation_summary,
    schedule_initial_focus,
    show_validation_summary,
)
from core.data_definition import DuplicateDefinitionIntent, RenameDefinitionIntent


class RenameFeatureDialog(QDialog):
    """Collect optional aliases while requiring an identifier selection."""

    def __init__(self, identity, values, on_apply, parent=None):  # noqa: ANN001
        super().__init__(parent)
        self._identity = identity
        self._values = values
        self._on_apply: Callable[[RenameDefinitionIntent], tuple[bool, str]] = on_apply
        self.setWindowTitle("Rename Feature")
        self.setAccessibleName("Rename Feature")
        self.setModal(True)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(*([style.spacing("space.outer")] * 4))
        layout.addWidget(_heading("Rename Feature"))
        form = QFormLayout()
        self.label_check, self.label_input = _optional_row(
            form, "Display name", values.get("label", ""), "New Feature display name"
        )
        self.key_check, self.key_input = _optional_row(
            form, "Predict key", values.get("column_key", ""), "New Predict key"
        )
        self.ml_check, self.ml_input = _optional_row(
            form, "ML name", values.get("ml_name", ""), "New ML name"
        )
        layout.addLayout(form)
        self.error_label = QLabel()
        configure_validation_summary(self.error_label, "Rename Feature validation summary")
        layout.addWidget(self.error_label)
        _actions(layout, self, self._apply, "Preview and Rename")
        schedule_initial_focus(self.key_check)

    def intent(self) -> RenameDefinitionIntent:
        return RenameDefinitionIntent(
            self._identity,
            label=self.label_input.text() if self.label_check.isChecked() else None,
            column_key=self.key_input.text() if self.key_check.isChecked() else None,
            ml_name=self.ml_input.text() if self.ml_check.isChecked() else None,
        )

    def _apply(self) -> None:
        accepted, message = self._on_apply(self.intent())
        if accepted:
            self.accept()
        else:
            show_validation_summary(self.error_label, message)


class DuplicateFeatureDialog(QDialog):
    """Require explicit independent names for one duplicate."""

    def __init__(self, identity, values, on_apply, parent=None):  # noqa: ANN001
        super().__init__(parent)
        self._identity = identity
        self._on_apply: Callable[[DuplicateDefinitionIntent], tuple[bool, str]] = on_apply
        self.setWindowTitle("Duplicate Feature")
        self.setAccessibleName("Duplicate Feature")
        self.setModal(True)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(*([style.spacing("space.outer")] * 4))
        layout.addWidget(_heading("Duplicate Feature"))
        form = QFormLayout()
        self.label_input = _input("Duplicate display name")
        self.key_input = _input("Duplicate Predict key")
        self.ml_input = _input("Duplicate ML name")
        self.label_input.setText(f"{values.get('label', '')} Copy".strip())
        self.key_input.setPlaceholderText("unique_predict_key")
        self.ml_input.setPlaceholderText("Required only when the original is an ML input")
        form.addRow("Display name", self.label_input)
        form.addRow("Predict key", self.key_input)
        form.addRow("ML name", self.ml_input)
        layout.addLayout(form)
        self.error_label = QLabel()
        configure_validation_summary(self.error_label, "Duplicate Feature validation summary")
        layout.addWidget(self.error_label)
        _actions(layout, self, self._apply, "Preview and Duplicate")
        schedule_initial_focus(self.label_input)

    def intent(self) -> DuplicateDefinitionIntent:
        return DuplicateDefinitionIntent(
            self._identity,
            self.label_input.text(),
            self.key_input.text(),
            self.ml_input.text(),
        )

    def _apply(self) -> None:
        accepted, message = self._on_apply(self.intent())
        if accepted:
            self.accept()
        else:
            show_validation_summary(self.error_label, message)


def _optional_row(form, title, current, accessible_name):  # noqa: ANN001
    checkbox = QCheckBox(f"Change {title}")
    checkbox.setAccessibleName(f"Select {title} for Rename")
    field = _input(accessible_name)
    field.setPlaceholderText(f"Current: {current or '(none)'}")
    field.setEnabled(False)
    checkbox.toggled.connect(field.setEnabled)
    container = QWidget()
    row = QHBoxLayout(container)
    row.setContentsMargins(0, 0, 0, 0)
    row.addWidget(checkbox)
    row.addWidget(field, 1)
    form.addRow(title, container)
    return checkbox, field


def _input(accessible_name):  # noqa: ANN001
    field = QLineEdit()
    field.setAccessibleName(accessible_name)
    return field


def _heading(text):  # noqa: ANN001
    label = QLabel(text)
    label.setObjectName("PanelTitle")
    label.setFont(style.qfont("font.window_title"))
    return label


def _actions(layout, dialog, callback, apply_text):  # noqa: ANN001
    actions = QHBoxLayout()
    actions.addStretch(1)
    cancel = QPushButton("Cancel")
    cancel.setAccessibleName(f"Cancel {dialog.windowTitle()}")
    cancel.clicked.connect(dialog.reject)
    apply_button = QPushButton(apply_text)
    apply_button.setAccessibleName(apply_text)
    apply_button.setDefault(True)
    apply_button.clicked.connect(callback)
    actions.addWidget(cancel)
    actions.addWidget(apply_button)
    layout.addLayout(actions)
