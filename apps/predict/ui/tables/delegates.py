"""Predict table delegates."""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import QEvent, QTimer, Qt
from PySide6.QtCore import QModelIndex
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QComboBox,
    QStyle,
    QStyledItemDelegate,
    QStyleOptionComboBox,
)


class DropdownDelegate(QStyledItemDelegate):
    """Render dropdown affordance and open a combo box in one click."""

    def __init__(
        self,
        items_by_column: dict[int, tuple[str, ...]],
        parent: QAbstractItemView | None = None,
        option_provider: Callable[[QModelIndex], tuple[str, ...]] | None = None,
    ) -> None:
        super().__init__(parent)
        self._items_by_column = items_by_column
        self._option_provider = option_provider

    def paint(self, painter, option, index):  # noqa: ANN001
        """Paint default cell plus a dropdown arrow affordance."""
        super().paint(painter, option, index)
        if index.column() not in self._items_by_column:
            return
        combo_option = QStyleOptionComboBox()
        combo_option.rect = option.rect
        combo_option.state = option.state | QStyle.State_Enabled
        combo_option.subControls = QStyle.SC_ComboBoxArrow
        QApplication.style().drawComplexControl(
            QStyle.CC_ComboBox,
            combo_option,
            painter,
        )

    def createEditor(self, parent, option, index):  # noqa: ANN001
        """Create a combo box for dropdown-capable columns."""
        items = self._items_for_index(index)
        if items is None:
            return super().createEditor(parent, option, index)
        combo = QComboBox(parent)
        combo.addItems(items)
        QTimer.singleShot(0, combo.showPopup)
        return combo

    def setEditorData(self, editor, index):  # noqa: ANN001
        """Set combo selection from current cell text."""
        if isinstance(editor, QComboBox):
            current = str(index.data(Qt.DisplayRole) or "")
            found = editor.findText(current)
            if found >= 0:
                editor.setCurrentIndex(found)
            return
        super().setEditorData(editor, index)

    def setModelData(self, editor, model, index):  # noqa: ANN001
        """Commit combo selection back to the model."""
        if isinstance(editor, QComboBox):
            model.setData(index, editor.currentText(), Qt.EditRole)
            return
        super().setModelData(editor, model, index)

    def editorEvent(self, event, model, option, index):  # noqa: ANN001
        """Enter edit mode on one click for dropdown cells."""
        if (
            index.column() in self._items_by_column
            and event.type() == QEvent.MouseButtonRelease
            and isinstance(self.parent(), QAbstractItemView)
        ):
            self.parent().edit(index)
            return True
        return super().editorEvent(event, model, option, index)

    def _items_for_index(self, index: QModelIndex) -> tuple[str, ...] | None:
        if index.column() not in self._items_by_column:
            return None
        if self._option_provider is not None:
            provided = self._option_provider(index)
            if provided:
                return provided
        return self._items_by_column.get(index.column(), ())
