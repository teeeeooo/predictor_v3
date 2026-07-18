"""View-side One-hot group intent collection."""

from __future__ import annotations

from PySide6.QtWidgets import QInputDialog, QMessageBox, QWidget

from apps.train.ui.data_definition.one_hot.intent_dialogs import OneHotGroupIntentDialog
from core.data_definition import (
    AddOneHotGroupIntent,
    AssignOneHotSelectorIntent,
    ChangeOneHotSourceModeIntent,
    DuplicateOneHotGroupIntent,
    EditOneHotGroupIntent,
    RemoveOneHotGroupIntent,
    RenameOneHotGroupIntent,
    SetOneHotGroupActiveIntent,
)


class OneHotGroupActions:
    def __init__(self, projection, selected, submit, refresh, parent: QWidget):  # noqa: ANN001
        self.projection = projection
        self.selected = selected
        self.submit = submit
        self.refresh = refresh
        self.parent = parent

    def update_projection(self, projection) -> None:  # noqa: ANN001
        self.projection = projection

    def add(self) -> None:
        dialog = OneHotGroupIntentDialog(self.projection, parent=self.parent)
        if not dialog.exec():
            return
        values = dialog.values()
        self.submit(AddOneHotGroupIntent(**values, active=False))

    def edit(self) -> None:
        group = self.selected()
        if group is None:
            return
        dialog = OneHotGroupIntentDialog(self.projection, group, self.parent)
        dialog.group_key.setEnabled(False)
        dialog.selector.setEnabled(False)
        dialog.mode.setEnabled(False)
        dialog.binding.setEnabled(False)
        if not dialog.exec():
            return
        values = dialog.values()
        self.submit(EditOneHotGroupIntent(
            group.identity,
            str(values["unknown_policy"]),
            str(values["missing_policy"]),
            str(values["source_binding"]),
        ))

    def rename(self) -> None:
        group = self.selected()
        if group is None:
            return
        value, ok = QInputDialog.getText(
            self.parent, "Rename One-hot Group", "Unique group key", text=group.group_key
        )
        if ok:
            self.submit(RenameOneHotGroupIntent(group.identity, value))

    def duplicate(self) -> None:
        group = self.selected()
        if group is None:
            return
        key, ok = QInputDialog.getText(
            self.parent, "Duplicate One-hot Group", "New group key",
            text=f"{group.group_key}_copy",
        )
        if not ok:
            return
        selector = self._choose_selector("Duplicate One-hot Group")
        if not selector:
            return
        suffix, ok = QInputDialog.getText(
            self.parent, "Duplicate One-hot Group", "Emitted ML name suffix", text="_copy"
        )
        if ok:
            self.submit(DuplicateOneHotGroupIntent(group.identity, key, selector, suffix))

    def remove(self) -> None:
        group = self.selected()
        if group is None:
            return
        label, ok = QInputDialog.getItem(
            self.parent,
            "Remove One-hot Group",
            "Selector disposition",
            ("Detach as ordinary Feature", "Remove selector Feature"),
            0,
            False,
        )
        if ok:
            disposition = "detach" if label.startswith("Detach") else "remove"
            self.submit(RemoveOneHotGroupIntent(group.identity, disposition))

    def toggle_active(self) -> None:
        group = self.selected()
        if group is not None:
            self.submit(SetOneHotGroupActiveIntent(group.identity, not group.active))

    def assign_selector(self) -> None:
        group = self.selected()
        if group is None:
            return
        selector = self._choose_selector("Assign One-hot Selector")
        if not selector:
            return
        label, ok = QInputDialog.getItem(
            self.parent,
            "Assign One-hot Selector",
            "Previous selector disposition",
            ("Detach as ordinary Feature", "Remove previous selector"),
            0,
            False,
        )
        if ok:
            disposition = "detach" if label.startswith("Detach") else "remove"
            self.submit(AssignOneHotSelectorIntent(group.identity, selector, disposition))

    def change_source(self) -> None:
        group = self.selected()
        if group is None:
            return
        dialog = OneHotGroupIntentDialog(self.projection, group, self.parent)
        dialog.group_key.setEnabled(False)
        dialog.selector.setEnabled(False)
        dialog.unknown.setEnabled(False)
        dialog.missing.setEnabled(False)
        dialog.setWindowTitle("Change One-hot Source Mode")
        if not dialog.exec():
            return
        values = dialog.values()
        mode = str(values["source_mode"])
        binding = str(values["source_binding"])
        provider_categories: list[tuple[str, str]] = []
        if mode == "external" and group.categories:
            snapshot = next((item for item in self.projection.vocabulary_snapshots
                             if item.source_mode == mode and item.source_binding == binding), None)
            if snapshot is None:
                QMessageBox.warning(self.parent, "External provider unavailable",
                                    self.projection.external_disabled_reason)
                return
            labels = tuple(f"{item.label or item.value} [{item.identity}]"
                           for item in snapshot.categories)
            by_label = dict(zip(labels, snapshot.categories, strict=True))
            for category in group.categories:
                selected, ok = QInputDialog.getItem(
                    self.parent,
                    "Map provider category",
                    f"Provider category for {category.source_value}",
                    labels,
                    0,
                    False,
                )
                if not ok:
                    return
                provider_categories.append((category.identity, by_label[selected].identity))
        self.submit(ChangeOneHotSourceModeIntent(
            group.identity, mode, binding, tuple(provider_categories)
        ))

    def _choose_selector(self, title: str) -> str:
        choices = tuple(
            f"{item.label} ({item.column_key})" for item in self.projection.selectors
            if item.selectable
        )
        if not choices:
            QMessageBox.information(
                self.parent, title,
                "No unassigned compatible string selector is available. Prepare one through Feature workflow first.",
            )
            return ""
        label, ok = QInputDialog.getItem(self.parent, title, "Selector Feature", choices, 0, False)
        if not ok:
            return ""
        return next(
            item.identity for item in self.projection.selectors
            if f"{item.label} ({item.column_key})" == label
        )
