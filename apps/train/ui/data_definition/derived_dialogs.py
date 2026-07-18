"""Restricted intent-only dialogs for Derived definitions."""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

from apps.train.controllers.derived_operand_projection import DerivedOperandOption
from core.data_definition import AddDerivedIntent, EditDerivedIntent

OperandOptions = tuple[DerivedOperandOption, ...]


class DerivedDefinitionDialog(QDialog):
    """Collect restricted safe_ratio intent without owning graph policy."""

    def __init__(
        self,
        submit: Callable[[object], tuple[bool, str]],
        operands: OperandOptions,
        *,
        identity: tuple[str, str] | None = None,
        values: dict[str, str] | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._submit = submit
        self._identity = identity
        values = values or {}
        self.setWindowTitle("Edit Derived" if identity else "Add Derived")
        self.setAccessibleName(self.windowTitle())
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.ml_name = QLineEdit(values.get("ml_name", ""), self)
        if identity is not None:
            self.ml_name.setReadOnly(True)
            self.ml_name.setToolTip("Use Rename Derived to change the output ML name.")
        self.operation = QComboBox(self)
        self.operation.addItem("safe_ratio", "safe_ratio")
        self.numerator = _operand_combo(operands, values.get("numerator_identity", ""), self)
        self.denominator = _operand_combo(operands, values.get("denominator_identity", ""), self)
        self.zero_policy = QComboBox(self)
        self.zero_policy.addItem("constant", "constant")
        self.zero_value = QLineEdit(values.get("zero_value", "0.0") or "0.0", self)
        self.active = QCheckBox("Active in ML projection", self)
        self.active.setChecked(values.get("active", "false").casefold() == "true")
        if identity is None:
            self.active.setChecked(False)
        form.addRow("Output ML name", self.ml_name)
        form.addRow("Operation", self.operation)
        form.addRow("Numerator", self.numerator)
        form.addRow("Denominator", self.denominator)
        form.addRow("Zero-denominator policy", self.zero_policy)
        form.addRow("Zero value", self.zero_value)
        form.addRow("Activation", self.active)
        layout.addLayout(form)
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel, self)
        buttons.accepted.connect(self._accept_intent)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _accept_intent(self) -> None:
        common = {
            "numerator_identity": str(self.numerator.currentData() or ""),
            "denominator_identity": str(self.denominator.currentData() or ""),
            "operation": str(self.operation.currentData()),
            "zero_denominator_policy": str(self.zero_policy.currentData()),
            "zero_value": self.zero_value.text(),
            "active": self.active.isChecked(),
        }
        intent = (
            EditDerivedIntent(self._identity, **common)
            if self._identity is not None
            else AddDerivedIntent(ml_name=self.ml_name.text(), **common)
        )
        accepted, message = self._submit(intent)
        if accepted:
            self.accept()
            return
        QMessageBox.warning(self, "Derived command blocked", message)


def _operand_combo(options, selected, parent):  # noqa: ANN001
    combo = QComboBox(parent)
    combo.addItem("Select a numeric Feature or Derived", "")
    for option in options:
        label = f"{option.display_name} [{option.identity}]"
        combo.addItem(label, option.identity)
        item = combo.model().item(combo.count() - 1)
        item.setEnabled(option.selectable)
        if option.blocked_reason:
            item.setToolTip(
                f"{option.blocked_reason} ({option.blocked_code})"
            )
    index = combo.findData(selected)
    if index >= 0:
        combo.setCurrentIndex(index)
    return combo
