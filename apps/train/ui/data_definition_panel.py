"""Read-only Data Definition Train/Admin panel."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QGridLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QScrollArea,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from apps.common.ui import style
from apps.train.controllers.data_definition_controller import (
    DataDefinitionController,
    DataDefinitionControllerState,
)
from apps.train.ui.data_definition_models import DataDefinitionDraftTableModel
from apps.train.ui.data_mapping_models import ReadOnlyMappingTableModel

SUMMARY_HEADERS = ("Metric", "Value")
DRAFT_CHANGE_HEADERS = ("Source", "Row Key", "Field", "Before", "After")
SAVE_PLAN_HEADERS = ("Target", "Status", "Reason")
SAVE_BLOCKER_HEADERS = ("Severity", "Code", "Target", "Message")
PROJECTED_FEATURE_HEADERS = (
    "Order",
    "Role",
    "ML Name",
    "UI Key",
    "Label",
    "Source",
    "Mapping Key",
    "One-hot Group",
    "Zero-fill",
    "Active",
)
MAPPING_REQUIREMENT_HEADERS = (
    "Column Key",
    "ML Name",
    "Mapping Entity",
    "Mapping Attribute",
    "Trigger Column",
    "Rule ID",
)
ONE_HOT_HEADERS = (
    "Selector",
    "One-hot Group",
    "Emitted ML Names",
    "Catalog ML Names",
    "Parity",
)
READINESS_HEADERS = ("Name", "Status", "Message")
ISSUE_HEADERS = ("Severity", "Code", "Subject", "Message")


class DataDefinitionPanel(QWidget):
    """Read-only Data Definition report surface."""

    def __init__(
        self,
        parent: QWidget | None = None,
        controller: DataDefinitionController | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("DataDefinitionPanel")
        self.setAccessibleName("Data Definition")
        self._controller = controller or DataDefinitionController()
        self.status_label = QLabel("Data Definition report pending.")
        self.status_label.setObjectName("PanelTitle")
        self.summary_table = _table("Data Definition Summary")
        self.draft_table = _table("Data Definition Draft", editable=True)
        self.draft_changes_table = _table("Data Definition Draft Changes")
        self.save_plan_table = _table("Data Definition Save Plan")
        self.save_blockers_table = _table("Data Definition Save Blockers")
        self.projected_features_table = _table("Projected Features")
        self.mapping_requirements_table = _table("Mapping Requirements")
        self.one_hot_table = _table("One-hot Relationships")
        self.readiness_table = _table("Readiness")
        self.issues_table = _table("Issues")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            style.spacing("space.outer"),
            style.spacing("space.outer"),
            style.spacing("space.outer"),
            style.spacing("space.outer"),
        )
        layout.setSpacing(style.spacing("space.sm"))
        layout.addWidget(self._build_command_bar())
        layout.addWidget(self._build_body(), 1)
        self.refresh()

    def refresh(self) -> None:
        """Reload report state through the controller."""
        self._apply_state(self._controller.refresh())

    def _build_command_bar(self) -> QFrame:
        panel = QFrame(self)
        panel.setObjectName("Panel")
        panel.setStyleSheet(style.panel_stylesheet())
        layout = QGridLayout(panel)
        layout.setContentsMargins(
            style.spacing("space.panel"),
            style.spacing("space.sm"),
            style.spacing("space.panel"),
            style.spacing("space.sm"),
        )
        refresh_button = QPushButton("Refresh")
        refresh_button.setAccessibleName("Refresh Data Definition")
        refresh_button.clicked.connect(self.refresh)
        reset_button = QPushButton("Reset Draft")
        reset_button.setAccessibleName("Reset Data Definition Draft")
        reset_button.clicked.connect(self._reset_draft)
        layout.addWidget(refresh_button, 0, 0)
        layout.addWidget(reset_button, 0, 1)
        layout.addWidget(self.status_label, 0, 2)
        layout.setColumnStretch(2, 1)
        return panel

    def _build_body(self) -> QScrollArea:
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        container = QWidget(scroll)
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(style.spacing("space.sm"))
        layout.addWidget(self._panel("Summary", self.summary_table, height=190))
        layout.addWidget(self._panel("Draft", self.draft_table, height=320))
        layout.addWidget(self._panel("Draft Changes", self.draft_changes_table, height=160))
        layout.addWidget(self._panel("Save Plan Preview", self.save_plan_table, height=150))
        layout.addWidget(self._panel("Save Blockers", self.save_blockers_table, height=170))
        layout.addWidget(self._panel("Projected Features", self.projected_features_table))
        layout.addWidget(self._panel("Mapping Requirements", self.mapping_requirements_table))
        layout.addWidget(self._panel("One-hot Relationships", self.one_hot_table, height=180))
        layout.addWidget(self._panel("Readiness", self.readiness_table, height=180))
        layout.addWidget(self._panel("Issues", self.issues_table, height=180))
        scroll.setWidget(container)
        return scroll

    def _panel(self, title: str, table: QTableView, *, height: int = 260) -> QFrame:
        panel = QFrame(self)
        panel.setObjectName("Panel")
        panel.setAccessibleName(f"Data Definition {title}")
        panel.setStyleSheet(style.panel_stylesheet())
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(
            style.spacing("space.panel"),
            style.spacing("space.panel"),
            style.spacing("space.panel"),
            style.spacing("space.panel"),
        )
        layout.setSpacing(style.spacing("space.sm"))
        heading = QLabel(title)
        heading.setObjectName("PanelTitle")
        heading.setFont(style.qfont("font.panel_title"))
        table.setMinimumHeight(height)
        layout.addWidget(heading)
        layout.addWidget(table, 1)
        return panel

    def _apply_state(self, state: DataDefinitionControllerState) -> None:
        self.status_label.setText(f"{state.message} ({state.status})")
        self.summary_table.setModel(
            ReadOnlyMappingTableModel(SUMMARY_HEADERS, state.summary_rows)
        )
        self.draft_table.setModel(
            DataDefinitionDraftTableModel(
                state.draft_headers,
                state.draft_row_identities,
                state.draft_rows,
                on_cell_changed=self._edit_draft_cell,
            )
        )
        self.draft_changes_table.setModel(
            ReadOnlyMappingTableModel(DRAFT_CHANGE_HEADERS, state.draft_change_rows)
        )
        self.save_plan_table.setModel(
            ReadOnlyMappingTableModel(SAVE_PLAN_HEADERS, state.save_plan_rows)
        )
        self.save_blockers_table.setModel(
            ReadOnlyMappingTableModel(SAVE_BLOCKER_HEADERS, state.save_blocker_rows)
        )
        self.projected_features_table.setModel(
            ReadOnlyMappingTableModel(
                PROJECTED_FEATURE_HEADERS,
                state.projected_feature_rows,
            )
        )
        self.mapping_requirements_table.setModel(
            ReadOnlyMappingTableModel(
                MAPPING_REQUIREMENT_HEADERS,
                state.mapping_requirement_rows or (("none", "", "", "", "", ""),),
            )
        )
        self.one_hot_table.setModel(
            ReadOnlyMappingTableModel(ONE_HOT_HEADERS, state.one_hot_rows)
        )
        self.readiness_table.setModel(
            ReadOnlyMappingTableModel(READINESS_HEADERS, state.readiness_rows)
        )
        self.issues_table.setModel(
            ReadOnlyMappingTableModel(ISSUE_HEADERS, state.issue_rows)
        )
        for table in _tables(self):
            table.resizeColumnsToContents()
        self.draft_table.resizeColumnsToContents()

    def _reset_draft(self) -> None:
        self._apply_state(self._controller.reset_draft())

    def _edit_draft_cell(
        self,
        row_identity: tuple[str, str],
        field_name: str,
        value: object,
    ) -> bool:
        state = self._controller.edit_cell(row_identity, field_name, value)
        self._apply_state(state)
        return state.last_action_ok


def _table(accessible_name: str, *, editable: bool = False) -> QTableView:
    table = QTableView()
    table.setObjectName(accessible_name.replace(" ", ""))
    table.setAccessibleName(accessible_name)
    if editable:
        table.setEditTriggers(
            QAbstractItemView.DoubleClicked
            | QAbstractItemView.EditKeyPressed
            | QAbstractItemView.SelectedClicked
        )
        table.setSelectionBehavior(QAbstractItemView.SelectItems)
    else:
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
    table.setSelectionMode(QAbstractItemView.ExtendedSelection)
    table.setAlternatingRowColors(True)
    table.verticalHeader().setVisible(True)
    table.horizontalHeader().setStretchLastSection(True)
    table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
    return table


def _tables(panel: DataDefinitionPanel) -> tuple[QTableView, ...]:
    return (
        panel.summary_table,
        panel.draft_changes_table,
        panel.save_plan_table,
        panel.save_blockers_table,
        panel.projected_features_table,
        panel.mapping_requirements_table,
        panel.one_hot_table,
        panel.readiness_table,
        panel.issues_table,
    )
