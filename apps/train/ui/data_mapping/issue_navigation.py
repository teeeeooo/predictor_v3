"""Structured validation-issue navigation for Data Mapping tables."""

from __future__ import annotations

from collections.abc import Callable, Sequence

from PySide6.QtCore import QModelIndex, Qt

from apps.train.application.data_mapping import (
    DataMappingCellTarget,
    DataMappingIssueTarget,
    row_index_for_identity,
)
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
    state = controller.refresh(target.group_key)
    apply_state(state)
    model = row_table.model()
    if model is None or not model.rowCount() or target.attribute_key not in state.value_headers:
        return
    row = _resolved_row_index(
        tuple(item.row_key for item in state.values),
        target.row_key,
        target.row_occurrence,
        target.row_index,
    )
    if row is None:
        return
    column = state.value_headers.index(target.attribute_key)
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
    row = row_index_for_identity(
        tuple(item.row_key for item in state.values),
        target.row_key,
        target.row_occurrence,
    )
    if row is None or target.attribute_key not in state.value_headers:
        return False
    cell = model.index(row, state.value_headers.index(target.attribute_key))
    row_table.setCurrentIndex(cell)
    row_table.scrollTo(cell)
    row_table.setFocus(Qt.OtherFocusReason)
    return True


def _resolved_row_index(
    row_keys: tuple[str, ...],
    row_key: str,
    row_occurrence: int | None,
    row_index: int | None,
) -> int | None:
    if row_occurrence is not None:
        return row_index_for_identity(row_keys, row_key, row_occurrence)
    if row_index is not None and 0 <= row_index < len(row_keys):
        return row_index
    return None


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
