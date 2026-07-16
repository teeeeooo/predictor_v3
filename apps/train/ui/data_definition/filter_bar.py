"""Search and filter composition for the Definition Inventory."""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import QSignalBlocker
from PySide6.QtWidgets import QComboBox, QFrame, QGridLayout, QLineEdit, QWidget

from apps.common.ui import style
from apps.train.controllers.data_definition_presentation import (
    DataDefinitionInventoryProjection,
)


class DataDefinitionFilterBar(QFrame):
    """Own non-mutating search/filter widgets and responsive placement."""

    def __init__(
        self,
        on_changed: Callable[[], None],
        on_search_submitted: Callable[[], None],
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("Panel")
        self.setAccessibleName("Data Definition search and filters")
        self.setStyleSheet(style.panel_stylesheet())
        self._compact = False
        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText("Search label, key, or ML name")
        self.search_input.setAccessibleName("Search Data Definitions")
        self.category_filter = _filter_combo(
            "Filter Data Definitions by category", self
        )
        self.source_filter = _filter_combo(
            "Filter Data Definitions by value source", self
        )
        self.state_filter = _filter_combo("Filter Data Definitions by state", self)
        self.layout_grid = QGridLayout(self)
        self.layout_grid.setContentsMargins(
            style.spacing("space.panel"),
            style.spacing("space.sm"),
            style.spacing("space.panel"),
            style.spacing("space.sm"),
        )
        self.layout_grid.setSpacing(style.spacing("space.sm"))
        self._arrange()
        self.search_input.textChanged.connect(on_changed)
        self.search_input.returnPressed.connect(on_search_submitted)
        self.category_filter.currentIndexChanged.connect(on_changed)
        self.source_filter.currentIndexChanged.connect(on_changed)
        self.state_filter.currentIndexChanged.connect(on_changed)

    def current_values(self) -> tuple[str, str, str, str]:
        return (
            self.search_input.text(),
            str(self.category_filter.currentData() or ""),
            str(self.source_filter.currentData() or ""),
            str(self.state_filter.currentData() or ""),
        )

    def apply_projection(self, projection: DataDefinitionInventoryProjection) -> None:
        _replace_options(
            self.category_filter,
            "All categories",
            projection.categories,
            projection.resolved_category,
        )
        _replace_options(
            self.source_filter,
            "All value sources",
            projection.source_types,
            projection.resolved_source_type,
        )
        _replace_options(
            self.state_filter,
            "All states",
            projection.lifecycle_states,
            projection.resolved_lifecycle_state,
        )

    def clear(self) -> None:
        with (
            QSignalBlocker(self.search_input),
            QSignalBlocker(self.category_filter),
            QSignalBlocker(self.source_filter),
            QSignalBlocker(self.state_filter),
        ):
            self.search_input.clear()
            self.category_filter.setCurrentIndex(0)
            self.source_filter.setCurrentIndex(0)
            self.state_filter.setCurrentIndex(0)

    def apply_compact(self, compact: bool) -> None:
        if compact == self._compact:
            return
        self._compact = compact
        self._arrange()

    def _arrange(self) -> None:
        for widget in (
            self.search_input,
            self.category_filter,
            self.source_filter,
            self.state_filter,
        ):
            self.layout_grid.removeWidget(widget)
        if self._compact:
            self.layout_grid.addWidget(self.search_input, 0, 0, 1, 3)
            self.layout_grid.addWidget(self.category_filter, 1, 0)
            self.layout_grid.addWidget(self.source_filter, 1, 1)
            self.layout_grid.addWidget(self.state_filter, 1, 2)
        else:
            self.layout_grid.addWidget(self.search_input, 0, 0)
            self.layout_grid.addWidget(self.category_filter, 0, 1)
            self.layout_grid.addWidget(self.source_filter, 0, 2)
            self.layout_grid.addWidget(self.state_filter, 0, 3)
        self.layout_grid.setColumnStretch(0, 2)
        for column in (1, 2, 3):
            self.layout_grid.setColumnStretch(column, 1)


def _filter_combo(accessible_name: str, parent: QWidget) -> QComboBox:
    combo = QComboBox(parent)
    combo.setAccessibleName(accessible_name)
    return combo


def _replace_options(
    combo: QComboBox,
    all_label: str,
    options: tuple[str, ...],
    selected: str,
) -> None:
    with QSignalBlocker(combo):
        combo.clear()
        combo.addItem(all_label, "")
        for option in options:
            combo.addItem(option, option)
        index = combo.findData(selected)
        combo.setCurrentIndex(index if index >= 0 else 0)
