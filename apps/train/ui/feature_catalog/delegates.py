"""Feature Catalog table delegates."""

from __future__ import annotations

from PySide6.QtCore import QRect, QTimer, Qt
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QCompleter,
    QStyle,
    QStyleOption,
    QStyledItemDelegate,
)


class FeatureCatalogDropdownDelegate(QStyledItemDelegate):
    """Render dropdown affordances and editors for catalog allowlist fields."""

    def paint(self, painter, option, index):  # noqa: ANN001
        """Paint the default cell plus a dropdown arrow when options exist."""
        super().paint(painter, option, index)
        if not _options_for(index):
            return
        arrow_option = QStyleOption(option)
        arrow_width = QApplication.style().pixelMetric(QStyle.PM_ScrollBarExtent)
        arrow_option.rect = QRect(
            option.rect.right() - arrow_width,
            option.rect.top(),
            arrow_width,
            option.rect.height(),
        )
        arrow_option.state = option.state | QStyle.State_Enabled
        QApplication.style().drawPrimitive(QStyle.PE_IndicatorArrowDown, arrow_option, painter)

    def createEditor(self, parent, option, index):  # noqa: ANN001
        """Create a combo editor for dropdown-capable cells."""
        options = _options_for(index)
        if not options:
            return super().createEditor(parent, option, index)
        combo = QComboBox(parent)
        combo.setEditable(True)
        combo.setInsertPolicy(QComboBox.NoInsert)
        combo.addItems(options)
        completer = QCompleter(list(options), combo)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setCompletionMode(QCompleter.PopupCompletion)
        combo.setCompleter(completer)
        combo.activated.connect(lambda _index, editor=combo: self._commit_and_close(editor))
        QTimer.singleShot(0, combo.showPopup)
        return combo

    def setEditorData(self, editor, index):  # noqa: ANN001
        """Set editor text from the current cell value."""
        if isinstance(editor, QComboBox):
            current = str(index.data(Qt.EditRole) or "")
            found = editor.findText(current)
            if found >= 0:
                editor.setCurrentIndex(found)
            else:
                editor.setEditText(current)
            return
        super().setEditorData(editor, index)

    def setModelData(self, editor, model, index):  # noqa: ANN001
        """Commit editor text back to the model."""
        if isinstance(editor, QComboBox):
            model.setData(index, editor.currentText(), Qt.EditRole)
            return
        super().setModelData(editor, model, index)

    def _commit_and_close(self, editor: QComboBox) -> None:
        self.commitData.emit(editor)
        self.closeEditor.emit(editor, QStyledItemDelegate.NoHint)


def _options_for(index) -> tuple[str, ...]:  # noqa: ANN001
    model = index.model()
    if model is None or not hasattr(model, "dropdown_options"):
        return ()
    return model.dropdown_options(index.row(), index.column())
