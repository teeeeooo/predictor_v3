"""Qt table models for Data Definition draft state."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt

from apps.common.ui import style
from apps.train.controllers.data_definition_controller import DataDefinitionDraftCellState
from apps.train.controllers.data_definition_presentation import DataDefinitionInventoryRow

DraftCellEditCallback = Callable[[tuple[str, str], str, object], bool]

INVENTORY_HEADERS = (
    "Label",
    "Kind",
    "Value source",
    "Predict",
    "Model input",
    "Status",
)


class DataDefinitionInventoryTableModel(QAbstractTableModel):
    """Read-only inventory model with stable draft-row identities."""

    def __init__(self, rows: Sequence[DataDefinitionInventoryRow] = ()) -> None:
        super().__init__()
        self._rows = tuple(rows)

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 0 if parent.isValid() else len(self._rows)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 0 if parent.isValid() else len(INVENTORY_HEADERS)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        if not self._has_cell(index):
            return None
        row = self._rows[index.row()]
        values = (
            row.label,
            row.kind,
            row.source_type,
            row.predict_visibility,
            row.model_input,
            row.lifecycle_state,
        )
        if role in (Qt.DisplayRole, Qt.EditRole):
            return values[index.column()]
        if role == Qt.ToolTipRole:
            return f"{row.internal_key}\nML name: {row.ml_name or '—'}"
        if role == Qt.AccessibleDescriptionRole:
            return f"Internal key {row.internal_key}; ML name {row.ml_name or 'none'}"
        if role == Qt.BackgroundRole:
            if row.lifecycle_state == "Blocked":
                return style.table_background_role("invalid")
            if row.lifecycle_state == "Changed":
                return style.table_background_role("warning")
        if role == Qt.TextAlignmentRole:
            return Qt.AlignLeft | Qt.AlignVCenter if index.column() == 0 else Qt.AlignCenter
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
            return INVENTORY_HEADERS[section] if 0 <= section < len(INVENTORY_HEADERS) else None
        return section + 1 if 0 <= section < len(self._rows) else None

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        if not self._has_cell(index):
            return Qt.NoItemFlags
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def identity_at(self, row: int) -> tuple[str, str] | None:
        return self._rows[row].identity if 0 <= row < len(self._rows) else None

    def row_for_identity(
        self,
        identity: tuple[str, str],
    ) -> int | None:
        return next(
            (index for index, row in enumerate(self._rows) if row.identity == identity),
            None,
        )

    def cell_value(self, row: int, column: int) -> str:
        index = self.index(row, column)
        return str(self.data(index, Qt.DisplayRole) or "")

    def _has_cell(self, index: QModelIndex) -> bool:
        return (
            index.isValid()
            and 0 <= index.row() < len(self._rows)
            and 0 <= index.column() < len(INVENTORY_HEADERS)
        )


class DataDefinitionDraftTableModel(QAbstractTableModel):
    """Editable table model backed by controller-projected draft rows."""

    def __init__(
        self,
        headers: Sequence[str],
        row_identities: Sequence[tuple[str, str]],
        rows: Sequence[Sequence[DataDefinitionDraftCellState]],
        *,
        on_cell_changed: DraftCellEditCallback | None = None,
    ) -> None:
        super().__init__()
        self._headers = tuple(headers)
        self._row_identities = tuple(row_identities)
        self._rows = tuple(tuple(row) for row in rows)
        self._on_cell_changed = on_cell_changed

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
        cell = self._rows[index.row()][index.column()]
        if role in (Qt.DisplayRole, Qt.EditRole):
            return cell.value
        if role == Qt.BackgroundRole:
            if cell.changed:
                return style.table_background_role("warning")
            if not cell.editable:
                return style.table_background_role("fixed")
        if role == Qt.ToolTipRole:
            if cell.changed:
                return "Draft value differs from the loaded schema."
            if not cell.editable:
                return cell.reason
        if role == Qt.TextAlignmentRole:
            return Qt.AlignCenter
        return None

    def setData(
        self,
        index: QModelIndex,
        value: Any,
        role: int = Qt.EditRole,
    ) -> bool:
        if role != Qt.EditRole or not self._has_cell(index):
            return False
        if not self.is_editable_cell(index.row(), index.column()):
            return False
        cell = self._rows[index.row()][index.column()]
        if str(cell.value) == str(value):
            return True
        if self._on_cell_changed is None:
            return False
        accepted = self._on_cell_changed(
            self._row_identities[index.row()],
            cell.field_name,
            value,
        )
        if accepted:
            self.dataChanged.emit(index, index, [Qt.DisplayRole, Qt.EditRole])
        return accepted

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
        if not 0 <= section < len(self._rows):
            return None
        return section + 1

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        if not self._has_cell(index):
            return Qt.NoItemFlags
        flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable
        if self.is_editable_cell(index.row(), index.column()):
            flags |= Qt.ItemIsEditable
        return flags

    def cell_value(self, row: int, column: int) -> str:
        """Return a display value for tests and future copy/export paths."""
        if not self._is_cell_in_range(row, column):
            return ""
        return self._rows[row][column].value

    def is_editable_cell(self, row: int, column: int) -> bool:
        """Return whether a cell can be edited by the user."""
        if not self._is_cell_in_range(row, column):
            return False
        return self._rows[row][column].editable

    def is_changed_cell(self, row: int, column: int) -> bool:
        """Return whether a cell differs from the loaded baseline."""
        if not self._is_cell_in_range(row, column):
            return False
        return self._rows[row][column].changed

    def _has_cell(self, index: QModelIndex) -> bool:
        return index.isValid() and self._is_cell_in_range(index.row(), index.column())

    def _is_cell_in_range(self, row: int, column: int) -> bool:
        return (
            0 <= row < len(self._rows)
            and 0 <= column < len(self._headers)
            and column < len(self._rows[row])
        )
