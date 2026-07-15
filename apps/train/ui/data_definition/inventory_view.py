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
    QWidget,
)

from apps.common.ui import style

NORMAL_WIDTHS = (0, 170, 120, 82, 96, 96)
COMPACT_WIDTHS = (0, 145, 105, 76, 90, 84)


class DataDefinitionInventoryView(QFrame):
    """Own only the default inventory card and six-column width convention."""

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
        widths = COMPACT_WIDTHS if self._compact else NORMAL_WIDTHS
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        for column, width in enumerate(widths[1:], start=1):
            header.setSectionResizeMode(column, QHeaderView.Fixed)
            header.resizeSection(column, width)
