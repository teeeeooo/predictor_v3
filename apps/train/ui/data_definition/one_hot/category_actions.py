"""View-side One-hot category intent collection."""

from __future__ import annotations

from PySide6.QtWidgets import QInputDialog, QWidget

from apps.train.ui.data_definition.one_hot.intent_dialogs import OneHotCategoryIntentDialog
from core.data_definition import (
    AddOneHotCategoryIntent,
    DuplicateOneHotCategoryIntent,
    EditOneHotCategoryIntent,
    MoveOneHotCategoryIntent,
    RemoveOneHotCategoryIntent,
    RenameOneHotEmittedFeatureIntent,
    SetOneHotCategoryActiveIntent,
)


class OneHotCategoryActions:
    def __init__(self, selected_group, selected_category, projection, submit, parent: QWidget):  # noqa: ANN001
        self.selected_group = selected_group
        self.selected_category = selected_category
        self.projection = projection
        self.submit = submit
        self.parent = parent

    def update_projection(self, projection) -> None:  # noqa: ANN001
        self.projection = projection

    def add(self) -> None:
        group = self.selected_group()
        if group is None:
            return
        dialog = OneHotCategoryIntentDialog(
            group, self.projection.vocabulary_snapshots, parent=self.parent
        )
        if dialog.exec():
            values = dialog.values()
            values.pop("active")
            self.submit(AddOneHotCategoryIntent(group.identity, **values, active=False))

    def edit(self) -> None:
        group, category = self._selection()
        if category is None:
            return
        dialog = OneHotCategoryIntentDialog(
            group, self.projection.vocabulary_snapshots, category, self.parent
        )
        if dialog.exec():
            self.submit(EditOneHotCategoryIntent(category.identity, **dialog.values()))

    def rename(self) -> None:
        _group, category = self._selection()
        if category is None:
            return
        value, ok = QInputDialog.getText(
            self.parent, "Rename emitted ML Feature", "Emitted ML name",
            text=category.emitted_ml_name,
        )
        if ok:
            self.submit(RenameOneHotEmittedFeatureIntent(category.identity, value))

    def duplicate(self) -> None:
        group, category = self._selection()
        if category is None:
            return
        dialog = OneHotCategoryIntentDialog(
            group, self.projection.vocabulary_snapshots, category, self.parent
        )
        dialog.setWindowTitle("Duplicate One-hot Category")
        dialog.active.setChecked(False)
        dialog.active.setEnabled(False)
        if dialog.exec():
            values = dialog.values()
            values.pop("active")
            self.submit(DuplicateOneHotCategoryIntent(category.identity, **values))

    def remove(self) -> None:
        _group, category = self._selection()
        if category is not None:
            self.submit(RemoveOneHotCategoryIntent(category.identity))

    def toggle_active(self) -> None:
        _group, category = self._selection()
        if category is not None:
            self.submit(SetOneHotCategoryActiveIntent(category.identity, not category.active))

    def move(self, direction: str) -> None:
        _group, category = self._selection()
        if category is not None:
            self.submit(MoveOneHotCategoryIntent(category.identity, direction))

    def _selection(self):  # noqa: ANN202
        return self.selected_group(), self.selected_category()
