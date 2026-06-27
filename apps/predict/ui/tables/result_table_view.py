"""Prediction Results table view."""

from PySide6.QtWidgets import QAbstractItemView, QTableView


class ResultTableView(QTableView):
    """QTableView configured for read-only prediction results."""

    def __init__(self, parent: QTableView | None = None) -> None:
        super().__init__(parent)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
