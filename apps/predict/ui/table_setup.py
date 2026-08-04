"""Visual table configuration shared by initial and rebound compositions."""

from PySide6.QtWidgets import QHeaderView

from apps.predict.ui.result_review import ResultReviewTableView
from apps.predict.ui.tables.case_table_model import CaseTableModel
from apps.predict.ui.tables.case_table_view import CaseTableView


def configure_workspace_tables(
    input_table: CaseTableView,
    input_model: CaseTableModel,
    result_table: ResultReviewTableView,
) -> None:
    """Configure independent table scrolling and Result Review anchoring."""
    input_table.setAlternatingRowColors(True)
    input_table.setSortingEnabled(False)
    input_table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
    input_table.horizontalHeader().setStretchLastSection(False)
    input_table.verticalHeader().setDefaultSectionSize(34)
    input_table.setStyleSheet("")
    for column_index, column in enumerate(input_model.columns):
        input_table.setColumnWidth(column_index, max(56, min(column.width, 150)))

    result_table.setAlternatingRowColors(True)
    result_table.setSortingEnabled(False)
    result_table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
    result_table.horizontalHeader().setStretchLastSection(False)
    result_table.verticalHeader().setDefaultSectionSize(34)
    result_table.setStyleSheet("")
    result_anchor = result_table.pinned_anchor_view
    result_anchor.setAlternatingRowColors(True)
    result_anchor.setSortingEnabled(False)
    result_anchor.verticalHeader().setDefaultSectionSize(34)
    result_anchor.setStyleSheet("")
    for column_index, width in enumerate(
        (64, 100, 100, 100, 360, 72, 72, 112, 112, 90)
    ):
        result_table.setColumnWidth(column_index, width)
