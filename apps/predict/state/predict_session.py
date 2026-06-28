"""Predict workspace session state."""

from apps.predict.state.case_store import CaseStore
from apps.predict.state.result_row import ResultRow


class PredictSession:
    """Qt-free state container for a Predict workspace."""

    def __init__(self, case_store: CaseStore | None = None) -> None:
        self.case_store = case_store or CaseStore()
        self.results_by_case_id: dict[str, ResultRow] = {}

    @property
    def case_order(self) -> tuple[str, ...]:
        """Return case ids in shared input/result row order."""
        return self.case_store.case_order

    def result_for_case(self, case_id: str) -> ResultRow:
        """Return existing result state or a pending placeholder."""
        return self.results_by_case_id.get(case_id, ResultRow(case_id=case_id))

    def set_result(self, result: ResultRow) -> None:
        """Attach result state by case_id."""
        self.case_store.get_case(result.case_id)
        self.results_by_case_id[result.case_id] = result

    def set_results(self, results: list[ResultRow]) -> None:
        """Attach several result states by case_id."""
        for result in results:
            self.set_result(result)

    def clear_result(self, case_id: str) -> None:
        """Clear result state for one case."""
        self.results_by_case_id.pop(case_id, None)

    def clear_all_results(self) -> None:
        """Clear every result state."""
        self.results_by_case_id.clear()

    def remove_results_for_cases(self, case_ids: list[str]) -> None:
        """Drop result state for removed cases."""
        for case_id in case_ids:
            self.results_by_case_id.pop(case_id, None)

    def summary_counts(self) -> dict[str, int]:
        """Return lightweight status counts for the workspace status bar."""
        total = len(self.case_store)
        completed = sum(
            1 for result in self.results_by_case_id.values() if result.status == "complete"
        )
        errors = sum(
            1 for result in self.results_by_case_id.values() if result.status == "error"
        )
        running = sum(
            1 for result in self.results_by_case_id.values() if result.status == "running"
        )
        invalid = sum(
            1 for result in self.results_by_case_id.values() if result.status == "invalid"
        )
        warnings = sum(
            1
            for result in self.results_by_case_id.values()
            if result.status in {"partial", "warning"}
        )
        dirty = sum(
            1 for case_id in self.case_order if self.case_store.get_case(case_id).is_dirty
        )
        return {
            "total": total,
            "completed": completed,
            "errors": errors,
            "running": running,
            "invalid": invalid,
            "warnings": warnings,
            "dirty": dirty,
        }
