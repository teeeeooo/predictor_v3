"""Coordinated Qt notifications for two projections of one session."""

from __future__ import annotations

from apps.predict.ui.result_review import ResultReviewTableModel
from apps.predict.ui.tables.case_table_model import CaseTableModel


class WorkspaceModelGroup:
    """Bracket canonical row mutations across both read models."""

    def __init__(
        self,
        input_model: CaseTableModel,
        result_model: ResultReviewTableModel,
    ) -> None:
        self.rebind(input_model, result_model)

    def rebind(
        self,
        input_model: CaseTableModel,
        result_model: ResultReviewTableModel,
    ) -> None:
        self._input = input_model
        self._result = result_model

    def begin_insert(self, first_row: int, last_row: int) -> None:
        self._input.begin_insert_rows(first_row, last_row)
        self._result.begin_insert_rows(first_row, last_row)

    def end_insert(self) -> None:
        self._input.end_insert_rows()
        self._result.end_insert_rows()

    def begin_remove(self, first_row: int, last_row: int) -> None:
        self._input.begin_remove_rows(first_row, last_row)
        self._result.begin_remove_rows(first_row, last_row)

    def end_remove(self) -> None:
        self._input.end_remove_rows()
        self._result.end_remove_rows()

    def begin_reset(self) -> None:
        self._input.begin_reset_model()
        self._result.begin_reset_model()

    def end_reset(self) -> None:
        self._input.end_reset_model()
        self._result.end_reset_model()
