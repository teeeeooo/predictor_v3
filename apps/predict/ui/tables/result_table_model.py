"""Prediction Results table model for the Predict workspace."""

from typing import Any

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PySide6.QtGui import QColor

from apps.predict.schema.column_schema_adapter import (
    PredictColumn,
    build_result_column_schema,
)
from apps.predict.state.predict_session import PredictSession


class ResultTableModel(QAbstractTableModel):
    """Read-only result model backed by PredictSession case order."""

    def __init__(
        self,
        session: PredictSession | None = None,
        columns: tuple[PredictColumn, ...] | None = None,
    ) -> None:
        super().__init__()
        self._session = session or PredictSession()
        self._columns = columns or build_result_column_schema()

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
        if role != Qt.DisplayRole:
            return None
        case_id = self._session.case_order[index.row()]
        result = self._session.result_for_case(case_id)
        value = result.result_values.get(column.key, "")
        return "" if value is None else value

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
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def refresh(self) -> None:
        """Notify views that existing values may have changed."""
        if self.rowCount() == 0 or self.columnCount() == 0:
            return
        top_left = self.index(0, 0)
        bottom_right = self.index(self.rowCount() - 1, self.columnCount() - 1)
        self.dataChanged.emit(top_left, bottom_right, [Qt.DisplayRole])

    def refresh_case_id(self, case_id: str) -> None:
        """Notify views that one result row changed."""
        try:
            row = self._session.case_order.index(case_id)
        except ValueError:
            return
        top_left = self.index(row, 0)
        bottom_right = self.index(row, self.columnCount() - 1)
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
