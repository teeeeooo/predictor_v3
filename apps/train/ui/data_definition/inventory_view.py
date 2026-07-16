"""Full-width Definition Inventory and its explicit display-column policy."""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHeaderView,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableView,
    QVBoxLayout,
    QSizePolicy,
    QWidget,
)

from apps.common.ui import style

NORMAL_COLUMNS = (0, 1, 2, 3, 4, 5, 6, 7)
COMPACT_COLUMNS = (0, 1, 2, 3, 4, 7)
NORMAL_WIDTHS = {
    0: 180,
    1: 178,
    2: 92,
    3: 128,
    4: 84,
    5: 104,
    6: 80,
    7: 100,
}
COMPACT_WIDTHS = {
    0: 160,
    1: 160,
    2: 88,
    3: 122,
    4: 84,
    7: 100,
}


class DataDefinitionInventoryView(QFrame):
    """Own inventory visibility and bounded normal/compact column policy."""

    def __init__(
        self,
        table: QTableView,
        on_clear_filters: Callable[[], None],
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("Panel")
        self.setAccessibleName("Data Definition Inventory")
        self.setStyleSheet(style.panel_stylesheet())
        self.table = table
        self._compact = False
        self._applying_widths = False
        self._section_widths: dict[bool, dict[int, int]] = {
            False: dict(NORMAL_WIDTHS),
            True: dict(COMPACT_WIDTHS),
        }
        self.table.horizontalHeader().sectionResized.connect(self._remember_width)
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.state_label = QLabel(self)
        self.state_label.setAccessibleName("Data Definition inventory state")
        self.state_label.setWordWrap(True)
        self.clear_button = QPushButton("Clear search and filters", self)
        self.clear_button.setAccessibleName("Clear Data Definition search and filters")
        self.clear_button.clicked.connect(on_clear_filters)
        self.clear_button.setVisible(False)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(*([style.spacing("space.panel")] * 4))
        layout.setSpacing(style.spacing("space.xs"))
        heading_row = QHBoxLayout()
        heading = QLabel("Definition Inventory", self)
        heading.setObjectName("PanelTitle")
        heading.setFont(style.qfont("font.panel_title"))
        heading_row.addWidget(heading)
        heading_row.addStretch(1)
        heading_row.addWidget(self.clear_button)
        layout.addLayout(heading_row)
        layout.addWidget(self.state_label)
        layout.addWidget(self.table, 1)
        self._configure_table()

    def apply_state(self, message: str, *, no_match: bool) -> None:
        self.state_label.setText(message)
        self.state_label.setAccessibleDescription(message)
        self.clear_button.setVisible(no_match)

    def apply_compact(self, compact: bool) -> None:
        if compact == self._compact:
            return
        self._compact = compact
        self._apply_widths()
        self.table.setMinimumHeight(190 if compact else 220)

    def refresh_column_policy(self) -> None:
        """Reapply per-section modes after the table model changes."""
        self._apply_widths()

    def _configure_table(self) -> None:
        self.table.verticalHeader().setVisible(False)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.setMinimumHeight(220)
        self._apply_widths()

    def _apply_widths(self) -> None:
        header = self.table.horizontalHeader()
        model = self.table.model()
        column_count = model.columnCount() if model is not None else 0
        visible_columns = set(COMPACT_COLUMNS if self._compact else NORMAL_COLUMNS)
        widths = self._section_widths[self._compact]
        self._applying_widths = True
        try:
            for column in range(column_count):
                visible = column in visible_columns
                self.table.setColumnHidden(column, not visible)
                if not visible:
                    continue
                header.setSectionResizeMode(column, QHeaderView.Interactive)
                header.resizeSection(column, widths[column])
        finally:
            self._applying_widths = False

    def _remember_width(self, section: int, _old_size: int, new_size: int) -> None:
        if not self._applying_widths and section in self._section_widths[self._compact]:
            self._section_widths[self._compact][section] = new_size
