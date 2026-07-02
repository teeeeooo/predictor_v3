"""Prediction Results table view."""

from PySide6.QtGui import QKeySequence
from PySide6.QtWidgets import QApplication, QAbstractItemView, QTableView

from apps.common.ui.tables.clipboard import format_tsv, rectangular_bounds


class ResultTableView(QTableView):
    """QTableView configured for read-only prediction results."""

    def __init__(self, parent: QTableView | None = None) -> None:
        super().__init__(parent)
        self.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)

    def copy_selection_tsv(self) -> str:
        """Return selected result cells as TSV."""
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

    def keyPressEvent(self, event):  # noqa: ANN001
        """Handle result copy shortcut."""
        if event.matches(QKeySequence.Copy):
            QApplication.clipboard().setText(self.copy_selection_tsv())
            event.accept()
            return
        super().keyPressEvent(event)

    def _selected_cells(self) -> list[tuple[int, int]]:
        indexes = self.selectionModel().selectedIndexes() if self.selectionModel() else []
        return sorted({(index.row(), index.column()) for index in indexes})
