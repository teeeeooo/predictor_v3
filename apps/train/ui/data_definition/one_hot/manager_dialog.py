"""Group-centered table-first One-hot authoring dialog."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from apps.train.ui.data_definition.command_preview_dialog import FeatureCommandPreviewDialog
from apps.train.ui.data_definition.one_hot.category_actions import OneHotCategoryActions
from apps.train.ui.data_definition.one_hot.group_actions import OneHotGroupActions


class OneHotManagerDialog(QDialog):
    """Render canonical groups/categories and forward only controlled intents."""

    def __init__(self, controller, apply_state, parent: QWidget | None = None):  # noqa: ANN001
        super().__init__(parent)
        self._controller = controller
        self._apply_state = apply_state
        self._projection = controller.one_hot_authoring_projection()
        self.setWindowTitle("One-hot Group and Category Manager")
        self.setAccessibleName(self.windowTitle())
        self.resize(980, 640)
        layout = QVBoxLayout(self)
        header = QLabel(
            "Data Definition owns group rules, emitted Features, order, and encoding policy. "
            "Mapping/provider values shown here are read-only.",
            self,
        )
        header.setWordWrap(True)
        layout.addWidget(header)
        self.group_choice = QComboBox(self)
        self.group_choice.setAccessibleName("One-hot group selector")
        self.group_choice.currentIndexChanged.connect(self._render_group)
        layout.addWidget(self.group_choice)
        self.group_details = QLabel(self)
        self.group_details.setWordWrap(True)
        self.group_details.setAccessibleName("One-hot group ownership and policy")
        layout.addWidget(self.group_details)
        layout.addWidget(self._group_actions_box())

        self.table = QTableWidget(0, 6, self)
        self.table.setHorizontalHeaderLabels(
            ("Order", "Source value", "Emitted ML Feature", "State", "Match / drift", "Provider identity")
        )
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setAccessibleName("One-hot category rules")
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table, 1)
        layout.addWidget(self._category_actions_box())

        self._group_actions = OneHotGroupActions(
            self._projection,
            self.selected_group,
            self._submit,
            self._refresh_projection,
            self,
        )
        self._category_actions = OneHotCategoryActions(
            self.selected_group,
            self.selected_category,
            self._projection,
            self._submit,
            self,
        )
        buttons = QDialogButtonBox(QDialogButtonBox.Close, self)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self._refresh_projection()

    def _group_actions_box(self) -> QGroupBox:
        box = QGroupBox("Group commands", self)
        grid = QGridLayout(box)
        actions = (
            ("Add", "Add inactive One-hot group", "add"),
            ("Edit policies", "Edit explicit unknown/missing policy", "edit"),
            ("Rename", "Rename group key without changing identity", "rename"),
            ("Duplicate", "Duplicate as inactive with new identities", "duplicate"),
            ("Remove", "Remove with explicit selector disposition", "remove"),
            ("Enable / Disable", "Toggle group runtime participation", "toggle_active"),
            ("Change source", "Migrate Static / Mapping-backed / External mode", "change_source"),
            ("Assign selector", "Change selector with explicit old-selector disposition", "assign_selector"),
        )
        self.group_buttons = []
        for index, (text, tooltip, method) in enumerate(actions):
            button = QPushButton(text, box)
            button.setToolTip(tooltip)
            button.clicked.connect(lambda _checked=False, name=method: getattr(self._group_actions, name)())
            grid.addWidget(button, index // 4, index % 4)
            self.group_buttons.append(button)
        return box

    def _category_actions_box(self) -> QGroupBox:
        box = QGroupBox("Category commands", self)
        row = QHBoxLayout(box)
        actions = (
            ("Add", "add"), ("Edit", "edit"), ("Rename emitted ML", "rename"),
            ("Duplicate", "duplicate"), ("Remove", "remove"),
            ("Enable / Disable", "toggle_active"),
            ("Move Up", "move_up"), ("Move Down", "move_down"),
        )
        self.category_buttons = []
        for text, method in actions:
            button = QPushButton(text, box)
            if method == "move_up":
                button.clicked.connect(lambda: self._category_actions.move("up"))
            elif method == "move_down":
                button.clicked.connect(lambda: self._category_actions.move("down"))
            else:
                button.clicked.connect(
                    lambda _checked=False, name=method: getattr(self._category_actions, name)()
                )
            row.addWidget(button)
            self.category_buttons.append(button)
        return box

    def _submit(self, intent) -> bool:  # noqa: ANN001
        prepared = self._controller.preview_one_hot_command(intent)
        preview_dialog = FeatureCommandPreviewDialog(prepared.preview, self)
        if not prepared.command_accepted:
            preview_dialog.exec()
            self._apply_state(self._controller.apply_prepared_one_hot_command(prepared))
            self._refresh_projection()
            return False
        if not preview_dialog.exec():
            return False
        state = self._controller.apply_prepared_one_hot_command(prepared)
        self._apply_state(state)
        self._refresh_projection()
        return state.last_action_ok

    def _refresh_projection(self) -> None:
        current_identity = self.group_choice.currentData()
        self._projection = self._controller.one_hot_authoring_projection()
        if hasattr(self, "_group_actions"):
            self._group_actions.update_projection(self._projection)
            self._category_actions.update_projection(self._projection)
        self.group_choice.blockSignals(True)
        self.group_choice.clear()
        for group in self._projection.groups:
            state = "active" if group.active else "inactive"
            self.group_choice.addItem(f"{group.group_key} — {group.source_mode} — {state}", group.identity)
        index = self.group_choice.findData(current_identity)
        self.group_choice.setCurrentIndex(index if index >= 0 else 0)
        self.group_choice.blockSignals(False)
        self._render_group()

    def _render_group(self) -> None:
        group = self.selected_group()
        enabled = group is not None
        for button in getattr(self, "group_buttons", ())[1:]:
            button.setEnabled(enabled)
        for button in getattr(self, "category_buttons", ()):
            button.setEnabled(enabled)
        self.table.setRowCount(0)
        if group is None:
            self.group_details.setText("No One-hot group is defined.")
            return
        provider = (
            "available" if group.provider_available else "unavailable"
        ) if group.provider_available is not None else "not applicable"
        self.group_details.setText(
            f"Selector: {group.selector_label} ({group.selector_column_key})\n"
            f"Owner: {group.vocabulary_owner}; binding: {group.source_binding or 'none'}; "
            f"provider: {provider}\n"
            f"Unknown: {group.unknown_policy}; missing: {group.missing_policy}. "
            "Category order changes only this group block; Predict display order is unchanged."
        )
        for category in group.categories:
            row = self.table.rowCount()
            self.table.insertRow(row)
            values = (
                str(category.order), category.source_value, category.emitted_ml_name,
                "active" if category.active else "inactive", category.drift_status,
                category.provider_category_identity or "—",
            )
            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setData(Qt.UserRole, category.identity)
                if category.drift_resolution:
                    item.setToolTip(category.drift_resolution)
                self.table.setItem(row, column, item)
        if self.table.rowCount():
            self.table.selectRow(0)

    def selected_group(self):  # noqa: ANN202
        identity = self.group_choice.currentData()
        return next((item for item in self._projection.groups if item.identity == identity), None)

    def selected_category(self):  # noqa: ANN202
        row = self.table.currentRow()
        if row < 0 or self.table.item(row, 0) is None:
            return None
        identity = self.table.item(row, 0).data(Qt.UserRole)
        group = self.selected_group()
        return next((item for item in group.categories if item.identity == identity), None)
