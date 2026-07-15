"""Concise selected-group Mapping Requirement coverage surface."""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import QSignalBlocker
from PySide6.QtWidgets import QComboBox, QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from apps.common.ui import style
from apps.train.application.data_mapping import DataMappingCellTarget, DataMappingCoverageItem


class DataMappingCoveragePanel(QFrame):
    """Present one selected requirement and forward stable unresolved targets."""

    def __init__(self, on_navigate: Callable[[DataMappingCellTarget], None]) -> None:
        super().__init__()
        self.setObjectName("Panel")
        self.setAccessibleName("Mapping Requirement coverage")
        self.setStyleSheet(style.panel_stylesheet())
        self._items: tuple[DataMappingCoverageItem, ...] = ()
        self._on_navigate = on_navigate
        self.selector = QComboBox(self)
        self.selector.setAccessibleName("Mapping Requirement coverage item")
        self.selector.currentIndexChanged.connect(self._sync)
        self.summary = QLabel(self)
        self.summary.setAccessibleName("Mapping Requirement coverage summary")
        self.summary.setWordWrap(True)
        self.go_button = QPushButton("Go to first unresolved", self)
        self.go_button.setAccessibleName("Go to first unresolved mapping value")
        self.go_button.clicked.connect(self._go)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            style.spacing("space.panel"),
            style.spacing("space.sm"),
            style.spacing("space.panel"),
            style.spacing("space.sm"),
        )
        heading = QHBoxLayout()
        title = QLabel("Definition-backed Coverage", self)
        title.setObjectName("PanelTitle")
        title.setFont(style.qfont("font.panel_title"))
        heading.addWidget(title)
        heading.addWidget(self.selector, 1)
        heading.addWidget(self.go_button)
        layout.addLayout(heading)
        layout.addWidget(self.summary)

    def apply_items(
        self,
        items: tuple[DataMappingCoverageItem, ...],
        selected_group_key: str,
        preferred_column_key: str = "",
    ) -> None:
        """Show canonical coverage items for the selected editor group."""
        self._items = tuple(
            item for item in items if item.mapping_group_key == selected_group_key
        )
        with QSignalBlocker(self.selector):
            self.selector.clear()
            for item in self._items:
                intent = "Required" if item.required else "Optional"
                self.selector.addItem(
                    f"{item.mapping_attribute} — {intent}",
                    item.definition_column_key,
                )
            preferred_index = next(
                (
                    index
                    for index, item in enumerate(self._items)
                    if preferred_column_key
                    in (
                        item.source_definition_column_keys
                        or (item.definition_column_key,)
                    )
                ),
                0,
            )
            self.selector.setCurrentIndex(preferred_index if self._items else -1)
        self.selector.setEnabled(bool(self._items))
        self._sync()

    def _sync(self) -> None:
        item = self._selected_item()
        if item is None:
            self.summary.setText("No definition-backed coverage for this mapping group.")
            self.go_button.setEnabled(False)
            return
        intent = "Required" if item.required else "Optional"
        self.summary.setText(f"{item.mapping_attribute} · {intent} · {item.summary}")
        self.go_button.setEnabled(item.first_unresolved is not None)

    def _go(self) -> None:
        item = self._selected_item()
        if item is not None and item.first_unresolved is not None:
            self._on_navigate(item.first_unresolved)

    def _selected_item(self) -> DataMappingCoverageItem | None:
        index = self.selector.currentIndex()
        if not 0 <= index < len(self._items):
            return None
        return self._items[index]
