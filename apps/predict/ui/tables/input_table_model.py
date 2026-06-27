"""Input Cases table model for the Predict workspace."""

from dataclasses import dataclass
from typing import Any

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt

from apps.predict.state.predict_session import PredictSession


@dataclass(frozen=True)
class InputColumn:
    """Local skeleton column definition for input/autofill display."""

    key: str
    label: str
    editable: bool = True
    autofill: bool = False


INPUT_COLUMNS: tuple[InputColumn, ...] = (
    InputColumn("case_id", "Case ID", editable=False),
    InputColumn("capacity", "Capacity"),
    InputColumn("indoor_model", "Indoor Model"),
    InputColumn("outdoor_model", "Outdoor Model"),
    InputColumn("refrigerant", "Refrigerant"),
    InputColumn("mapped_volume", "Mapped Volume", editable=False, autofill=True),
)


class InputTableModel(QAbstractTableModel):
    """Editable input/autofill model backed by PredictSession."""

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
        return len(INPUT_COLUMNS)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        if not index.isValid() or role not in (Qt.DisplayRole, Qt.EditRole):
            return None
        column = INPUT_COLUMNS[index.column()]
        case = self._session.case_store.get_case_at(index.row())
        if column.key == "case_id":
            return case.case_id
        if column.autofill:
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
        column = INPUT_COLUMNS[index.column()]
        if not column.editable or column.autofill:
            return False
        case = self._session.case_store.get_case_at(index.row())
        self._session.case_store.update_cell_value(case.case_id, column.key, value)
        self.dataChanged.emit(index, index, [Qt.DisplayRole, Qt.EditRole])
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
            return INPUT_COLUMNS[section].label
        return section + 1

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        if not index.isValid():
            return Qt.NoItemFlags
        flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable
        column = INPUT_COLUMNS[index.column()]
        if column.editable and not column.autofill:
            flags |= Qt.ItemIsEditable
        return flags

    def refresh(self) -> None:
        """Notify views that the session order or values changed."""
        self.layoutChanged.emit()
