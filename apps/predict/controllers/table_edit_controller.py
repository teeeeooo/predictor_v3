"""Controller for Predict unified case-table row lifecycle commands."""

from __future__ import annotations

from dataclasses import dataclass

from apps.predict.state.predict_session import PredictSession


@dataclass(frozen=True)
class RowRemovalGroup:
    """Contiguous row removal span and matching case ids."""

    first_row: int
    last_row: int
    case_ids: tuple[str, ...]


class TableEditController:
    """Mutate Predict session row state behind the workspace boundary."""

    def __init__(self, session: PredictSession) -> None:
        self._session = session

    def ensure_initial_rows(self, count: int) -> None:
        """Append initial empty rows when the session starts empty."""
        if len(self._session.case_store) == 0 and count > 0:
            self._session.case_store.append_empty_rows(count)

    def append_row_span(self, count: int = 1) -> tuple[int, int] | None:
        """Return the model row span that would be inserted."""
        if count <= 0:
            return None
        first_row = len(self._session.case_store)
        return first_row, first_row + count - 1

    def append_empty_rows(self, count: int = 1) -> None:
        """Append empty rows to the session."""
        if count > 0:
            self._session.case_store.append_empty_rows(count)

    def reset_rows(self, initial_count: int) -> list[str]:
        """Reset all cases/results and append a fresh initial row set."""
        removed = self._session.case_store.remove_rows(self._session.case_order)
        self._session.remove_results_for_cases(removed)
        self._session.case_store.append_empty_rows(initial_count)
        return removed

    def removal_groups_for_indexes(
        self,
        row_indexes: list[int],
    ) -> list[RowRemovalGroup]:
        """Return contiguous descending removal groups for valid row indexes."""
        valid_rows = sorted(
            {row for row in row_indexes if 0 <= row < len(self._session.case_store)},
            reverse=True,
        )
        groups: list[list[int]] = []
        for row in valid_rows:
            if not groups or groups[-1][-1] - 1 != row:
                groups.append([row])
            else:
                groups[-1].append(row)

        removal_groups: list[RowRemovalGroup] = []
        for group in groups:
            first_row = group[-1]
            last_row = group[0]
            case_ids = tuple(
                self._session.case_order[row]
                for row in range(first_row, last_row + 1)
            )
            removal_groups.append(RowRemovalGroup(first_row, last_row, case_ids))
        return removal_groups

    def remove_case_ids(self, case_ids: tuple[str, ...]) -> list[str]:
        """Remove cases/results by id and return removed case ids."""
        removed = self._session.case_store.remove_rows(case_ids)
        self._session.remove_results_for_cases(removed)
        return removed
