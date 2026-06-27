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
    ResultColumn("case_id", "Case ID"),
    ResultColumn("status", "Status"),
    ResultColumn("power", "Power"),
    ResultColumn("eer", "EER"),
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
        if column.key == "case_id":
            return case_id
        if column.key == "status":
            return result.status
        if column.key == "message":
            return result.message
        return result.result_values.get(column.key, "")

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
        """Notify views that the session order or values changed."""
        self.layoutChanged.emit()
