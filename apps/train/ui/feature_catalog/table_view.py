"""Spreadsheet-like Feature Catalog table view."""

from __future__ import annotations

from PySide6.QtCore import QItemSelectionModel, Qt
from PySide6.QtGui import QKeySequence
from PySide6.QtWidgets import QApplication, QAbstractItemView, QTableView

from apps.common.ui.tables.clipboard import format_tsv, parse_tsv, rectangular_bounds
from apps.common.ui.tables.undo import CellChange, TableUndoStack


class FeatureCatalogTableView(QTableView):
    """QTableView with Feature Catalog clipboard, clear, and undo behavior."""

    def __init__(self, parent: QTableView | None = None) -> None:
        super().__init__(parent)
        self.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setEditTriggers(
            QAbstractItemView.DoubleClicked
            | QAbstractItemView.EditKeyPressed
            | QAbstractItemView.SelectedClicked
        )
        self._undo_stack = TableUndoStack()

    def copy_selection_tsv(self) -> str:
        """Return the selected rectangular range as TSV."""
        model = self.model()
        if model is None or not hasattr(model, "cell_value"):
            return ""
        bounds = rectangular_bounds(self._selected_cells())
        if bounds is None:
            return ""
        top, left, bottom, right = bounds
        return format_tsv(
            [
                [model.cell_value(row, col) for col in range(left, right + 1)]
                for row in range(top, bottom + 1)
            ]
        )

    def paste_tsv_at_selection(self, text: str) -> int:
        """Paste TSV at the selection anchor, skipping locked cells."""
        model = self.model()
        anchor = self._selection_anchor()
        if model is None or anchor is None:
            return 0
        grid = self._expand_grid_for_selection(parse_tsv(text))
        if not grid:
            return 0
        changes: list[CellChange] = []
        top, left = anchor
        for row_offset, row_values in enumerate(grid):
            row = top + row_offset
            if row >= model.rowCount():
                continue
            for col_offset, value in enumerate(row_values):
                col = left + col_offset
                if col >= model.columnCount():
                    continue
                index = model.index(row, col)
                if not (model.flags(index) & Qt.ItemIsEditable):
                    continue
                old_value = model.cell_value(row, col)
                if str(old_value) == str(value):
                    continue
                if model.setData(index, value, Qt.EditRole):
                    changes.append(CellChange(row, col, old_value, value))
        self._undo_stack.push(changes)
        return len(changes)

    def clear_selection(self) -> int:
        """Clear selected editable cells as one undo group."""
        model = self.model()
        if model is None:
            return 0
        changes: list[CellChange] = []
        for row, col in self._selected_cells():
            index = model.index(row, col)
            if not (model.flags(index) & Qt.ItemIsEditable):
                continue
            old_value = model.cell_value(row, col)
            if old_value == "":
                continue
            if model.setData(index, "", Qt.EditRole):
                changes.append(CellChange(row, col, old_value, ""))
        self._undo_stack.push(changes)
        return len(changes)

    def undo(self) -> int:
        """Undo the most recent edit/paste/clear group."""
        model = self.model()
        if model is None:
            return 0
        undone = 0
        for change in reversed(self._undo_stack.pop()):
            index = model.index(change.row, change.col)
            if model.setData(index, change.old_value, Qt.EditRole):
                undone += 1
        return undone

    def clear_undo_history(self) -> None:
        """Clear table-local undo history after reload."""
        self._undo_stack.clear()

    def keyPressEvent(self, event):  # noqa: ANN001
        """Handle spreadsheet-like keyboard commands."""
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
        if event.matches(QKeySequence.Undo):
            self.undo()
            event.accept()
            return
        if event.key() in (Qt.Key_Tab, Qt.Key_Backtab):
            self._move_current_horizontal(backward=event.key() == Qt.Key_Backtab)
            event.accept()
            return
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self._move_current_vertical(backward=bool(event.modifiers() & Qt.ShiftModifier))
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

    def _expand_grid_for_selection(self, grid: list[list[str]]) -> list[list[str]]:
        bounds = rectangular_bounds(self._selected_cells())
        if bounds is None or not grid:
            return grid
        top, left, bottom, right = bounds
        selected_rows = bottom - top + 1
        selected_cols = right - left + 1
        if len(grid) == 1 and len(grid[0]) == 1:
            return [[grid[0][0] for _col in range(selected_cols)] for _row in range(selected_rows)]
        if len(grid) == 1 and len(grid[0]) == selected_cols and selected_rows > 1:
            return [list(grid[0]) for _row in range(selected_rows)]
        return grid

    def _move_current_horizontal(self, backward: bool = False) -> None:
        model = self.model()
        if model is None or model.rowCount() == 0 or model.columnCount() == 0:
            return
        current = self.currentIndex()
        row = current.row() if current.isValid() else 0
        col = current.column() if current.isValid() else 0
        step = -1 if backward else 1
        col += step
        if col >= model.columnCount():
            col = 0
            row = (row + 1) % model.rowCount()
        elif col < 0:
            col = model.columnCount() - 1
            row = (row - 1) % model.rowCount()
        self.selectionModel().setCurrentIndex(
            model.index(row, col),
            QItemSelectionModel.ClearAndSelect,
        )

    def _move_current_vertical(self, backward: bool = False) -> None:
        model = self.model()
        if model is None or model.rowCount() == 0 or model.columnCount() == 0:
            return
        current = self.currentIndex()
        row = current.row() if current.isValid() else 0
        col = current.column() if current.isValid() else 0
        step = -1 if backward else 1
        row += step
        if row >= model.rowCount():
            row = 0
            col = (col + 1) % model.columnCount()
        elif row < 0:
            row = model.rowCount() - 1
            col = (col - 1) % model.columnCount()
        self.selectionModel().setCurrentIndex(
            model.index(row, col),
            QItemSelectionModel.ClearAndSelect,
        )
