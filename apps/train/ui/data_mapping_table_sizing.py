"""Semantic column sizing policies for the Data Mapping tables."""

from __future__ import annotations

from collections.abc import Mapping

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QAbstractItemView, QHeaderView, QTableView

TABLE_COLUMN_MIN_WIDTH = 72
TABLE_COLUMN_MAX_WIDTH = 240
ROW_COUNT_COLUMN_WIDTH = 58


def configure_table_defaults(table: QTableView) -> None:
    """Set neutral interactive defaults without position-based stretching."""
    header = table.horizontalHeader()
    header.setStretchLastSection(False)
    header.setSectionResizeMode(QHeaderView.Interactive)
    table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
    table.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)


def apply_primary_table_sizing(table: QTableView) -> None:
    """Fit every mapping data column by the same bounded content policy."""
    configure_table_defaults(table)
    _fit_bounded_columns(table)


def apply_group_navigation_sizing(table: QTableView) -> None:
    """Stretch the group label while keeping row counts compact."""
    _apply_named_policy(
        table,
        stretch_headers=("Group",),
        fixed_headers={"Rows": ROW_COUNT_COLUMN_WIDTH},
    )


def apply_secondary_table_sizing(
    table: QTableView,
    *,
    description_header: str,
) -> None:
    """Stretch one explicitly named descriptive column and bound the rest."""
    _apply_named_policy(table, stretch_headers=(description_header,))


def _apply_named_policy(
    table: QTableView,
    *,
    stretch_headers: tuple[str, ...] = (),
    fixed_headers: Mapping[str, int] | None = None,
) -> None:
    configure_table_defaults(table)
    _fit_bounded_columns(table)
    header = table.horizontalHeader()
    for label in stretch_headers:
        section = _section_for_header(table, label)
        if section is not None:
            header.setSectionResizeMode(section, QHeaderView.Stretch)
    for label, width in (fixed_headers or {}).items():
        section = _section_for_header(table, label)
        if section is not None:
            header.setSectionResizeMode(section, QHeaderView.Fixed)
            table.setColumnWidth(section, width)


def _fit_bounded_columns(table: QTableView) -> None:
    model = table.model()
    if model is None:
        return
    table.resizeColumnsToContents()
    header = table.horizontalHeader()
    for column in range(model.columnCount()):
        header.setSectionResizeMode(column, QHeaderView.Interactive)
        width = table.columnWidth(column)
        table.setColumnWidth(
            column,
            max(TABLE_COLUMN_MIN_WIDTH, min(width, TABLE_COLUMN_MAX_WIDTH)),
        )


def _section_for_header(table: QTableView, label: str) -> int | None:
    model = table.model()
    if model is None:
        return None
    for section in range(model.columnCount()):
        if model.headerData(section, Qt.Horizontal, Qt.DisplayRole) == label:
            return section
    return None
