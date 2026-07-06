"""Qt table models for Data Mapping Manager rows."""

from __future__ import annotations

from collections.abc import Callable, Sequence
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
        if not self._has_cell(index):
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
            if not 0 <= section < len(self._headers):
                return None
            return self._headers[section]
        if orientation == Qt.Vertical:
            if not 0 <= section < len(self._rows):
                return None
            return section + 1
        return None

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        if not self._has_cell(index):
            return Qt.NoItemFlags
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def cell_value(self, row: int, column: int) -> str | None:
        """Return a safe cell value for tests and future copy/export paths."""
        if not self._is_cell_in_range(row, column):
            return None
        return str(self._rows[row][column])

    def _has_cell(self, index: QModelIndex) -> bool:
        if not index.isValid():
            return False
        return self._is_cell_in_range(index.row(), index.column())

    def _is_cell_in_range(self, row: int, column: int) -> bool:
        return (
            0 <= row < len(self._rows)
            and 0 <= column < len(self._headers)
            and column < len(self._rows[row])
        )


class EditableMappingTableModel(ReadOnlyMappingTableModel):
    """Editable table model for Data Mapping draft rows."""

    def __init__(
        self,
        headers: Sequence[str] = (),
        rows: Sequence[Sequence[object]] = (),
        *,
        on_cell_changed: Callable[[int, str, object], bool] | None = None,
    ) -> None:
        super().__init__(headers, rows)
        self._on_cell_changed = on_cell_changed

    def setData(
        self,
        index: QModelIndex,
        value: Any,
        role: int = Qt.EditRole,
    ) -> bool:
        if role != Qt.EditRole or not self._has_cell(index):
            return False
        header = self._headers[index.column()]
        if self._on_cell_changed is None:
            return False
        accepted = self._on_cell_changed(index.row(), header, value)
        if accepted:
            self.dataChanged.emit(index, index, [Qt.DisplayRole, Qt.EditRole])
        return accepted

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        if not self._has_cell(index):
            return Qt.NoItemFlags
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable
