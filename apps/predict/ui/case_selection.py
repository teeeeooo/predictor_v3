"""Stable-case selection bridge for the two cached Predict surfaces."""

from __future__ import annotations

from PySide6.QtCore import QItemSelectionModel
from PySide6.QtWidgets import QTableView

from apps.predict.application.workspace_state import (
    PredictWorkspaceState,
    WorkspaceSurface,
)
from apps.predict.state.predict_session import PredictSession


class WorkspaceCaseSelectionBridge:
    """Share current case identity without sharing table selection state."""

    def __init__(
        self,
        state: PredictWorkspaceState,
        session: PredictSession,
        input_table: QTableView,
        result_table: QTableView,
    ) -> None:
        self._state = state
        self._session = session
        self._input_table = input_table
        self._result_table = result_table
        self._syncing = False

    def bind(self) -> None:
        """Bind the selection models currently installed on both tables."""
        self._input_table.selectionModel().currentChanged.connect(
            self._record_current_case
        )
        self._result_table.selectionModel().currentChanged.connect(
            self._record_current_case
        )

    def reconcile(self) -> None:
        """Drop a deleted identity and update both current rows."""
        self._state.reconcile_case_ids(self._session.case_order)
        self.apply_to(WorkspaceSurface.INPUT)
        self.apply_to(WorkspaceSurface.RESULT)

    def apply_to(self, surface: WorkspaceSurface) -> None:
        """Set only the target table's current row, preserving its selections."""
        case_id = self._state.reconcile_case_ids(self._session.case_order)
        table = (
            self._input_table
            if surface is WorkspaceSurface.INPUT
            else self._result_table
        )
        selection = table.selectionModel()
        if case_id is None:
            selection.clearCurrentIndex()
            return
        row = self._session.case_order.index(case_id)
        self._syncing = True
        try:
            selection.setCurrentIndex(
                table.model().index(row, 0),
                QItemSelectionModel.NoUpdate,
            )
        finally:
            self._syncing = False

    def _record_current_case(self, current, _previous) -> None:  # noqa: ANN001
        if self._syncing or not current.isValid():
            return
        case_order = self._session.case_order
        if 0 <= current.row() < len(case_order):
            self._state.select_case(case_order[current.row()], case_order)
