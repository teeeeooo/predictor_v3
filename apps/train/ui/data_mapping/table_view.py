"""Spreadsheet interaction owner for the Data Mapping primary table."""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import QItemSelectionModel, Qt
from PySide6.QtGui import QKeySequence
from PySide6.QtWidgets import QApplication, QAbstractItemView, QTableView

from apps.common.ui.tables.clipboard import format_tsv, parse_tsv, rectangular_bounds
from apps.train.controllers.data_mapping_controller import DataMappingControllerState
from apps.train.services.data_mapping_types import DataMappingCellEdit

BatchEditCallback = Callable[[tuple[DataMappingCellEdit, ...]], DataMappingControllerState]
UndoCallback = Callable[[], DataMappingControllerState]


class DataMappingTableView(QTableView):
    """QTableView with bounded spreadsheet behavior for visible mapping cells."""

    def __init__(self, parent: QTableView | None = None) -> None:
        super().__init__(parent)
        self.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.EditKeyPressed)
        self._batch_edit_callback: BatchEditCallback | None = None
        self._undo_callback: UndoCallback | None = None
        self._press_started_on_selected_current = False

    def bind_interactions(
        self,
        *,
        batch_edit: BatchEditCallback,
        undo: UndoCallback,
    ) -> None:
        """Bind application intents without owning a shadow draft."""
        self._batch_edit_callback = batch_edit
        self._undo_callback = undo

    def copy_selection_tsv(self) -> str:
        """Return the selected visible rectangle as TSV."""
        model = self.model()
        bounds = rectangular_bounds(self._selected_cells())
        if model is None or bounds is None or not hasattr(model, "cell_value"):
            return ""
        top, left, bottom, right = bounds
        return format_tsv(
            [
                [model.cell_value(row, col) for col in range(left, right + 1)]
                for row in range(top, bottom + 1)
            ]
        )

    def paste_tsv_at_selection(self, text: str) -> int:
        """Paste one TSV rectangle from the current top-left anchor."""
        model = self.model()
        anchor = self._selection_anchor()
        if model is None or anchor is None or self._batch_edit_callback is None:
            return 0
        grid = parse_tsv(text)
        if not grid:
            return 0
        grid = self._expand_grid_for_selection(grid)
        edits = self._edits_for_grid(anchor, grid)
        if not edits:
            return 0
        return self._batch_edit_callback(edits).operation_applied

    def clear_selection(self) -> int:
        """Clear the selected rectangle as one service-owned command."""
        model = self.model()
        if model is None or self._batch_edit_callback is None:
            return 0
        edits = tuple(
            DataMappingCellEdit(row, model.header_for_column(col), "")
            for row, col in self._selected_cells()
            if hasattr(model, "header_for_column")
        )
        if not edits:
            return 0
        return self._batch_edit_callback(edits).operation_applied

    def replace_current_cell(self, text: str) -> bool:
        """Replace the active cell as one application command."""
        model = self.model()
        index = self.currentIndex()
        if (
            model is None
            or not index.isValid()
            or self._batch_edit_callback is None
            or not (model.flags(index) & Qt.ItemIsEditable)
        ):
            return False
        state = self._batch_edit_callback(
            (DataMappingCellEdit(index.row(), model.header_for_column(index.column()), text),)
        )
        return bool(state.operation_applied)

    def undo(self) -> int:
        """Undo the most recent service-owned mapping command."""
        if self._undo_callback is None:
            return 0
        return self._undo_callback().operation_applied

    def keyPressEvent(self, event):  # noqa: ANN001
        if event.matches(QKeySequence.Copy):
            QApplication.clipboard().setText(self.copy_selection_tsv())
            event.accept()
            return
        if event.matches(QKeySequence.Paste):
            self.paste_tsv_at_selection(QApplication.clipboard().text())
            event.accept()
            return
        if event.matches(QKeySequence.Undo):
            self.undo()
            event.accept()
            return
        if event.key() in (Qt.Key_Delete, Qt.Key_Backspace):
            self.clear_selection()
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
        if event.key() == Qt.Key_F2 and self.currentIndex().isValid():
            self.edit(self.currentIndex())
            event.accept()
            return
        if self._is_printable_replace_event(event) and self.replace_current_cell(event.text()):
            if self.currentIndex().isValid() and self.isVisible():
                self.edit(self.currentIndex())
            event.accept()
            return
        super().keyPressEvent(event)

    def mousePressEvent(self, event):  # noqa: ANN001
        index = self.indexAt(event.position().toPoint())
        selection = self.selectionModel()
        self._press_started_on_selected_current = bool(
            index.isValid()
            and index == self.currentIndex()
            and selection is not None
            and selection.isSelected(index)
        )
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):  # noqa: ANN001
        index = self.indexAt(event.position().toPoint())
        should_edit = self._press_started_on_selected_current
        self._press_started_on_selected_current = False
        super().mouseReleaseEvent(event)
        if (
            event.button() == Qt.LeftButton
            and should_edit
            and index.isValid()
            and self.model() is not None
            and self.model().flags(index) & Qt.ItemIsEditable
        ):
            self.edit(index)
            event.accept()

    def _edits_for_grid(
        self,
        anchor: tuple[int, int],
        grid: list[list[str]],
    ) -> tuple[DataMappingCellEdit, ...]:
        model = self.model()
        if model is None or not hasattr(model, "header_for_column"):
            return ()
        top, left = anchor
        edits: list[DataMappingCellEdit] = []
        for row_offset, values in enumerate(grid):
            row = top + row_offset
            if row >= model.rowCount():
                continue
            for col_offset, value in enumerate(values):
                col = left + col_offset
                if col >= model.columnCount():
                    continue
                edits.append(DataMappingCellEdit(row, model.header_for_column(col), value))
        return tuple(edits)

    def _selected_cells(self) -> list[tuple[int, int]]:
        selection = self.selectionModel()
        indexes = selection.selectedIndexes() if selection is not None else []
        return sorted({(index.row(), index.column()) for index in indexes})

    def _selection_anchor(self) -> tuple[int, int] | None:
        bounds = rectangular_bounds(self._selected_cells())
        if bounds is not None:
            return bounds[0], bounds[1]
        current = self.currentIndex()
        return (current.row(), current.column()) if current.isValid() else None

    def _expand_grid_for_selection(self, grid: list[list[str]]) -> list[list[str]]:
        bounds = rectangular_bounds(self._selected_cells())
        if bounds is None:
            return grid
        top, left, bottom, right = bounds
        rows = bottom - top + 1
        columns = right - left + 1
        if len(grid) == 1 and len(grid[0]) == 1:
            return [[grid[0][0] for _column in range(columns)] for _row in range(rows)]
        if len(grid) == 1 and len(grid[0]) == columns and rows > 1:
            return [list(grid[0]) for _row in range(rows)]
        return grid

    def _move_current_horizontal(self, *, backward: bool) -> None:
        model = self.model()
        if model is None or not model.rowCount() or not model.columnCount():
            return
        current = self.currentIndex()
        start_row = current.row() if current.isValid() else 0
        start_col = current.column() if current.isValid() else 0
        total = model.rowCount() * model.columnCount()
        position = start_row * model.columnCount() + start_col
        step = -1 if backward else 1
        for _attempt in range(total):
            position = (position + step) % total
            row, col = divmod(position, model.columnCount())
            index = model.index(row, col)
            if model.flags(index) & Qt.ItemIsEditable:
                self._set_current(index)
                return

    def _move_current_vertical(self, *, backward: bool) -> None:
        model = self.model()
        if model is None or not model.rowCount() or not model.columnCount():
            return
        current = self.currentIndex()
        row = current.row() if current.isValid() else 0
        col = current.column() if current.isValid() else 0
        row = (row + (-1 if backward else 1)) % model.rowCount()
        self._set_current(model.index(row, col))

    def _set_current(self, index) -> None:  # noqa: ANN001
        selection = self.selectionModel()
        if selection is not None:
            selection.setCurrentIndex(index, QItemSelectionModel.ClearAndSelect)
            self.scrollTo(index)

    @staticmethod
    def _is_printable_replace_event(event) -> bool:  # noqa: ANN001
        text = event.text()
        if not text or not text.isprintable():
            return False
        blocked = Qt.ControlModifier | Qt.AltModifier | Qt.MetaModifier
        return not bool(event.modifiers() & blocked)
