"""Input Cases table view."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence
from PySide6.QtWidgets import QApplication, QAbstractItemView, QTableView

from apps.predict.ui.tables.clipboard import format_tsv, parse_tsv, rectangular_bounds


class InputTableView(QTableView):
    """QTableView configured for editable input cases."""

    def __init__(self, parent: QTableView | None = None) -> None:
        super().__init__(parent)
        self.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setEditTriggers(
            QAbstractItemView.DoubleClicked
            | QAbstractItemView.EditKeyPressed
            | QAbstractItemView.SelectedClicked
        )

    def copy_selection_tsv(self) -> str:
        """Return selected cells as TSV."""
        model = self.model()
        if model is None or not hasattr(model, "cell_value"):
            return ""
        cells = self._selected_cells()
        bounds = rectangular_bounds(cells)
        if bounds is None:
            return ""
        top, left, bottom, right = bounds
        grid = [
            [model.cell_value(row, col) for col in range(left, right + 1)]
            for row in range(top, bottom + 1)
        ]
        return format_tsv(grid)

    def paste_tsv_at_selection(self, text: str) -> int:
        """Paste TSV at the current selection anchor."""
        model = self.model()
        if model is None or not hasattr(model, "setData"):
            return 0
        anchor = self._selection_anchor()
        if anchor is None:
            return 0
        grid = parse_tsv(text)
        if not grid:
            return 0
        top, left = anchor
        changed = 0
        for r_offset, row_values in enumerate(grid):
            row = top + r_offset
            if row >= model.rowCount():
                continue
            for c_offset, value in enumerate(row_values):
                col = left + c_offset
                if col >= model.columnCount():
                    continue
                index = model.index(row, col)
                if not (model.flags(index) & Qt.ItemIsEditable):
                    continue
                if model.setData(index, value, Qt.EditRole):
                    changed += 1
        return changed

    def clear_selection(self) -> int:
        """Clear selected editable cells."""
        model = self.model()
        if model is None or not hasattr(model, "clear_cells"):
            return 0
        return model.clear_cells(self._selected_cells())

    def keyPressEvent(self, event):  # noqa: ANN001
        """Handle spreadsheet-like clipboard and clear shortcuts."""
        if event.matches(QKeySequence.Copy):
            QApplication.clipboard().setText(self.copy_selection_tsv())
            event.accept()
            return
        if event.matches(QKeySequence.Paste):
            self.paste_tsv_at_selection(QApplication.clipboard().text())
            event.accept()
            return
        if event.key() in (Qt.Key_Delete, Qt.Key_Backspace):
            self.clear_selection()
            event.accept()
            return
        super().keyPressEvent(event)

    def _selected_cells(self) -> list[tuple[int, int]]:
        indexes = self.selectionModel().selectedIndexes() if self.selectionModel() else []
        return sorted({(index.row(), index.column()) for index in indexes})

    def _selection_anchor(self) -> tuple[int, int] | None:
        cells = self._selected_cells()
        if cells:
            bounds = rectangular_bounds(cells)
            if bounds is None:
                return None
            top, left, _bottom, _right = bounds
            return top, left
        current = self.currentIndex()
        if current.isValid():
            return current.row(), current.column()
        return None
