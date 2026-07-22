"""Predict workspace session state."""

from dataclasses import dataclass

from apps.predict.state.case_store import CaseStore
from apps.predict.state.result_row import ResultRow


@dataclass(frozen=True)
class PredictSessionProjection:
    """Complete case/result state for one generation transition."""

    case_order: tuple[str, ...]
    cases: tuple[tuple[str, dict, dict, set], ...]
    results: tuple[ResultRow, ...]


class PredictSession:
    """Qt-free state container for a Predict workspace."""

    def __init__(self, case_store: CaseStore | None = None) -> None:
        self._revision = 0
        self.case_store = case_store or CaseStore()
        self.case_store.bind_mutation_callback(self._touch)
        self.results_by_case_id: dict[str, ResultRow] = {}

    @property
    def revision(self) -> int:
        return self._revision

    def _touch(self) -> None:
        self._revision += 1

    def set_autofill_value(
        self, case_id: str, key: str, value: object, *, dirty: bool = False
    ) -> None:
        case = self.case_store.get_case(case_id)
        changed = case.autofill_values.get(key) != value
        case.autofill_values[key] = value
        if dirty:
            changed = changed or key not in case.dirty_fields
            case.dirty_fields.add(key)
        if changed:
            self._touch()

    def apply_runtime_projection(
        self,
        projection: PredictSessionProjection,
        *,
        expected_revision: int,
    ) -> None:
        """Install a validated case/result migration as one session mutation."""
        if self._revision != expected_revision:
            raise ValueError("Predict session changed after prepare")
        self._validate_projection(projection)
        cases = tuple(
            self.case_store.get_case(item[0]) for item in projection.cases
        )
        case_values = tuple(
            (dict(inputs), dict(autofill), set(dirty))
            for _case_id, inputs, autofill, dirty in projection.cases
        )
        results = {
            result.case_id: _copy_result(result) for result in projection.results
        }
        for case, (inputs, autofill, dirty) in zip(
            cases, case_values, strict=True
        ):
            case.input_values = inputs
            case.autofill_values = autofill
            case.dirty_fields = dirty
        self.results_by_case_id = results
        self._touch()

    def restore_runtime_projection(
        self, projection: PredictSessionProjection
    ) -> None:
        """Restore one complete rollback snapshot without changing case identity."""
        self._validate_projection(projection)
        self.apply_runtime_projection(
            projection,
            expected_revision=self._revision,
        )

    def snapshot_runtime_projection(self) -> PredictSessionProjection:
        """Copy all mutable case and result state for exact rollback."""
        return PredictSessionProjection(
            case_order=self.case_order,
            cases=tuple(
                (
                    case_id,
                    dict(self.case_store.get_case(case_id).input_values),
                    dict(self.case_store.get_case(case_id).autofill_values),
                    set(self.case_store.get_case(case_id).dirty_fields),
                )
                for case_id in self.case_order
            ),
            results=tuple(
                _copy_result(self.results_by_case_id[case_id])
                for case_id in self.case_order
                if case_id in self.results_by_case_id
            ),
        )

    def _validate_projection(self, projection: PredictSessionProjection) -> None:
        if projection.case_order != self.case_order:
            raise ValueError("Predict case structure changed after prepare")
        if tuple(item[0] for item in projection.cases) != projection.case_order:
            raise ValueError("Predict case projection order is invalid")
        result_ids = tuple(result.case_id for result in projection.results)
        if len(result_ids) != len(set(result_ids)) or not set(result_ids).issubset(
            projection.case_order
        ):
            raise ValueError("Predict result projection identity is invalid")

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
        if self.results_by_case_id.get(result.case_id) != result:
            self.results_by_case_id[result.case_id] = result
            self._touch()

    def set_results(self, results: list[ResultRow]) -> None:
        """Attach several result states by case_id."""
        for result in results:
            self.set_result(result)

    def clear_result(self, case_id: str) -> None:
        """Clear result state for one case."""
        if self.results_by_case_id.pop(case_id, None) is not None:
            self._touch()

    def clear_all_results(self) -> None:
        """Clear every result state."""
        if self.results_by_case_id:
            self.results_by_case_id.clear()
            self._touch()

    def remove_results_for_cases(self, case_ids: list[str]) -> None:
        """Drop result state for removed cases."""
        for case_id in case_ids:
            self.clear_result(case_id)

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
        cancelled = sum(
            1
            for result in self.results_by_case_id.values()
            if result.status == "cancelled"
        )
        warnings = sum(
            1
            for result in self.results_by_case_id.values()
            if result.status in {"partial", "warning", "cancelled"}
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
            "cancelled": cancelled,
            "warnings": warnings,
            "dirty": dirty,
        }


def _copy_result(result: ResultRow) -> ResultRow:
    return ResultRow(
        case_id=result.case_id,
        status=result.status,
        result_values=dict(result.result_values),
        message=result.message,
    )
