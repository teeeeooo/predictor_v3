"""Table-linked grouped header affordance for unified case tables."""

from __future__ import annotations

from collections.abc import Sequence

from PySide6.QtCore import QRect, Qt
from PySide6.QtWidgets import QLabel, QFrame, QTableView

from apps.common.ui import style
from apps.predict.schema.case_table_schema_adapter import UnifiedCaseColumn


GROUP_LABELS = {
    "input": "Input",
    "auto": "Auto-fill / Calculated",
    "result": "Prediction Results",
    "status": "Status / Warning",
}


class TableLinkedGroupHeader(QFrame):
    """Header band whose label geometry follows a table's real columns."""

    def __init__(
        self,
        table: QTableView,
        columns: Sequence[UnifiedCaseColumn],
        parent: QFrame | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("TableLinkedGroupHeader")
        self.setFixedHeight(24)
        self._table = table
        self._columns: tuple[UnifiedCaseColumn, ...] = ()
        self._labels: dict[str, QLabel] = {}
        self._model = None
        self._connect_table()
        self.rebind(columns)

    def rebind(self, columns: Sequence[UnifiedCaseColumn]) -> None:
        """Bind label geometry and model signals to the current table projection."""
        self._disconnect_model()
        self._columns = tuple(columns)
        self._sync_labels()
        self._model = self._table.model()
        self._connect_model()
        self.update_geometry()

    def group_rects(self) -> dict[str, QRect]:
        """Return visible group rectangles in this widget's coordinate space."""
        return self._group_rects(clipped=True)

    def group_column_rects(self) -> dict[str, QRect]:
        """Return full group rectangles derived from actual table sections."""
        return self._group_rects(clipped=False)

    def update_geometry(self) -> None:
        """Synchronize child labels with current table header geometry."""
        rects = self.group_rects()
        for group, label in self._labels.items():
            rect = rects.get(group, QRect())
            label.setVisible(rect.width() > 0)
            label.setGeometry(rect)

    def resizeEvent(self, event):  # noqa: ANN001
        super().resizeEvent(event)
        self.update_geometry()

    def _group_rects(self, clipped: bool) -> dict[str, QRect]:
        header = self._table.horizontalHeader()
        viewport_left = self._table.verticalHeader().width()
        viewport_width = self._table.viewport().width()
        visible_left = viewport_left
        visible_right = viewport_left + viewport_width
        rects: dict[str, QRect] = {}
        for group in self._ordered_groups():
            indexes = [
                index for index, column in enumerate(self._columns) if column.group == group
            ]
            if not indexes:
                continue
            first = indexes[0]
            last = indexes[-1]
            x = viewport_left + header.sectionViewportPosition(first)
            right = (
                viewport_left
                + header.sectionViewportPosition(last)
                + header.sectionSize(last)
            )
            if clipped:
                x = max(x, visible_left)
                right = min(right, visible_right)
            rects[group] = QRect(x, 0, max(0, right - x), self.height())
        return rects

    def _connect_table(self) -> None:
        header = self._table.horizontalHeader()
        header.sectionResized.connect(self._update_from_signal)
        header.sectionMoved.connect(self._update_from_signal)
        header.geometriesChanged.connect(self.update_geometry)
        self._table.horizontalScrollBar().valueChanged.connect(self._update_from_signal)

    def _connect_model(self) -> None:
        if self._model is None:
            return
        self._model.modelReset.connect(self._update_from_signal)
        self._model.columnsInserted.connect(self._update_from_signal)
        self._model.columnsRemoved.connect(self._update_from_signal)

    def _disconnect_model(self) -> None:
        if self._model is None:
            return
        self._model.modelReset.disconnect(self._update_from_signal)
        self._model.columnsInserted.disconnect(self._update_from_signal)
        self._model.columnsRemoved.disconnect(self._update_from_signal)
        self._model = None

    def _update_from_signal(self, *_args) -> None:
        self.update_geometry()

    def _sync_labels(self) -> None:
        groups = self._ordered_groups()
        for group in tuple(self._labels):
            if group in groups:
                continue
            label = self._labels.pop(group)
            label.hide()
            label.deleteLater()
        self._labels = {
            group: self._labels.get(group) or self._label_for(group)
            for group in groups
        }

    def _ordered_groups(self) -> tuple[str, ...]:
        groups: list[str] = []
        for column in self._columns:
            if column.group and column.group not in groups:
                groups.append(column.group)
        return tuple(groups)

    def _label_for(self, group: str) -> QLabel:
        label = QLabel(GROUP_LABELS.get(group, group), self)
        label.setObjectName("TableLinkedGroupHeaderLabel")
        label.setAlignment(Qt.AlignCenter)
        label.setFont(style.qfont("font.caption"))
        label.setStyleSheet(style.table_group_label_stylesheet(group))
        return label
