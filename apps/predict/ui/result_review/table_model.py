"""Read-only Qt model for the canonical Result Review projection."""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt

from apps.predict.application.result_review import (
    RESULT_REVIEW_COLUMNS,
    ResultReviewClipboardDocument,
    ResultReviewProjection,
)
from apps.predict.application.result_review.presentation import (
    display_value,
    tooltip_value,
)


class ResultReviewTableModel(QAbstractTableModel):
    """Present projection rows without retaining an independent row store."""

    def __init__(self, projection: ResultReviewProjection) -> None:
        super().__init__()
        self._projection = projection

    @property
    def projection(self) -> ResultReviewProjection:
        return self._projection

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 0 if parent.isValid() else len(self._projection.session.case_order)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 0 if parent.isValid() else len(RESULT_REVIEW_COLUMNS)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        if not index.isValid():
            return None
        rows = self._projection.rows()
        if not (0 <= index.row() < len(rows)):
            return None
        row = rows[index.row()]
        key = RESULT_REVIEW_COLUMNS[index.column()].key
        if role == Qt.DisplayRole:
            return display_value(row, key)
        if role == Qt.ToolTipRole:
            return tooltip_value(row, key)
        if role == Qt.TextAlignmentRole and key != "specification_summary":
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
            return RESULT_REVIEW_COLUMNS[section].header
        return section + 1

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        if not index.isValid():
            return Qt.NoItemFlags
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def case_ids_for_rows(self, row_indexes: list[int]) -> tuple[str, ...]:
        selected = set(row_indexes)
        return tuple(
            case_id
            for index, case_id in enumerate(self._projection.session.case_order)
            if index in selected
        )

    def full_row_document_for_rows(
        self, row_indexes: list[int]
    ) -> ResultReviewClipboardDocument | None:
        case_ids = self.case_ids_for_rows(row_indexes)
        if not case_ids:
            return None
        return self._projection.clipboard_document(case_ids)

    def copy_rows_tsv(self, row_indexes: list[int]) -> str:
        document = self.full_row_document_for_rows(row_indexes)
        return "" if document is None else document.to_tsv()

    def refresh(self) -> None:
        self.beginResetModel()
        self.endResetModel()

    def refresh_case_id(self, case_id: str) -> None:
        """Notify views that one canonical projection row changed."""
        try:
            row = self._projection.session.case_order.index(case_id)
        except ValueError:
            return
        first = self.index(row, 0)
        last = self.index(row, self.columnCount() - 1)
        self.dataChanged.emit(first, last)

    def begin_insert_rows(self, first_row: int, last_row: int) -> None:
        self.beginInsertRows(QModelIndex(), first_row, last_row)

    def end_insert_rows(self) -> None:
        self.endInsertRows()

    def begin_remove_rows(self, first_row: int, last_row: int) -> None:
        self.beginRemoveRows(QModelIndex(), first_row, last_row)

    def end_remove_rows(self) -> None:
        self.endRemoveRows()

    def begin_reset_model(self) -> None:
        self.beginResetModel()

    def end_reset_model(self) -> None:
        self.endResetModel()
