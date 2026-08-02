"""Read-only full-row interaction for Result Review."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence
from PySide6.QtWidgets import QApplication, QAbstractItemView, QTableView


class ResultReviewTableView(QTableView):
    """Select and copy complete review rows in canonical session order."""

    def __init__(self, parent: QTableView | None = None) -> None:
        super().__init__(parent)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setWordWrap(False)
        self.setTextElideMode(Qt.ElideRight)

    def selected_row_indexes(self) -> list[int]:
        selection = self.selectionModel()
        if selection is None:
            return []
        return sorted({index.row() for index in selection.selectedRows()})

    def copy_selected_rows_tsv(self) -> str:
        model = self.model()
        if model is None or not hasattr(model, "copy_rows_tsv"):
            return ""
        return model.copy_rows_tsv(self.selected_row_indexes())

    def copy_selected_rows_to_clipboard(self) -> bool:
        text = self.copy_selected_rows_tsv()
        if not text:
            return False
        QApplication.clipboard().setText(text)
        return True

    def keyPressEvent(self, event):  # noqa: ANN001
        if event.matches(QKeySequence.Copy):
            self.copy_selected_rows_to_clipboard()
            event.accept()
            return
        super().keyPressEvent(event)
