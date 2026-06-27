"""Input Cases table model for the Predict workspace."""

from collections.abc import Callable
from typing import Any

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PySide6.QtGui import QColor

from apps.predict.schema.column_schema_adapter import (
    PredictColumn,
    build_input_column_schema,
)
from apps.predict.state.predict_session import PredictSession

InputEditCallback = Callable[[str, str], None]


class InputTableModel(QAbstractTableModel):
    """Editable input/autofill model backed by PredictSession."""

    def __init__(
        self,
        session: PredictSession | None = None,
        columns: tuple[PredictColumn, ...] | None = None,
        edit_callback: InputEditCallback | None = None,
    ) -> None:
        super().__init__()
        self._session = session or PredictSession()
        self._columns = columns or build_input_column_schema()
        self._edit_callback = edit_callback

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent.isValid():
            return 0
        return len(self._session.case_order)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent.isValid():
            return 0
        return len(self._columns)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        if not index.isValid():
            return None
        column = self._columns[index.column()]
        if role == Qt.BackgroundRole and column.bg_color:
            return QColor(column.bg_color)
        if role not in (Qt.DisplayRole, Qt.EditRole):
            return None
        case = self._session.case_store.get_case_at(index.row())
        if column.is_auto:
            return case.autofill_values.get(column.key, "")
        return case.input_values.get(column.key, "")

    def setData(
        self,
        index: QModelIndex,
        value: Any,
        role: int = Qt.EditRole,
    ) -> bool:
        if not index.isValid() or role != Qt.EditRole:
            return False
        column = self._columns[index.column()]
        if not column.editable or column.is_auto:
            return False
        case = self._session.case_store.get_case_at(index.row())
        self._session.case_store.update_cell_value(case.case_id, column.key, value)
        if self._edit_callback is not None:
            self._edit_callback(case.case_id, column.key)
        left = self.index(index.row(), 0)
        right = self.index(index.row(), self.columnCount() - 1)
        self.dataChanged.emit(left, right, [Qt.DisplayRole, Qt.EditRole])
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
            return self._columns[section].header
        return section + 1

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        if not index.isValid():
            return Qt.NoItemFlags
        flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable
        column = self._columns[index.column()]
        if column.editable and not column.is_auto:
            flags |= Qt.ItemIsEditable
        return flags

    def refresh(self) -> None:
        """Notify views that existing values may have changed."""
        if self.rowCount() == 0 or self.columnCount() == 0:
            return
        top_left = self.index(0, 0)
        bottom_right = self.index(self.rowCount() - 1, self.columnCount() - 1)
        self.dataChanged.emit(top_left, bottom_right, [Qt.DisplayRole])

    def begin_insert_rows(self, first_row: int, last_row: int) -> None:
        """Notify views that rows are about to be inserted."""
        self.beginInsertRows(QModelIndex(), first_row, last_row)

    def end_insert_rows(self) -> None:
        """Notify views that row insertion finished."""
        self.endInsertRows()

    def begin_remove_rows(self, first_row: int, last_row: int) -> None:
        """Notify views that rows are about to be removed."""
        self.beginRemoveRows(QModelIndex(), first_row, last_row)

    def end_remove_rows(self) -> None:
        """Notify views that row removal finished."""
        self.endRemoveRows()

    def begin_reset_model(self) -> None:
        """Notify views that the model is about to reset."""
        self.beginResetModel()

    def end_reset_model(self) -> None:
        """Notify views that model reset finished."""
        self.endResetModel()
