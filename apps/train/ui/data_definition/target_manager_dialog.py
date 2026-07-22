"""Table-first Result/Target manager that emits structured canonical intents."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView, QCheckBox, QComboBox, QDialog, QDialogButtonBox, QFormLayout,
    QHBoxLayout, QInputDialog, QLabel, QLineEdit, QListWidget, QListWidgetItem,
    QMessageBox, QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)

from apps.train.ui.data_definition.command_preview_dialog import FeatureCommandPreviewDialog
from core.data_definition import (
    AddTargetIntent, ChangeTargetModelGroupIntent, ChangeTargetPolicyIntent,
    DuplicateTargetIntent, EditTargetIntent, MoveTargetIntent, RemoveTargetIntent,
    RenameTargetIntent, SetTargetActiveIntent,
)


class TargetManagerDialog(QDialog):
    def __init__(self, controller, apply_state, parent: QWidget | None = None):  # noqa: ANN001
        super().__init__(parent)
        self._controller = controller
        self._apply_state = apply_state
        self.setWindowTitle("Result and Target Registry Manager")
        self.resize(1120, 650)
        layout = QVBoxLayout(self)
        note = QLabel(
            "Data Definition owns Result identity, Target association, presentation order, and "
            "Target policy. Registry key, group name, and use_rfe are read-only.", self
        )
        note.setWordWrap(True)
        layout.addWidget(note)
        self.table = QTableWidget(0, 10, self)
        self.table.setHorizontalHeaderLabels((
            "Order", "Label", "Predict key", "ML name", "Visible", "Active",
            "Registry key", "Model group", "use_rfe", "Policy / final inputs",
        ))
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table, 1)
        actions = QHBoxLayout()
        for text, callback in (
            ("Add", self._add), ("Edit", self._edit), ("Rename", self._rename),
            ("Duplicate", self._duplicate), ("Remove", self._remove),
            ("Enable / Disable", self._toggle), ("Move Up", lambda: self._move("up")),
            ("Move Down", lambda: self._move("down")),
            ("Change Group", self._change_group), ("Change Policy", self._change_policy),
        ):
            button = QPushButton(text, self)
            button.clicked.connect(callback)
            actions.addWidget(button)
        layout.addLayout(actions)
        buttons = QDialogButtonBox(QDialogButtonBox.Close, self)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self._refresh()

    def _refresh(self) -> None:
        selected = self._selected_identity()
        self._projection = self._controller.target_authoring_projection()
        self.table.setRowCount(0)
        for row in self._projection.rows:
            index = self.table.rowCount()
            self.table.insertRow(index)
            values = (
                row.presentation_order, row.label, row.column_key, row.ml_name,
                "yes" if row.visible else "no", "active" if row.active else "inactive",
                row.registry_key, row.model_group_name, "yes" if row.use_rfe else "no",
                f"{row.policy_mode}: {', '.join(row.policy_ml_names)}\n"
                f"final: {', '.join(row.final_training_inputs)}",
            )
            for column, value in enumerate(values):
                item = QTableWidgetItem(str(value))
                item.setData(Qt.UserRole, row.identity)
                self.table.setItem(index, column, item)
            if row.identity == selected:
                self.table.selectRow(index)
        if self.table.rowCount() and self.table.currentRow() < 0:
            self.table.selectRow(0)

    def _selected_identity(self) -> str:
        row = self.table.currentRow()
        return "" if row < 0 or self.table.item(row, 0) is None else str(self.table.item(row, 0).data(Qt.UserRole))

    def _selected(self):  # noqa: ANN202
        identity = self._selected_identity()
        return next((item for item in self._projection.rows if item.identity == identity), None)

    def _submit(self, intent) -> bool:  # noqa: ANN001
        prepared = self._controller.preview_target_command(intent)
        dialog = FeatureCommandPreviewDialog(prepared.preview, self)
        if not prepared.command_accepted:
            dialog.exec()
            self._apply_state(self._controller.apply_prepared_target_command(prepared))
            self._refresh()
            return False
        if not dialog.exec():
            return False
        state = self._controller.apply_prepared_target_command(prepared)
        self._apply_state(state)
        self._refresh()
        return state.last_action_ok

    def _add(self) -> None:
        dialog = _TargetDefinitionDialog(self._projection, parent=self)
        if dialog.exec():
            self._submit(dialog.add_intent())

    def _edit(self) -> None:
        row = self._selected()
        if row:
            dialog = _TargetEditDialog(row, self)
            if dialog.exec():
                self._submit(EditTargetIntent(row.identity, dialog.label.text(), dialog.visible.isChecked()))

    def _rename(self) -> None:
        row = self._selected()
        if not row:
            return
        label, ok = QInputDialog.getText(self, "Rename Target", "Display label", text=row.label)
        if not ok:
            return
        key, ok = QInputDialog.getText(self, "Rename Target", "Predict column key", text=row.column_key)
        if not ok:
            return
        name, ok = QInputDialog.getText(self, "Rename Target", "ML name", text=row.ml_name)
        if ok:
            self._submit(RenameTargetIntent(row.identity, label, key, name))

    def _duplicate(self) -> None:
        row = self._selected()
        if not row:
            return
        dialog = _TargetDefinitionDialog(self._projection, source=row, duplicate=True, parent=self)
        if dialog.exec():
            values = dialog.names()
            self._submit(DuplicateTargetIntent(row.identity, *values))

    def _remove(self) -> None:
        row = self._selected()
        if row and QMessageBox.question(self, "Remove Target", f"Remove {row.ml_name} and its Result Feature?") == QMessageBox.Yes:
            self._submit(RemoveTargetIntent(row.identity))

    def _toggle(self) -> None:
        row = self._selected()
        if row:
            self._submit(SetTargetActiveIntent(row.identity, not row.active))

    def _move(self, direction: str) -> None:
        row = self._selected()
        if row:
            self._submit(MoveTargetIntent(row.identity, direction))

    def _change_group(self) -> None:
        row = self._selected()
        if not row:
            return
        groups = _groups(self._projection)
        labels = [f"{key} — {name} — use_rfe={use_rfe}" for _identity, key, name, use_rfe in groups]
        choice, ok = QInputDialog.getItem(self, "Change Model Group", "Validated group", labels, editable=False)
        if ok:
            self._submit(ChangeTargetModelGroupIntent(row.identity, groups[labels.index(choice)][0]))

    def _change_policy(self) -> None:
        row = self._selected()
        if not row:
            return
        dialog = _PolicyDialog(self._projection, row.policy_mode, row.policy_owner_identities, self)
        if dialog.exec():
            mode, owners = dialog.values()
            self._submit(ChangeTargetPolicyIntent(row.identity, mode, owners))


class _TargetDefinitionDialog(QDialog):
    def __init__(self, projection, source=None, duplicate=False, parent=None):  # noqa: ANN001
        super().__init__(parent)
        self._projection = projection
        self.setWindowTitle("Duplicate Target" if duplicate else "Add inactive Target")
        form = QFormLayout(self)
        suffix = " Copy" if duplicate else ""
        self.label = QLineEdit((source.label + suffix) if source else "", self)
        self.key = QLineEdit((source.column_key + "_copy") if source else "", self)
        self.ml = QLineEdit((source.ml_name + " Copy") if source else "", self)
        form.addRow("Display label", self.label); form.addRow("Predict key", self.key); form.addRow("ML name", self.ml)
        self.group = QComboBox(self)
        for identity, key, name, use_rfe in _groups(projection):
            self.group.addItem(f"{key} — {name} — use_rfe={use_rfe}", identity)
        form.addRow("Validated model group", self.group)
        self.policy = _PolicyDialog(projection, source.policy_mode if source else "exclude", source.policy_owner_identities if source else (), self, embedded=True)
        form.addRow(self.policy)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        buttons.accepted.connect(self.accept); buttons.rejected.connect(self.reject); form.addRow(buttons)

    def names(self) -> tuple[str, str, str]:
        return self.label.text(), self.key.text(), self.ml.text()

    def add_intent(self) -> AddTargetIntent:
        mode, owners = self.policy.values()
        return AddTargetIntent(*self.names(), str(self.group.currentData()), mode, owners)


class _TargetEditDialog(QDialog):
    def __init__(self, row, parent=None):  # noqa: ANN001
        super().__init__(parent)
        self.setWindowTitle("Edit Target presentation")
        form = QFormLayout(self)
        self.label = QLineEdit(row.label, self)
        self.visible = QCheckBox("Visible in Predict", self)
        self.visible.setChecked(row.visible)
        form.addRow("Display label", self.label)
        form.addRow(self.visible)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        buttons.accepted.connect(self.accept); buttons.rejected.connect(self.reject)
        form.addRow(buttons)


class _PolicyDialog(QDialog):
    def __init__(self, projection, mode, selected, parent=None, embedded=False):  # noqa: ANN001
        super().__init__(parent)
        layout = QVBoxLayout(self)
        self.mode = QComboBox(self); self.mode.addItems(("allowed", "exclude")); self.mode.setCurrentText(mode)
        layout.addWidget(self.mode)
        self.owners = QListWidget(self)
        for option in projection.policy_owner_options:
            item = QListWidgetItem(f"{option.ml_name} — {option.owner_kind}", self.owners)
            item.setData(Qt.UserRole, option.identity)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked if option.identity in selected else Qt.Unchecked)
            item.setToolTip(option.reason)
        layout.addWidget(self.owners)
        if not embedded:
            buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
            buttons.accepted.connect(self.accept); buttons.rejected.connect(self.reject); layout.addWidget(buttons)

    def values(self) -> tuple[str, tuple[str, ...]]:
        return self.mode.currentText(), tuple(
            str(self.owners.item(index).data(Qt.UserRole))
            for index in range(self.owners.count())
            if self.owners.item(index).checkState() == Qt.Checked
        )


def _groups(projection):  # noqa: ANN001
    return projection.model_groups
