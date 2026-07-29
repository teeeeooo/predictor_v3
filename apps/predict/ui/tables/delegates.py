"""Predict table delegates."""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import Qt
from PySide6.QtCore import QModelIndex
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QComboBox,
    QCompleter,
    QStyle,
    QStyledItemDelegate,
    QStyleOptionComboBox,
    QStyleOptionViewItem,
)


class DropdownDelegate(QStyledItemDelegate):
    """Render dropdown affordance and provide editable combo editors."""

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
        if index.column() not in self._items_by_column:
            super().paint(painter, option, index)
            return
        style = (
            option.widget.style()
            if option.widget is not None
            else QApplication.style()
        )
        view_option = QStyleOptionViewItem(option)
        self.initStyleOption(view_option, index)
        combo_option = QStyleOptionComboBox()
        combo_option.rect = option.rect
        combo_option.state = option.state
        combo_option.direction = option.direction
        combo_option.palette = option.palette
        combo_option.subControls = QStyle.SC_ComboBoxArrow
        arrow_rect = style.subControlRect(
            QStyle.CC_ComboBox,
            combo_option,
            QStyle.SC_ComboBoxArrow,
            option.widget,
        )

        background_option = QStyleOptionViewItem(view_option)
        background_option.text = ""
        style.drawControl(
            QStyle.CE_ItemViewItem,
            background_option,
            painter,
            option.widget,
        )

        text_rect = option.rect.adjusted(0, 0, 0, 0)
        if option.direction == Qt.RightToLeft:
            text_rect.setLeft(arrow_rect.right() + 1)
        else:
            text_rect.setRight(arrow_rect.left() - 1)
        painter.save()
        painter.setClipRect(text_rect)
        style.drawControl(
            QStyle.CE_ItemViewItem,
            view_option,
            painter,
            option.widget,
        )
        painter.restore()

        arrow_option = QStyleOptionComboBox(combo_option)
        arrow_option.rect = arrow_rect
        style.drawPrimitive(
            QStyle.PE_IndicatorArrowDown,
            arrow_option,
            painter,
            option.widget,
        )

    def createEditor(self, parent, option, index):  # noqa: ANN001
        """Create a combo box for dropdown-capable columns."""
        items = self._items_for_index(index)
        if items is None:
            return super().createEditor(parent, option, index)
        combo = QComboBox(parent)
        combo.setEditable(True)
        combo.setInsertPolicy(QComboBox.NoInsert)
        combo.addItems(items)
        completer = QCompleter(list(items), combo)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setCompletionMode(QCompleter.PopupCompletion)
        combo.setCompleter(completer)
        return combo

    def setEditorData(self, editor, index):  # noqa: ANN001
        """Set combo selection from current cell text."""
        if isinstance(editor, QComboBox):
            current = str(index.data(Qt.DisplayRole) or "")
            found = editor.findText(current)
            if found >= 0:
                editor.setCurrentIndex(found)
            else:
                editor.setEditText(current)
            return
        super().setEditorData(editor, index)

    def setModelData(self, editor, model, index):  # noqa: ANN001
        """Commit combo selection back to the model."""
        if isinstance(editor, QComboBox):
            model.setData(index, editor.currentText(), Qt.EditRole)
            return
        super().setModelData(editor, model, index)

    def _items_for_index(self, index: QModelIndex) -> tuple[str, ...] | None:
        if index.column() not in self._items_by_column:
            return None
        if self._option_provider is not None:
            provided = self._option_provider(index)
            if provided:
                return provided
        return self._items_by_column.get(index.column(), ())
