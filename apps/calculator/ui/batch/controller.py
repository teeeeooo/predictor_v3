"""Controller for calculator batch row recalculation."""

from __future__ import annotations

from typing import Protocol

from dataclasses import dataclass

from apps.calculator.ui.batch.models import BatchRowState
from apps.calculator.ui.batch.case_table import BatchCaseTable


class BatchRowHandler(Protocol):
    def calculate_row(self, row: dict[str, str]) -> "BatchCalculationResult":
        ...


class BatchCalculationResult(Protocol):
    values: dict[str, str]
    state: BatchRowState


@dataclass(frozen=True)
class BatchCalculationSummary:
    valid_rows: int
    blank_rows: int
    error_rows: int


class BatchCalculationController:
    def __init__(self, table: BatchCaseTable, handler: BatchRowHandler) -> None:
        self._table = table
        self._handler = handler

    def recalculate(self) -> BatchCalculationSummary:
        valid = 0
        blank = 0
        error = 0
        for row_index, row in enumerate(self._table.input_rows()):
            result = self._handler.calculate_row(row)
            self._table.set_row_results(row_index, result.values)
            if result.state is BatchRowState.OK:
                valid += 1
            elif result.state is BatchRowState.ERROR:
                error += 1
            else:
                blank += 1
        return BatchCalculationSummary(valid, blank, error)

    def run_batch(self) -> BatchCalculationSummary:
        """Compatibility alias; UI entry now uses auto-calc."""
        return self.recalculate()

    def clear_results(self) -> None:
        self._table.clear_results()
