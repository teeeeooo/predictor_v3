"""Structured validation-issue navigation for Data Mapping tables."""

from __future__ import annotations

from collections.abc import Callable, Sequence

from PySide6.QtCore import QModelIndex, Qt

from apps.train.application.data_mapping import DataMappingCellTarget, DataMappingIssueTarget
from apps.train.controllers.data_mapping.presentation import DataMappingControllerState
from apps.train.controllers.data_mapping_controller import DataMappingController
from apps.train.ui.data_mapping.table_view import DataMappingTableView


def navigate_to_issue(
    index: QModelIndex,
    targets: Sequence[DataMappingIssueTarget | None],
    *,
    controller: DataMappingController,
    apply_state: Callable[[DataMappingControllerState], None],
    row_table: DataMappingTableView,
) -> None:
    """Select and focus the structured target without parsing issue text."""
    if not index.isValid() or index.row() >= len(targets):
        return
    target = targets[index.row()]
    if target is None:
        return
    apply_state(controller.refresh(target.group_key))
    model = row_table.model()
    if target.row_index is None or model is None or not model.rowCount():
        return
    column = target.column_index if target.column_index is not None else 0
    row = min(target.row_index, model.rowCount() - 1)
    column = min(column, model.columnCount() - 1)
    cell = model.index(row, column)
    row_table.setCurrentIndex(cell)
    row_table.scrollTo(cell)
    row_table.setFocus(Qt.OtherFocusReason)


def focus_cell_target(
    target: DataMappingCellTarget,
    state: DataMappingControllerState,
    row_table: DataMappingTableView,
) -> bool:
    """Resolve one stable row/attribute identity against the current snapshot."""
    model = row_table.model()
    if model is None:
        return False
    matches = tuple(
        index for index, item in enumerate(state.values) if item.row_key == target.row_key
    )
    row = (
        matches[target.row_occurrence]
        if target.row_occurrence < len(matches)
        else None
    )
    if row is None or target.attribute_key not in state.value_headers:
        return False
    cell = model.index(row, state.value_headers.index(target.attribute_key))
    row_table.setCurrentIndex(cell)
    row_table.scrollTo(cell)
    row_table.setFocus(Qt.OtherFocusReason)
    return True


def focus_attribute(
    attribute: str,
    state: DataMappingControllerState,
    row_table: DataMappingTableView,
) -> bool:
    """Display one exact attribute when coverage has no unresolved target."""
    model = row_table.model()
    if model is None or not model.rowCount() or attribute not in state.value_headers:
        return False
    cell = model.index(0, state.value_headers.index(attribute))
    row_table.setCurrentIndex(cell)
    row_table.scrollTo(cell)
    return True
