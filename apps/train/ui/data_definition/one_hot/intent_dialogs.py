"""Intent-only forms for One-hot group and category commands."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QVBoxLayout,
    QWidget,
)


class OneHotGroupIntentDialog(QDialog):
    """Collect explicit group/source/policy intent without domain decisions."""

    def __init__(self, projection, group=None, parent: QWidget | None = None):  # noqa: ANN001
        super().__init__(parent)
        self._projection = projection
        self._group = group
        self.setWindowTitle("Edit One-hot Group" if group else "Add One-hot Group")
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.group_key = QLineEdit(group.group_key if group else "", self)
        self.selector = QComboBox(self)
        for item in projection.selectors:
            current = bool(group and item.identity == group.selector_feature_identity)
            status = "" if item.selectable or current else f" — {item.takeover_state}"
            self.selector.addItem(
                f"{item.label} ({item.column_key}){status}", item.identity
            )
            model_item = self.selector.model().item(self.selector.count() - 1)
            model_item.setEnabled(item.selectable or current)
            if item.actionable_reason:
                owners = ", ".join(item.affected_owners)
                model_item.setToolTip(
                    item.actionable_reason + (f" Affected: {owners}." if owners else "")
                )
        if group:
            self.selector.setCurrentIndex(max(0, self.selector.findData(group.selector_feature_identity)))
        self.mode = QComboBox(self)
        for value, label in (
            ("static", "Static — Data Definition owns values"),
            ("mapping_backed", "Mapping-backed — Data Mapping owns values"),
            ("external", "External — provider owns identity/value"),
        ):
            self.mode.addItem(label, value)
            if value == "external" and not projection.external_creation_enabled:
                self.mode.model().item(self.mode.count() - 1).setEnabled(False)
        self.binding = QComboBox(self)
        self.binding.setEditable(False)
        self.unknown = QComboBox(self)
        self.unknown.addItem("Warn and encode all-zero", "warn_all_zero")
        self.missing = QComboBox(self)
        self.missing.addItem("Encode all-zero", "all_zero")
        owner = QLabel(self)
        owner.setWordWrap(True)
        self.owner = owner
        form.addRow("Group key", self.group_key)
        form.addRow("Selector Feature", self.selector)
        form.addRow("Source mode", self.mode)
        form.addRow("Source binding", self.binding)
        form.addRow("Vocabulary owner", owner)
        form.addRow("Unknown value", self.unknown)
        form.addRow("Missing value", self.missing)
        layout.addLayout(form)
        if projection.external_disabled_reason:
            note = QLabel(projection.external_disabled_reason, self)
            note.setWordWrap(True)
            layout.addWidget(note)
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self.mode.currentIndexChanged.connect(self._refresh_source)
        if group:
            self.mode.setCurrentIndex(self.mode.findData(group.source_mode))
        self._refresh_source()
        if group:
            index = self.binding.findData(group.source_binding)
            if index < 0 and group.source_binding:
                self.binding.addItem(group.source_binding, group.source_binding)
                index = self.binding.count() - 1
            self.binding.setCurrentIndex(max(0, index))
            self.unknown.setCurrentIndex(max(0, self.unknown.findData(group.unknown_policy)))
            self.missing.setCurrentIndex(max(0, self.missing.findData(group.missing_policy)))

    def values(self) -> dict[str, object]:
        return {
            "group_key": self.group_key.text(),
            "selector_feature_identity": str(self.selector.currentData() or ""),
            "source_mode": str(self.mode.currentData() or ""),
            "source_binding": str(self.binding.currentData() or ""),
            "unknown_policy": str(self.unknown.currentData() or ""),
            "missing_policy": str(self.missing.currentData() or ""),
        }

    def _refresh_source(self) -> None:
        mode = str(self.mode.currentData() or "")
        self.binding.clear()
        for snapshot in self._projection.vocabulary_snapshots:
            if snapshot.source_mode == mode:
                self.binding.addItem(snapshot.source_binding, snapshot.source_binding)
        self.binding.setEnabled(mode != "static")
        self.owner.setText({
            "static": "Data Definition owns source values and selector options.",
            "mapping_backed": "Persisted Data Mapping values are read-only candidates.",
            "external": "Provider category identity and value are read-only.",
        }.get(mode, ""))


class OneHotCategoryIntentDialog(QDialog):
    """Collect a bounded category overlay; provider fields remain read-only."""

    def __init__(self, group, snapshots, category=None, parent=None):  # noqa: ANN001
        super().__init__(parent)
        self._group = group
        self.setWindowTitle("Edit One-hot Category" if category else "Add One-hot Category")
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.source = QLineEdit(category.source_value if category else "", self)
        self.source_choice = QComboBox(self)
        snapshot = next((item for item in snapshots
                         if item.source_mode == group.source_mode
                         and item.source_binding == group.source_binding), None)
        if snapshot:
            for item in snapshot.categories:
                self.source_choice.addItem(item.label or item.value, (item.identity, item.value))
        if category and self.source_choice.findData(
            (category.provider_category_identity, category.source_value)
        ) < 0:
            self.source_choice.addItem(
                f"{category.source_value} (stale)",
                (category.provider_category_identity, category.source_value),
            )
        if category:
            target = (
                category.provider_category_identity if group.source_mode == "external" else "",
                category.source_value,
            )
            index = self.source_choice.findData(target)
            self.source_choice.setCurrentIndex(max(0, index))
        self.emitted = QLineEdit(category.emitted_ml_name if category else "", self)
        self.active = QCheckBox("Active in group encoding", self)
        self.active.setChecked(category.active if category else False)
        if category is None:
            self.active.setEnabled(False)
        if group.source_mode == "static":
            form.addRow("Source value", self.source)
        else:
            self.source.setVisible(False)
            form.addRow("Read-only source candidate", self.source_choice)
        form.addRow("Emitted ML name", self.emitted)
        form.addRow("Lifecycle", self.active)
        layout.addLayout(form)
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def values(self) -> dict[str, object]:
        if self._group.source_mode == "static":
            source_value = self.source.text()
            provider_identity = ""
        else:
            provider_identity, source_value = self.source_choice.currentData() or ("", "")
            if self._group.source_mode != "external":
                provider_identity = ""
        return {
            "source_value": str(source_value),
            "provider_category_identity": str(provider_identity),
            "emitted_ml_name": self.emitted.text(),
            "active": self.active.isChecked(),
        }
