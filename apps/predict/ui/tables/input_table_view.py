"""Input Cases table view."""

from PySide6.QtWidgets import QAbstractItemView, QTableView


class InputTableView(QTableView):
    """QTableView configured for editable input cases."""

    def __init__(self, parent: QTableView | None = None) -> None:
        super().__init__(parent)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
