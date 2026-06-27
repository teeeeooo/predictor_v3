"""Prediction Results table model for the Predict workspace."""

from dataclasses import dataclass
from typing import Any

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt

from apps.predict.state.predict_session import PredictSession


@dataclass(frozen=True)
class ResultColumn:
    """Local skeleton column definition for result display."""

    key: str
    label: str


RESULT_COLUMNS: tuple[ResultColumn, ...] = (
    ResultColumn("status", "Status"),
    ResultColumn("cooling_power", "Cooling Power"),
    ResultColumn("heating_power", "Heating Power"),
    ResultColumn("ref_qty", "Ref Qty"),
    ResultColumn("cooling_hz", "Cooling Hz"),
    ResultColumn("heating_hz", "Heating Hz"),
    ResultColumn("message", "Message"),
)


class ResultTableModel(QAbstractTableModel):
    """Read-only result model backed by PredictSession case order."""

    def __init__(self, session: PredictSession) -> None:
        super().__init__()
        self._session = session

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent.isValid():
            return 0
        return len(self._session.case_order)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent.isValid():
            return 0
        return len(RESULT_COLUMNS)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        if not index.isValid() or role != Qt.DisplayRole:
            return None
        column = RESULT_COLUMNS[index.column()]
        case_id = self._session.case_order[index.row()]
        result = self._session.result_for_case(case_id)
        if column.key == "status":
            return result.status
        if column.key == "message":
            return result.message
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
            return RESULT_COLUMNS[section].label
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
