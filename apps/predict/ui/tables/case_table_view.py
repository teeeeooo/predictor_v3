"""Unified Predict case table view."""

from collections.abc import Callable
from dataclasses import dataclass

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence
from PySide6.QtWidgets import QApplication, QAbstractItemView, QTableView
from PySide6.QtCore import QItemSelectionModel

from apps.common.ui.tables.clipboard import format_tsv, rectangular_bounds
from apps.common.ui.tables.undo import CellChange


PasteHandler = Callable[[str, int, int, int, int], int]
UndoHandler = Callable[[], int]
ReauthorizeHandler = Callable[[], bool]


@dataclass(frozen=True)
class _CompoundUndo:
    execute: UndoHandler
    reauthorize: ReauthorizeHandler | None = None


class CaseTableView(QTableView):
    """QTableView configured for unified case-table interactions."""

    def __init__(self, parent: QTableView | None = None) -> None:
        super().__init__(parent)
        self.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setEditTriggers(
            QAbstractItemView.DoubleClicked
            | QAbstractItemView.EditKeyPressed
        )
        self._undo_stack: list[tuple[CellChange, ...] | _CompoundUndo] = []
        self._paste_handler: PasteHandler | None = None
        self._press_started_on_selected_current = False

    def copy_selection_tsv(self) -> str:
        """Return selected visible cells as TSV."""
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
        """Route a complete TSV payload to the Predict transaction owner."""
        if self._paste_handler is None:
            return 0
        bounds = self._selection_bounds()
        if bounds is None:
            return 0
        return self._paste_handler(text, *bounds)

    def set_paste_handler(self, handler: PasteHandler | None) -> None:
        """Bind the one production bulk-paste entry owner."""
        self._paste_handler = handler

    def register_compound_undo(
        self,
        handler: UndoHandler,
        reauthorize: ReauthorizeHandler | None = None,
    ) -> None:
        """Place one application-owned transaction in table undo chronology."""
        self._push_undo(_CompoundUndo(handler, reauthorize))

    def clear_selection(self) -> int:
        """Clear selected editable cells."""
        model = self.model()
        if model is None or not hasattr(model, "setData"):
            return 0
        changes: list[CellChange] = []
        for row, col in self._selected_cells():
            index = model.index(row, col)
            if not (model.flags(index) & Qt.ItemIsEditable):
                continue
            old_value = model.cell_value(row, col)
            if str(old_value or "") == "":
                continue
            if model.setData(index, "", Qt.EditRole):
                changes.append(CellChange(row, col, old_value, ""))
        self._push_undo(tuple(changes))
        return len(changes)

    def replace_current_cell(self, text: str) -> bool:
        """Replace the active editable cell with text as one undoable edit."""
        model = self.model()
        index = self.currentIndex()
        if model is None or not index.isValid():
            return False
        if not (model.flags(index) & Qt.ItemIsEditable):
            return False
        old_value = model.cell_value(index.row(), index.column())
        if str(old_value or "") == text:
            return True
        if not model.setData(index, text, Qt.EditRole):
            return False
        self._push_undo(
            (CellChange(index.row(), index.column(), old_value, text),)
        )
        if self.isVisible():
            self.edit(index)
        return True

    def undo(self) -> int:
        """Undo the most recent grouped edit/paste/clear action."""
        model = self.model()
        if model is None:
            return 0
        if not self._undo_stack:
            return 0
        changes = self._undo_stack.pop()
        if isinstance(changes, _CompoundUndo):
            undone = changes.execute()
            if undone:
                self._reauthorize_top_compound()
            return undone
        undone = 0
        for change in reversed(changes):
            index = model.index(change.row, change.col)
            if model.setData(index, change.old_value, Qt.EditRole):
                undone += 1
        if undone == len(changes):
            self._reauthorize_top_compound()
        return undone

    def clear_undo_history(self) -> None:
        """Clear table-local undo history after a data context reset."""
        self._undo_stack.clear()

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
        if event.key() == Qt.Key_F2:
            index = self.currentIndex()
            if index.isValid():
                self.edit(index)
                event.accept()
                return
        if self._is_printable_replace_event(event):
            if self.replace_current_cell(event.text()):
                event.accept()
                return
        super().keyPressEvent(event)

    def mousePressEvent(self, event):  # noqa: ANN001
        """Remember whether a click began on the already active selected cell."""
        index = self.indexAt(event.position().toPoint())
        self._press_started_on_selected_current = (
            index.isValid()
            and index == self.currentIndex()
            and self.selectionModel() is not None
            and self.selectionModel().isSelected(index)
        )
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):  # noqa: ANN001
        """Keep first click as selection and same-cell click as edit entry."""
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

    def _selected_cells(self) -> list[tuple[int, int]]:
        indexes = self.selectionModel().selectedIndexes() if self.selectionModel() else []
        return sorted({(index.row(), index.column()) for index in indexes})

    def _selection_bounds(self) -> tuple[int, int, int, int] | None:
        cells = self._selected_cells()
        if cells:
            bounds = rectangular_bounds(cells)
            if bounds is None:
                return None
            return bounds
        current = self.currentIndex()
        if current.isValid():
            return current.row(), current.column(), current.row(), current.column()
        return None

    def _push_undo(
        self, action: tuple[CellChange, ...] | _CompoundUndo
    ) -> None:
        if isinstance(action, tuple) and not action:
            return
        self._undo_stack.append(action)
        if len(self._undo_stack) > 64:
            del self._undo_stack[0]

    def _reauthorize_top_compound(self) -> None:
        if not self._undo_stack:
            return
        action = self._undo_stack[-1]
        if isinstance(action, _CompoundUndo) and action.reauthorize is not None:
            action.reauthorize()

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

    def _is_printable_replace_event(self, event) -> bool:  # noqa: ANN001
        text = event.text()
        if not text or not text.isprintable():
            return False
        blocked_modifiers = Qt.ControlModifier | Qt.AltModifier | Qt.MetaModifier
        return not bool(event.modifiers() & blocked_modifiers)
