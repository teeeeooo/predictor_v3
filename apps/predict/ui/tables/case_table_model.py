"""Unified case table model for the Predict workspace."""

from collections.abc import Callable
from typing import Any

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PySide6.QtGui import QColor

from apps.common.ui import style
from apps.predict.schema.case_table_schema_adapter import (
    UnifiedCaseColumn,
    build_case_table_column_schema,
)
from apps.predict.state.predict_session import PredictSession

InputEditCallback = Callable[[str, str], None]


class CaseTableModel(QAbstractTableModel):
    """Unified input, auto-fill, result, and status table model."""

    def __init__(
        self,
        session: PredictSession | None = None,
        columns: tuple[UnifiedCaseColumn, ...] | None = None,
        edit_callback: InputEditCallback | None = None,
    ) -> None:
        super().__init__()
        self._session = session or PredictSession()
        self._columns = columns or build_case_table_column_schema()
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
        if role == Qt.BackgroundRole:
            return self._background_for_cell(index.row(), column)
        if role == Qt.ToolTipRole:
            return self._tooltip_for_cell(index.row(), index.column())
        if role not in (Qt.DisplayRole, Qt.EditRole):
            return None
        return self.cell_value(index.row(), index.column())

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
        column = self._columns[index.column()]
        case = self._session.case_store.get_case_at(index.row())
        current_value = case.input_values.get(column.key, "")
        new_value = "" if value is None else str(value)
        if str(current_value) == new_value:
            return True
        self._session.case_store.update_cell_value(case.case_id, column.key, value)
        if self._edit_callback is not None:
            self._edit_callback(case.case_id, column.key)
        self.refresh_case_id(case.case_id)
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
        if self.is_editable_cell(index.row(), index.column()):
            flags |= Qt.ItemIsEditable
        return flags

    @property
    def columns(self) -> tuple[UnifiedCaseColumn, ...]:
        """Return unified case table column descriptors."""
        return self._columns

    def cell_value(self, row: int, col: int) -> Any:
        """Return display value for a cell by row/column."""
        if not (0 <= row < self.rowCount() and 0 <= col < self.columnCount()):
            return ""
        column = self._columns[col]
        case_id = self._session.case_order[row]
        case = self._session.case_store.get_case(case_id)
        if column.is_input:
            return case.input_values.get(column.key, "")
        if column.is_auto:
            return case.autofill_values.get(column.key, "")
        result = self._session.result_for_case(case_id)
        if column.is_result:
            return result.result_values.get(column.key, "")
        if column.key == "status":
            return result.status
        if column.key == "message":
            return result.message
        return ""

    def is_editable_cell(self, row: int, col: int) -> bool:
        """Return whether a row/column can be edited by the user."""
        if not (0 <= row < self.rowCount() and 0 <= col < self.columnCount()):
            return False
        return self._columns[col].editable

    def is_readonly_cell(self, row: int, col: int) -> bool:
        """Return whether a row/column is selectable but mutation-protected."""
        if not (0 <= row < self.rowCount() and 0 <= col < self.columnCount()):
            return False
        return self._columns[col].read_only

    def is_invalid(self, row: int, col: int) -> bool:
        """Return whether a numeric ML feature cell contains invalid text."""
        if not (0 <= row < self.rowCount() and 0 <= col < self.columnCount()):
            return False
        column = self._columns[col]
        if not column.ml_feature:
            return False
        value = self.cell_value(row, col)
        if value is None or str(value).strip() == "":
            return False
        try:
            float(value)
        except (TypeError, ValueError):
            return True
        return False

    def refresh(self) -> None:
        """Notify views that existing values may have changed."""
        if self.rowCount() == 0 or self.columnCount() == 0:
            return
        top_left = self.index(0, 0)
        bottom_right = self.index(self.rowCount() - 1, self.columnCount() - 1)
        self.dataChanged.emit(top_left, bottom_right, [Qt.DisplayRole, Qt.EditRole])

    def refresh_case_id(self, case_id: str) -> None:
        """Notify views that one unified case row changed."""
        try:
            row = self._session.case_order.index(case_id)
        except ValueError:
            return
        top_left = self.index(row, 0)
        bottom_right = self.index(row, self.columnCount() - 1)
        self.dataChanged.emit(top_left, bottom_right, [Qt.DisplayRole, Qt.EditRole])

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

    def _background_for_cell(self, row: int, column: UnifiedCaseColumn) -> QColor:
        if self.is_invalid(row, column.index):
            return style.table_background_role("invalid")
        case_id = self._session.case_order[row]
        result = self._session.result_for_case(case_id)
        if result.status in {"error", "invalid"}:
            return style.table_background_role("invalid")
        if result.status in {"partial", "warning"}:
            return style.table_background_role("warning")
        if column.is_auto:
            return style.table_background_role("calculated")
        if column.is_result or column.is_status:
            return style.table_background_role("result")
        if column.bg_color:
            return QColor(column.bg_color)
        return style.table_background_role("input")

    def _tooltip_for_cell(self, row: int, col: int) -> str:
        if self.is_invalid(row, col):
            return f"{self._columns[col].header} must be numeric."
        case_id = self._session.case_order[row]
        result = self._session.result_for_case(case_id)
        return result.message
