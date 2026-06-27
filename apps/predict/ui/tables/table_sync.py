"""Input/result table synchronization helpers."""

from PySide6.QtCore import QItemSelection, QItemSelectionModel
from PySide6.QtWidgets import QTableView


class TableSelectionScrollSync:
    """Synchronize row selection and vertical scroll between two tables."""

    def __init__(self, input_table: QTableView, result_table: QTableView) -> None:
        self._input_table = input_table
        self._result_table = result_table
        self._syncing_scroll = False
        self._syncing_selection = False

        input_table.verticalScrollBar().valueChanged.connect(
            self._sync_result_scroll
        )
        result_table.verticalScrollBar().valueChanged.connect(
            self._sync_input_scroll
        )
        input_table.selectionModel().selectionChanged.connect(
            self._sync_result_selection
        )
        result_table.selectionModel().selectionChanged.connect(
            self._sync_input_selection
        )

    def sync_row_heights(self) -> None:
        """Mirror input row heights to the result table for current rows."""
        row_count = min(
            self._input_table.model().rowCount(),
            self._result_table.model().rowCount(),
        )
        for row in range(row_count):
            self._result_table.setRowHeight(row, self._input_table.rowHeight(row))

    def _sync_result_scroll(self, value: int) -> None:
        if self._syncing_scroll:
            return
        self._syncing_scroll = True
        try:
            self._result_table.verticalScrollBar().setValue(value)
        finally:
            self._syncing_scroll = False

    def _sync_input_scroll(self, value: int) -> None:
        if self._syncing_scroll:
            return
        self._syncing_scroll = True
        try:
            self._input_table.verticalScrollBar().setValue(value)
        finally:
            self._syncing_scroll = False

    def _sync_result_selection(
        self,
        selected: QItemSelection,
        _deselected: QItemSelection,
    ) -> None:
        if self._syncing_selection:
            return
        self._syncing_selection = True
        try:
            self._apply_row_selection(self._result_table, selected)
        finally:
            self._syncing_selection = False

    def _sync_input_selection(
        self,
        selected: QItemSelection,
        _deselected: QItemSelection,
    ) -> None:
        if self._syncing_selection:
            return
        self._syncing_selection = True
        try:
            self._apply_row_selection(self._input_table, selected)
        finally:
            self._syncing_selection = False

    def _apply_row_selection(self, target: QTableView, selected: QItemSelection) -> None:
        selection_model = target.selectionModel()
        selection_model.clearSelection()
        for source_index in selected.indexes():
            target_index = target.model().index(source_index.row(), 0)
            selection_model.select(
                target_index,
                QItemSelectionModel.Select | QItemSelectionModel.Rows,
            )
