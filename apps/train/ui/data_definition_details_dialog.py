"""Read-only on-demand Details dialog for one Data Definition snapshot."""

from __future__ import annotations

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from apps.common.ui import style
from apps.train.controllers.data_definition_details_projection import (
    DataDefinitionDetailsProjection,
)
from apps.train.ui.data_definition.dialog_support import schedule_initial_focus
from apps.train.ui.data_definition_diagnostics import definition_table
from apps.train.ui.data_mapping_models import ReadOnlyMappingTableModel


DETAIL_HEADERS = ("Property", "Value")


class DataDefinitionDetailsDialog(QDialog):
    """Render a stable, immutable Details projection without edit controls."""

    def __init__(
        self,
        projection: DataDefinitionDetailsProjection,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.projection = projection
        self.setWindowTitle("Definition Details")
        self.setAccessibleName("Data Definition Details")
        self.setModal(True)
        self.setObjectName("DataDefinitionDetailsDialog")
        self.setStyleSheet(style.panel_stylesheet())
        self.escape_shortcut = QShortcut(QKeySequence(Qt.Key_Escape), self)
        self.escape_shortcut.setContext(Qt.WindowShortcut)
        self.escape_shortcut.activated.connect(self.reject)
        self._build()
        self._apply_projection()
        self._fit_to_parent(parent)
        schedule_initial_focus(self.close_button)

    def _build(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(*([style.spacing("space.outer")] * 4))
        layout.setSpacing(style.spacing("space.sm"))

        heading = QLabel("Definition Details", self)
        heading.setObjectName("PanelTitle")
        heading.setFont(style.qfont("font.window_title"))
        heading.setAccessibleName("Definition Details title")
        layout.addWidget(heading)

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setAccessibleName("Definition Details content")
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QScrollArea.NoFrame)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        content = QWidget(self.scroll_area)
        content.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(style.spacing("space.sm"))

        identity_row = QHBoxLayout()
        self.title_label = QLabel(self)
        self.title_label.setAccessibleName("Definition Details label")
        self.title_label.setFont(style.qfont("font.panel_title"))
        self.title_label.setWordWrap(True)
        identity_row.addWidget(self.title_label, 1)
        self.status_label = QLabel(self)
        self.status_label.setAccessibleName("Definition Details status")
        identity_row.addWidget(self.status_label, 0, Qt.AlignTop)
        content_layout.addLayout(identity_row)

        self.key_label = QLabel(self)
        self.key_label.setAccessibleName("Definition Details internal key")
        self.key_label.setTextInteractionFlags(
            Qt.TextSelectableByKeyboard | Qt.TextSelectableByMouse
        )
        content_layout.addWidget(self.key_label)
        self.description_label = QLabel(self)
        self.description_label.setAccessibleName("Definition Details description")
        self.description_label.setWordWrap(True)
        self.description_label.setTextInteractionFlags(
            Qt.TextSelectableByKeyboard | Qt.TextSelectableByMouse
        )
        content_layout.addWidget(self.description_label)

        self.facts_widget = QWidget(content)
        self.facts_widget.setAccessibleName("Definition Details practical facts")
        self.facts_layout = QGridLayout(self.facts_widget)
        self.facts_layout.setContentsMargins(0, 0, 0, 0)
        self.facts_layout.setHorizontalSpacing(style.spacing("space.md"))
        self.facts_layout.setVerticalSpacing(style.spacing("space.xs"))
        content_layout.addWidget(self.facts_widget)

        self.technical_toggle = QPushButton("Technical details ▸", content)
        self.technical_toggle.setCheckable(True)
        self.technical_toggle.setAccessibleName(
            "Toggle Definition Details technical details"
        )
        self.technical_toggle.toggled.connect(self._toggle_technical_details)
        content_layout.addWidget(self.technical_toggle, 0, Qt.AlignLeft)

        self.technical_table = definition_table(
            "Definition Details Technical Details"
        )
        self.technical_table.setWordWrap(True)
        self.technical_table.setTextElideMode(Qt.ElideNone)
        self.technical_table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.technical_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.technical_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.technical_table.setFocusPolicy(Qt.NoFocus)
        self.technical_table.setVisible(False)
        technical_header = self.technical_table.horizontalHeader()
        technical_header.setStretchLastSection(False)
        content_layout.addWidget(self.technical_table)

        content_layout.addStretch(1)
        self.scroll_area.setWidget(content)
        layout.addWidget(self.scroll_area, 1)

        actions = QHBoxLayout()
        actions.addStretch(1)
        self.close_button = QPushButton("Close", self)
        self.close_button.setAccessibleName("Close Data Definition Details")
        self.close_button.setDefault(True)
        self.close_button.clicked.connect(self.accept)
        actions.addWidget(self.close_button)
        layout.addLayout(actions)
        self.setTabOrder(self.technical_toggle, self.close_button)

    def _apply_projection(self) -> None:
        projection = self.projection
        self.title_label.setText(projection.title)
        self.status_label.setText(projection.status)
        self.status_label.setVisible(bool(projection.status))
        self.status_label.setStyleSheet(_status_stylesheet(projection.status))
        self.key_label.setText(
            f"Internal key: {projection.internal_key}"
            if projection.internal_key
            else ""
        )
        self.key_label.setVisible(bool(projection.internal_key))
        self.description_label.setText(projection.description)
        for fact_index, fact in enumerate(projection.facts):
            name = QLabel(fact.label, self.facts_widget)
            name.setStyleSheet(f"color: {style.color('text.muted')};")
            name.setAccessibleName(f"Definition Details {fact.label} label")
            value = QLabel(fact.value, self.facts_widget)
            value.setAccessibleName(f"Definition Details {fact.label}")
            value.setWordWrap(True)
            value.setTextInteractionFlags(
                Qt.TextSelectableByKeyboard | Qt.TextSelectableByMouse
            )
            row = fact_index
            self.facts_layout.addWidget(name, row, 0)
            self.facts_layout.addWidget(value, row, 1)
        self.facts_layout.setColumnStretch(1, 1)
        self.facts_widget.setVisible(bool(projection.facts))

        self.technical_table.setModel(
            ReadOnlyMappingTableModel(DETAIL_HEADERS, projection.technical_details)
        )
        self.technical_table.resizeColumnsToContents()
        self.technical_table.setColumnWidth(
            0, max(160, min(220, self.technical_table.columnWidth(0)))
        )
        self.technical_table.setColumnWidth(
            1, max(300, min(440, self.technical_table.columnWidth(1)))
        )
        self.technical_table.resizeRowsToContents()
        self.technical_table.setVisible(False)
        self.technical_toggle.setVisible(bool(projection.technical_details))
        self.technical_toggle.setEnabled(bool(projection.technical_details))

    def _toggle_technical_details(self, checked: bool) -> None:
        self.technical_toggle.setText(
            "Technical details ▾" if checked else "Technical details ▸"
        )
        self.technical_table.setVisible(checked)
        self.technical_table.setFocusPolicy(
            Qt.StrongFocus if checked else Qt.NoFocus
        )
        if checked:
            self._fit_technical_table_height()
        QTimer.singleShot(0, self._clamp_scroll_position)

    def _fit_technical_table_height(self) -> None:
        model = self.technical_table.model()
        if model is None:
            return
        height = self.technical_table.frameWidth() * 2
        height += self.technical_table.horizontalHeader().height()
        height += sum(
            self.technical_table.rowHeight(row)
            for row in range(model.rowCount())
        )
        self.technical_table.setFixedHeight(max(64, height + 6))

    def _clamp_scroll_position(self) -> None:
        bar = self.scroll_area.verticalScrollBar()
        bar.setValue(min(bar.value(), bar.maximum()))

    def _fit_to_parent(self, parent: QWidget | None) -> None:
        parent_width = parent.width() if parent is not None else 0
        parent_height = parent.height() if parent is not None else 0
        width = min(720, max(520, parent_width - 96 if parent_width else 720))
        height = min(600, max(360, parent_height - 96 if parent_height else 600))
        self.setMinimumSize(min(520, width), min(360, height))
        self.setMaximumSize(width, height)
        self.resize(width, height)


def _status_stylesheet(status: str) -> str:
    return style.status_badge_stylesheet(
        {
            "Active": "good",
            "Changed": "warning",
            "Blocked": "error",
        }.get(status, "neutral")
    )
