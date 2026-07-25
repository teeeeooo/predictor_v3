"""Read-only table model for Trainer placeholder/status tables."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt


class StaticTableModel(QAbstractTableModel):
    """Small read-only table model backed by header and row tuples."""

    def __init__(
        self,
        headers: Sequence[str],
        rows: Sequence[Sequence[object]],
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
        row, column = index.row(), index.column()
        if (
            row < 0
            or row >= len(self._rows)
            or column < 0
            or column >= len(self._headers)
            or column >= len(self._rows[row])
        ):
            return None
        if role == Qt.DisplayRole:
            return str(self._rows[row][column])
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
            if 0 <= section < len(self._headers):
                return self._headers[section]
            return None
        if 0 <= section < len(self._rows):
            return section + 1
        return None

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        if not index.isValid():
            return Qt.NoItemFlags
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable
