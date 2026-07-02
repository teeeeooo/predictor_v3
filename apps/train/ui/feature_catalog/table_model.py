"""Read-only Feature Catalog table model."""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt, Signal

from apps.common.ui import style
from apps.train.application.feature_catalog import (
    EDITABLE_HEADERS,
    FeatureCatalogRecord,
    FeatureCatalogSnapshot,
)

ALLOWED_ACTIVE_VALUES = frozenset({"true", "false"})
ALLOWED_ZERO_FILL_POLICIES = frozenset({"disallow", "mode_missing_allowed"})


class FeatureCatalogTableModel(QAbstractTableModel):
    """QAbstractTableModel backed by a Feature Catalog snapshot."""

    dirty_changed = Signal(bool)

    def __init__(self, snapshot: FeatureCatalogSnapshot | None = None) -> None:
        super().__init__()
        self._headers: tuple[str, ...] = ()
        self._display_headers: tuple[str, ...] = ()
        self._rows: list[list[str]] = []
        self._baseline_rows: tuple[tuple[str, ...], ...] = ()
        self._field_options = None
        self._dirty = False
        self.set_snapshot(snapshot)

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
        if role == Qt.BackgroundRole and self.is_invalid_cell(index.row(), index.column()):
            return style.table_background_role("invalid")
        if role not in (Qt.DisplayRole, Qt.EditRole):
            return None
        return self._rows[index.row()][index.column()]

    def setData(
        self,
        index: QModelIndex,
        value: Any,
        role: int = Qt.EditRole,
    ) -> bool:
        if not index.isValid() or role != Qt.EditRole:
            return False
        if not self.is_editable_cell(index.row(), index.column()):
            return False
        new_value = "" if value is None else str(value)
        if self._rows[index.row()][index.column()] == new_value:
            return True
        self._rows[index.row()][index.column()] = new_value
        self.dataChanged.emit(index, index, [Qt.DisplayRole, Qt.EditRole, Qt.BackgroundRole])
        self._sync_dirty_state()
        return True

    def headerData(
        self,
        section: int,
        orientation: Qt.Orientation,
        role: int = Qt.DisplayRole,
    ) -> Any:
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            return self._display_headers[section]
        return section + 1

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        if not index.isValid():
            return Qt.NoItemFlags
        flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable
        if self.is_editable_cell(index.row(), index.column()):
            flags |= Qt.ItemIsEditable
        return flags

    def set_snapshot(self, snapshot: FeatureCatalogSnapshot | None) -> None:
        """Replace the table data with a newly loaded snapshot."""
        self.beginResetModel()
        self._headers = tuple(snapshot.headers) if snapshot is not None else ()
        self._display_headers = tuple(snapshot.display_headers) if snapshot is not None else ()
        self._field_options = snapshot.field_options if snapshot is not None else None
        self._rows = [
            [record.value_at(column) for column in range(len(self._headers))]
            for record in (snapshot.rows if snapshot is not None else ())
        ]
        self._baseline_rows = tuple(tuple(row) for row in self._rows)
        self.endResetModel()
        self._set_dirty(False)

    def cell_value(self, row: int, column: int) -> str:
        """Return a safe cell value for tests and future copy/export paths."""
        if not (0 <= row < self.rowCount() and 0 <= column < self.columnCount()):
            return ""
        return self._rows[row][column]

    def records(self) -> tuple[FeatureCatalogRecord, ...]:
        """Return current table rows as service DTOs."""
        return tuple(FeatureCatalogRecord(values=tuple(row)) for row in self._rows)

    def canonical_header(self, column: int) -> str:
        """Return the canonical header for a column."""
        if not 0 <= column < len(self._headers):
            return ""
        return self._headers[column]

    def dropdown_options(self, row: int, column: int) -> tuple[str, ...]:
        """Return dropdown candidates for a cell."""
        if not (0 <= row < self.rowCount() and 0 <= column < self.columnCount()):
            return ()
        snapshot_options = getattr(self, "_field_options", None)
        if snapshot_options is None:
            return ()
        return snapshot_options.values_for(self._headers[column])

    @property
    def is_dirty(self) -> bool:
        """Return whether current table values differ from the loaded snapshot."""
        return self._dirty

    def is_editable_cell(self, row: int, column: int) -> bool:
        """Return whether the cell belongs to the editable whitelist."""
        if not (0 <= row < self.rowCount() and 0 <= column < self.columnCount()):
            return False
        return self._headers[column] in EDITABLE_HEADERS

    def is_invalid_cell(self, row: int, column: int) -> bool:
        """Return whether a cell has an invalid strict enum value."""
        if not (0 <= row < self.rowCount() and 0 <= column < self.columnCount()):
            return False
        header = self._headers[column]
        value = self._rows[row][column]
        if header == "active":
            return value not in ALLOWED_ACTIVE_VALUES
        if header == "zero_fill_policy":
            return value not in ALLOWED_ZERO_FILL_POLICIES
        return False

    def _set_dirty(self, dirty: bool) -> None:
        if self._dirty == dirty:
            return
        self._dirty = dirty
        self.dirty_changed.emit(dirty)

    def _sync_dirty_state(self) -> None:
        self._set_dirty(tuple(tuple(row) for row in self._rows) != self._baseline_rows)
