"""Read-only full-row interaction for Result Review."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence
from PySide6.QtWidgets import (
    QApplication,
    QAbstractItemView,
    QHeaderView,
    QTableView,
    QWidget,
)


PINNED_RESULT_COLUMNS = 2


class _ResultReviewAnchorView(QTableView):
    """Render the pinned columns while sharing the primary view's state."""

    def __init__(self, owner: "ResultReviewTableView") -> None:
        super().__init__(owner)
        self._owner = owner
        self.setObjectName("ResultReviewPinnedAnchor")
        self.setFocusProxy(owner)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setWordWrap(False)
        self.setTextElideMode(Qt.ElideRight)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.verticalHeader().hide()
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.horizontalHeader().setStretchLastSection(False)

    def keyPressEvent(self, event):  # noqa: ANN001
        if event.matches(QKeySequence.Copy):
            self._owner.copy_selected_rows_to_clipboard()
            event.accept()
            return
        super().keyPressEvent(event)


class ResultReviewTableView(QTableView):
    """Select and copy complete review rows in canonical session order."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setWordWrap(False)
        self.setTextElideMode(Qt.ElideRight)
        self._pinning_active = False
        self._syncing_width = False
        self._anchor_view = _ResultReviewAnchorView(self)
        self._anchor_view.hide()
        self.horizontalHeader().sectionResized.connect(
            self._sync_anchor_column_width
        )
        self._anchor_view.horizontalHeader().sectionResized.connect(
            self._sync_primary_column_width
        )
        self.verticalHeader().sectionResized.connect(self._sync_anchor_row_height)
        self.verticalScrollBar().valueChanged.connect(
            self._anchor_view.verticalScrollBar().setValue
        )
        self._anchor_view.verticalScrollBar().valueChanged.connect(
            self.verticalScrollBar().setValue
        )

    @property
    def pinned_columns_active(self) -> bool:
        return self._pinning_active

    @property
    def pinned_anchor_view(self) -> QTableView:
        """Expose the actual Qt anchor surface for bounded interaction checks."""
        return self._anchor_view

    def setModel(self, model) -> None:  # noqa: ANN001, N802
        super().setModel(model)
        self._anchor_view.setModel(model)
        if model is not None:
            self._anchor_view.setSelectionModel(self.selectionModel())
            for column in range(model.columnCount()):
                self._anchor_view.setColumnHidden(
                    column, column >= PINNED_RESULT_COLUMNS
                )
        self._update_pinned_presentation()

    def setColumnWidth(self, column: int, width: int) -> None:  # noqa: N802
        super().setColumnWidth(column, width)
        if column < PINNED_RESULT_COLUMNS and not self._syncing_width:
            self._syncing_width = True
            try:
                self._anchor_view.setColumnWidth(column, width)
            finally:
                self._syncing_width = False
        self._update_pinned_presentation()

    def presentation_column_widths(self) -> tuple[int, ...]:
        """Return user-visible widths whether columns are pinned or inline."""
        model = self.model()
        if model is None:
            return ()
        return tuple(
            self._anchor_view.columnWidth(column)
            if column < PINNED_RESULT_COLUMNS and self._pinning_active
            else self.columnWidth(column)
            for column in range(model.columnCount())
        )

    def restore_presentation_column_widths(self, widths: tuple[int, ...]) -> None:
        for column, width in enumerate(widths):
            self.setColumnWidth(column, width)

    def presentation_row_heights(self) -> tuple[int, ...]:
        model = self.model()
        if model is None:
            return ()
        return tuple(self.rowHeight(row) for row in range(model.rowCount()))

    def restore_presentation_row_heights(self, heights: tuple[int, ...]) -> None:
        for row, height in enumerate(heights):
            self.setRowHeight(row, height)
            self._anchor_view.setRowHeight(row, height)

    def resizeEvent(self, event) -> None:  # noqa: ANN001, N802
        super().resizeEvent(event)
        self._update_pinned_presentation()

    def selected_row_indexes(self) -> list[int]:
        selection = self.selectionModel()
        if selection is None:
            return []
        return sorted({index.row() for index in selection.selectedRows()})

    def copy_selected_rows_tsv(self) -> str:
        model = self.model()
        if model is None or not hasattr(model, "copy_rows_tsv"):
            return ""
        return model.copy_rows_tsv(self.selected_row_indexes())

    def copy_selected_rows_to_clipboard(self) -> bool:
        text = self.copy_selected_rows_tsv()
        if not text:
            return False
        QApplication.clipboard().setText(text)
        return True

    def keyPressEvent(self, event):  # noqa: ANN001
        if event.matches(QKeySequence.Copy):
            self.copy_selected_rows_to_clipboard()
            event.accept()
            return
        super().keyPressEvent(event)

    def _sync_anchor_column_width(
        self, logical_index: int, _old_size: int, new_size: int
    ) -> None:
        if logical_index < PINNED_RESULT_COLUMNS and not self._syncing_width:
            self._syncing_width = True
            try:
                self._anchor_view.setColumnWidth(logical_index, new_size)
            finally:
                self._syncing_width = False
        self._update_pinned_presentation()

    def _sync_primary_column_width(
        self, logical_index: int, _old_size: int, new_size: int
    ) -> None:
        if logical_index >= PINNED_RESULT_COLUMNS or self._syncing_width:
            return
        self._syncing_width = True
        try:
            super().setColumnWidth(logical_index, new_size)
        finally:
            self._syncing_width = False
        self._update_pinned_presentation()

    def _sync_anchor_row_height(
        self, logical_index: int, _old_size: int, new_size: int
    ) -> None:
        self._anchor_view.setRowHeight(logical_index, new_size)

    def _update_pinned_presentation(self) -> None:
        model = self.model()
        if model is None:
            self._set_pinning_active(False)
            return
        content_width = sum(self.presentation_column_widths())
        scrollbar_width = (
            self.verticalScrollBar().sizeHint().width()
            if self.verticalScrollBar().isVisible()
            else 0
        )
        available_width = max(
            0,
            self.width()
            - (2 * self.frameWidth())
            - self.verticalHeader().width()
            - scrollbar_width,
        )
        self._set_pinning_active(content_width > available_width)

    def _set_pinning_active(self, active: bool) -> None:
        if self._pinning_active != active:
            self._pinning_active = active
            for column in range(PINNED_RESULT_COLUMNS):
                self.setColumnHidden(column, active)
        anchor_width = sum(
            self._anchor_view.columnWidth(column)
            for column in range(PINNED_RESULT_COLUMNS)
        )
        vertical_header_width = (
            self.verticalHeader().width() if self.verticalHeader().isVisible() else 0
        )
        horizontal_header_height = (
            self.horizontalHeader().height() if self.horizontalHeader().isVisible() else 0
        )
        self.setViewportMargins(
            vertical_header_width + (anchor_width if active else 0),
            horizontal_header_height,
            0,
            0,
        )
        if not active:
            self._anchor_view.hide()
            return
        self._anchor_view.setGeometry(
            vertical_header_width + self.frameWidth(),
            0,
            anchor_width,
            self.viewport().height()
            + horizontal_header_height
            + (2 * self.frameWidth()),
        )
        self._anchor_view.horizontalHeader().setFixedHeight(
            self.horizontalHeader().height()
        )
        self._anchor_view.show()
        self._anchor_view.raise_()
