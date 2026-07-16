"""Progressively disclosed diagnostic tables for Data Definition."""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QHeaderView,
    QPushButton,
    QTabWidget,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from apps.common.ui import style
from apps.train.controllers.data_definition_controller import DataDefinitionControllerState
from apps.train.ui.data_definition_models import DataDefinitionDraftTableModel
from apps.train.ui.data_mapping_models import ReadOnlyMappingTableModel

SUMMARY_HEADERS = ("Metric", "Value")
DRAFT_CHANGE_HEADERS = ("Source", "Row Key", "Field", "Before", "After")
SAVE_PLAN_HEADERS = ("Target", "Status", "Reason")
SAVE_BLOCKER_HEADERS = ("Severity", "Code", "Target", "Message")
SAVE_RESULT_HEADERS = ("Metric", "Value")
PROJECTED_FEATURE_HEADERS = (
    "Order", "Role", "ML Name", "UI Key", "Label", "Source",
    "Mapping Key", "One-hot Group", "Zero-fill", "Active",
)
MAPPING_REQUIREMENT_HEADERS = (
    "Column Key", "ML Name", "Mapping Entity", "Mapping Attribute",
    "Trigger Column", "Rule ID",
)
ONE_HOT_HEADERS = (
    "Selector", "One-hot Group", "Emitted ML Names", "Catalog ML Names", "Parity",
)
READINESS_HEADERS = ("Name", "Status", "Message")
ISSUE_HEADERS = ("Severity", "Code", "Subject", "Message")

DraftEditCallback = Callable[[tuple[str, str], str, object], bool]
DIAGNOSTICS_MIN_HEIGHT = 320


class DataDefinitionDiagnostics(QWidget):
    """Own existing evidence tables behind one advanced-area toggle."""

    def __init__(self, on_cell_changed: DraftEditCallback, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setAccessibleName("Data Definition Advanced Diagnostics")
        self.summary_table = definition_table("Data Definition Summary")
        self.draft_table = definition_table("Data Definition Draft", editable=True)
        self.draft_changes_table = definition_table("Data Definition Draft Changes")
        self.save_plan_table = definition_table("Data Definition Save Plan")
        self.save_blockers_table = definition_table("Data Definition Save Blockers")
        self.save_result_table = definition_table("Data Definition Save Result")
        self.projected_features_table = definition_table("Projected Features")
        self.mapping_requirements_table = definition_table("Mapping Requirements")
        self.one_hot_table = definition_table("One-hot Relationships")
        self.readiness_table = definition_table("Readiness")
        self.issues_table = definition_table("Issues")
        self._on_cell_changed = on_cell_changed

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(style.spacing("space.xs"))
        self.toggle_button = QPushButton("Show Advanced Diagnostics")
        self.toggle_button.setCheckable(True)
        self.toggle_button.setAccessibleName("Toggle Data Definition Advanced Diagnostics")
        self.toggle_button.toggled.connect(self._toggle)
        layout.addWidget(self.toggle_button)
        self.tabs = self._build_tabs()
        self.tabs.setVisible(False)
        layout.addWidget(self.tabs)

    def apply_state(self, state: DataDefinitionControllerState) -> None:
        """Refresh all preserved evidence tables from controller projection."""
        self.summary_table.setModel(ReadOnlyMappingTableModel(SUMMARY_HEADERS, state.summary_rows))
        self.draft_table.setModel(
            DataDefinitionDraftTableModel(
                state.draft_headers,
                state.draft_row_identities,
                state.draft_rows,
                on_cell_changed=self._on_cell_changed,
            )
        )
        models = (
            (self.draft_changes_table, DRAFT_CHANGE_HEADERS, state.draft_change_rows),
            (self.save_plan_table, SAVE_PLAN_HEADERS, state.save_plan_rows),
            (self.save_blockers_table, SAVE_BLOCKER_HEADERS, state.save_blocker_rows),
            (self.save_result_table, SAVE_RESULT_HEADERS, state.save_result_rows),
            (self.projected_features_table, PROJECTED_FEATURE_HEADERS, state.projected_feature_rows),
            (
                self.mapping_requirements_table,
                MAPPING_REQUIREMENT_HEADERS,
                state.mapping_requirement_rows or (("none", "", "", "", "", ""),),
            ),
            (self.one_hot_table, ONE_HOT_HEADERS, state.one_hot_rows),
            (self.readiness_table, READINESS_HEADERS, state.readiness_rows),
            (self.issues_table, ISSUE_HEADERS, state.issue_rows),
        )
        for table, headers, rows in models:
            table.setModel(ReadOnlyMappingTableModel(headers, rows))
        for table in self.read_only_tables():
            table.resizeColumnsToContents()
        self.draft_table.resizeColumnsToContents()

    def read_only_tables(self) -> tuple[QTableView, ...]:
        return (
            self.summary_table,
            self.draft_changes_table,
            self.save_plan_table,
            self.save_blockers_table,
            self.save_result_table,
            self.projected_features_table,
            self.mapping_requirements_table,
            self.one_hot_table,
            self.readiness_table,
            self.issues_table,
        )

    def _build_tabs(self) -> QTabWidget:
        tabs = QTabWidget(self)
        tabs.setAccessibleName("Data Definition diagnostic reports")
        tabs.setMinimumHeight(DIAGNOSTICS_MIN_HEIGHT)
        entries = (
            ("Raw Draft", self.draft_table),
            ("Summary", self.summary_table),
            ("Draft Changes", self.draft_changes_table),
            ("Save Plan", self.save_plan_table),
            ("Save Blockers", self.save_blockers_table),
            ("Save Result", self.save_result_table),
            ("Projected Features", self.projected_features_table),
            ("Mapping Requirements", self.mapping_requirements_table),
            ("One-hot", self.one_hot_table),
            ("Readiness", self.readiness_table),
            ("Issues", self.issues_table),
        )
        for title, table in entries:
            tabs.addTab(_table_page(table), title)
        return tabs

    def _toggle(self, checked: bool) -> None:
        self.tabs.setVisible(checked)
        self.toggle_button.setText(
            "Hide Advanced Diagnostics" if checked else "Show Advanced Diagnostics"
        )


def definition_table(accessible_name: str, *, editable: bool = False) -> QTableView:
    """Build a Data Definition table with the existing model/view convention."""
    table = QTableView()
    table.setObjectName(accessible_name.replace(" ", ""))
    table.setAccessibleName(accessible_name)
    table.setEditTriggers(
        QAbstractItemView.DoubleClicked
        | QAbstractItemView.EditKeyPressed
        | QAbstractItemView.SelectedClicked
        if editable
        else QAbstractItemView.NoEditTriggers
    )
    table.setSelectionBehavior(
        QAbstractItemView.SelectItems if editable else QAbstractItemView.SelectRows
    )
    table.setSelectionMode(
        QAbstractItemView.ExtendedSelection if editable else QAbstractItemView.SingleSelection
    )
    table.setAlternatingRowColors(True)
    table.verticalHeader().setVisible(True)
    table.horizontalHeader().setStretchLastSection(True)
    table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
    return table


def _table_page(table: QTableView) -> QFrame:
    page = QFrame()
    layout = QVBoxLayout(page)
    layout.setContentsMargins(
        style.spacing("space.xs"),
        style.spacing("space.xs"),
        style.spacing("space.xs"),
        style.spacing("space.xs"),
    )
    layout.addWidget(table)
    return page
