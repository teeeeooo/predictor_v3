"""Read-only Feature Catalog table model."""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt

from apps.train.application.feature_catalog import FeatureCatalogSnapshot


class FeatureCatalogTableModel(QAbstractTableModel):
    """QAbstractTableModel backed by a Feature Catalog snapshot."""

    def __init__(self, snapshot: FeatureCatalogSnapshot | None = None) -> None:
        super().__init__()
        self._snapshot = snapshot

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent.isValid() or self._snapshot is None:
            return 0
        return self._snapshot.row_count

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent.isValid() or self._snapshot is None:
            return 0
        return len(self._snapshot.headers)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        if not index.isValid() or self._snapshot is None:
            return None
        if role not in (Qt.DisplayRole, Qt.EditRole):
            return None
        return self._snapshot.rows[index.row()].value_at(index.column())

    def headerData(
        self,
        section: int,
        orientation: Qt.Orientation,
        role: int = Qt.DisplayRole,
    ) -> Any:
        if role != Qt.DisplayRole or self._snapshot is None:
            return None
        if orientation == Qt.Horizontal:
            return self._snapshot.headers[section]
        return section + 1

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        if not index.isValid():
            return Qt.NoItemFlags
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def set_snapshot(self, snapshot: FeatureCatalogSnapshot | None) -> None:
        """Replace the table data with a newly loaded snapshot."""
        self.beginResetModel()
        self._snapshot = snapshot
        self.endResetModel()

    def cell_value(self, row: int, column: int) -> str:
        """Return a safe cell value for tests and future copy/export paths."""
        if self._snapshot is None or not (0 <= row < self.rowCount()):
            return ""
        return self._snapshot.rows[row].value_at(column)
