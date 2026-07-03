"""Read-only Qt table models for Data Mapping UI foundation."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt


class ReadOnlyMappingTableModel(QAbstractTableModel):
    """Small read-only table model for Data Mapping view state rows."""

    def __init__(
        self,
        headers: Sequence[str] = (),
        rows: Sequence[Sequence[object]] = (),
    ) -> None:
        super().__init__()
        self._headers = tuple(headers)
        self._rows = tuple(tuple(row) for row in rows)

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent.isValid():
            return 0
        return len(self._rows)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent.isValid():
            return 0
        return len(self._headers)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        if not index.isValid():
            return None
        if role in (Qt.DisplayRole, Qt.EditRole):
            return str(self._rows[index.row()][index.column()])
        if role == Qt.TextAlignmentRole:
            return Qt.AlignCenter
        return None

    def headerData(
        self,
        section: int,
        orientation: Qt.Orientation,
        role: int = Qt.DisplayRole,
    ) -> Any:
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            return self._headers[section]
        return section + 1

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        if not index.isValid():
            return Qt.NoItemFlags
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def cell_value(self, row: int, column: int) -> str:
        """Return a safe cell value for tests and future copy/export paths."""
        if not (0 <= row < self.rowCount() and 0 <= column < self.columnCount()):
            return ""
        return str(self._rows[row][column])
