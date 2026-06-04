"""Controller for explicit-run calculator batch tables."""

from __future__ import annotations

from typing import Protocol

from ui_tk.batch_models import BatchRowState
from ui_tk.batch_case_table import BatchCaseTable


class BatchRowHandler(Protocol):
    def calculate_row(self, row: dict[str, str]) -> "BatchCalculationResult":
        ...


class BatchCalculationResult(Protocol):
    values: dict[str, str]
    state: BatchRowState


class BatchCalculationController:
    def __init__(self, table: BatchCaseTable, handler: BatchRowHandler) -> None:
        self._table = table
        self._handler = handler

    def run_batch(self) -> None:
        for row_index, row in enumerate(self._table.input_rows()):
            result = self._handler.calculate_row(row)
            self._table.set_row_results(row_index, result.values)

    def clear_results(self) -> None:
        self._table.clear_results()
