"""Selected-definition summary card for the task-oriented workspace."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from apps.common.ui import style
from apps.train.controllers.data_definition_summary_projection import (
    DataDefinitionSummaryProjection,
)
from apps.train.ui.data_definition_diagnostics import definition_table
from apps.train.ui.data_mapping_models import ReadOnlyMappingTableModel

DETAIL_HEADERS = ("Property", "Value")


class DataDefinitionSummaryCard(QFrame):
    """Render practical answers first and technical evidence on demand."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("Panel")
        self.setAccessibleName("Selected Data Definition summary")
        self.setStyleSheet(style.panel_stylesheet())
        self._compact = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(*([style.spacing("space.panel")] * 4))
        layout.setSpacing(style.spacing("space.xs"))
        heading = QLabel("Selected Definition", self)
        heading.setObjectName("PanelTitle")
        heading.setFont(style.qfont("font.panel_title"))
        layout.addWidget(heading)

        identity_row = QHBoxLayout()
        self.title_label = QLabel("No definition selected", self)
        self.title_label.setAccessibleName("Selected Definition label")
        self.title_label.setFont(style.qfont("font.panel_title"))
        self.title_label.setWordWrap(True)
        self.status_label = QLabel(self)
        self.status_label.setAccessibleName("Selected Definition status")
        identity_row.addWidget(self.title_label, 1)
        identity_row.addWidget(self.status_label, 0, Qt.AlignTop)
        layout.addLayout(identity_row)

        self.key_label = QLabel(self)
        self.key_label.setAccessibleName("Selected Definition internal key")
        self.key_label.setTextInteractionFlags(Qt.TextSelectableByKeyboard | Qt.TextSelectableByMouse)
        layout.addWidget(self.key_label)
        self.description_label = QLabel(self)
        self.description_label.setAccessibleName("Selected Definition description")
        self.description_label.setWordWrap(True)
        layout.addWidget(self.description_label)

        self.facts_widget = QWidget(self)
        self.facts_widget.setAccessibleName("Selected Definition practical facts")
        self.facts_layout = QGridLayout(self.facts_widget)
        self.facts_layout.setContentsMargins(0, style.spacing("space.xs"), 0, 0)
        self.facts_layout.setHorizontalSpacing(style.spacing("space.md"))
        self.facts_layout.setVerticalSpacing(style.spacing("space.xs"))
        self._fact_labels: list[tuple[QLabel, QLabel]] = []
        layout.addWidget(self.facts_widget)

        self.technical_toggle = QPushButton("Technical details ▸", self)
        self.technical_toggle.setCheckable(True)
        self.technical_toggle.setAccessibleName("Toggle Selected Definition technical details")
        self.technical_toggle.toggled.connect(self._toggle_technical_details)
        layout.addWidget(self.technical_toggle, 0, Qt.AlignLeft)
        self.technical_table = definition_table("Selected Data Definition Technical Details")
        self.technical_table.setMinimumHeight(240)
        self.technical_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.technical_table.setVisible(False)
        self.technical_table.setFocusPolicy(Qt.NoFocus)
        layout.addWidget(self.technical_table)

    def apply_projection(self, projection: DataDefinitionSummaryProjection) -> None:
        """Replace every selected-state value so stale detail cannot remain."""
        self.title_label.setText(projection.title)
        self.key_label.setText(projection.internal_key)
        self.key_label.setVisible(bool(projection.internal_key))
        self.status_label.setText(projection.status)
        self.status_label.setVisible(bool(projection.status))
        self.status_label.setStyleSheet(
            style.status_badge_stylesheet(_status_kind(projection.status))
        )
        self.description_label.setText(projection.description)
        self.description_label.setAccessibleDescription(projection.description)
        self._replace_facts(projection)
        self.technical_table.setModel(
            ReadOnlyMappingTableModel(DETAIL_HEADERS, projection.technical_details)
        )
        self.technical_table.resizeColumnsToContents()
        has_details = bool(projection.technical_details)
        self.technical_toggle.setVisible(has_details)
        if not has_details:
            self.technical_toggle.setChecked(False)

    def apply_compact(self, compact: bool) -> None:
        if compact == self._compact:
            return
        self._compact = compact
        self._arrange_facts()

    def _replace_facts(self, projection: DataDefinitionSummaryProjection) -> None:
        for name, value in self._fact_labels:
            name.deleteLater()
            value.deleteLater()
        self._fact_labels = []
        for fact in projection.facts:
            name = QLabel(fact.label, self.facts_widget)
            name.setAccessibleName(f"Selected Definition {fact.label} label")
            name.setStyleSheet(f"color: {style.color('text.muted')};")
            value = QLabel(fact.value, self.facts_widget)
            value.setAccessibleName(f"Selected Definition {fact.label}")
            value.setWordWrap(True)
            self._fact_labels.append((name, value))
        self.facts_widget.setVisible(bool(self._fact_labels))
        self._arrange_facts()

    def _arrange_facts(self) -> None:
        for name, value in self._fact_labels:
            self.facts_layout.removeWidget(name)
            self.facts_layout.removeWidget(value)
        for index, (name, value) in enumerate(self._fact_labels):
            group = 0 if self._compact else index % 2
            row = index if self._compact else index // 2
            column = group * 2
            self.facts_layout.addWidget(name, row, column)
            self.facts_layout.addWidget(value, row, column + 1)
        self.facts_layout.setColumnStretch(1, 1)
        self.facts_layout.setColumnStretch(3, 0 if self._compact else 1)

    def _toggle_technical_details(self, checked: bool) -> None:
        self.technical_toggle.setText(
            "Technical details ▾" if checked else "Technical details ▸"
        )
        self.technical_table.setVisible(checked)
        self.technical_table.setFocusPolicy(Qt.StrongFocus if checked else Qt.NoFocus)


def _status_kind(status: str) -> str:
    return {
        "Active": "good",
        "Changed": "warning",
        "Blocked": "error",
        "Inactive": "neutral",
        "Read-only": "neutral",
    }.get(status, "neutral")
