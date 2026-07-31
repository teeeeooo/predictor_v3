"""Qt-free canonical Predict workspace session state."""

from collections import deque
from dataclasses import dataclass
from uuid import uuid4

from apps.predict.application.result_contract import (
    PredictionExecutionContext,
    PredictionExecutionSemantics,
    PredictionModelIdentity,
    ResultAcceptance,
)
from apps.predict.state.case_store import CaseStore
from apps.predict.state.result_row import ResultRow


@dataclass(frozen=True)
class PredictSessionProjection:
    case_order: tuple[str, ...]
    cases: tuple[tuple[str, dict, dict, set, int], ...]
    results: tuple[ResultRow, ...]


class PredictSession:
    """Own cases, typed results, and the stale-result acceptance gate."""

    def __init__(self, case_store: CaseStore | None = None, *, session_id: str | None = None) -> None:
        self._revision = 0
        self._session_id = session_id or f"predict-session-{uuid4().hex}"
        self.case_store = case_store or CaseStore()
        self.case_store.bind_mutation_callback(self._touch)
        self.results_by_case_id: dict[str, ResultRow] = {}
        self._allowed_contexts: dict[str, PredictionExecutionContext] = {}
        self._acceptance_diagnostics: deque[ResultAcceptance] = deque(maxlen=32)

    @property
    def revision(self) -> int:
        return self._revision

    @property
    def session_id(self) -> str:
        return self._session_id

    @property
    def case_order(self) -> tuple[str, ...]:
        return self.case_store.case_order

    @property
    def acceptance_diagnostics(self) -> tuple[ResultAcceptance, ...]:
        return tuple(self._acceptance_diagnostics)

    def _touch(self, changed_case_id: str = "") -> None:
        self._revision += 1
        if changed_case_id:
            self._mark_case_result_stale(changed_case_id, "input_changed")

    def set_autofill_value(self, case_id: str, key: str, value: object, *, dirty: bool = False) -> None:
        case = self.case_store.get_case(case_id)
        value_changed = case.autofill_values.get(key) != value
        dirty_changed = dirty and key not in case.dirty_fields
        case.autofill_values[key] = value
        if dirty:
            case.dirty_fields.add(key)
        if value_changed:
            case.input_revision += 1
        if value_changed or dirty_changed:
            self._touch(case_id if value_changed else "")

    def result_for_case(self, case_id: str) -> ResultRow:
        return self.results_by_case_id.get(case_id, ResultRow(case_id=case_id))

    def set_result(self, result: ResultRow) -> None:
        """Attach non-executed/legacy state; executed results use accept_result."""
        self.case_store.get_case(result.case_id)
        if self.results_by_case_id.get(result.case_id) != result:
            self.results_by_case_id[result.case_id] = result
            self._touch()

    def set_results(self, results: list[ResultRow]) -> None:
        for result in results:
            self.set_result(result)

    def allow_result(self, context: PredictionExecutionContext) -> None:
        case = self.case_store.get_case(context.case_id)
        if context.session_id != self._session_id:
            raise ValueError("execution context session identity mismatch")
        if context.case_input_revision != case.input_revision:
            raise ValueError("execution context input revision is stale")
        self._allowed_contexts[context.case_id] = context

    def accept_result(self, result: ResultRow) -> ResultAcceptance:
        context = result.execution_context
        reason = self._acceptance_reason(result.case_id, context)
        acceptance = ResultAcceptance(
            not reason, reason, result.case_id, context.run_id if context else ""
        )
        if reason:
            self._acceptance_diagnostics.append(acceptance)
            return acceptance
        self.set_result(result)
        self._allowed_contexts.pop(result.case_id, None)
        return acceptance

    def revoke_run(self, run_id: str) -> None:
        self._allowed_contexts = {
            case_id: context for case_id, context in self._allowed_contexts.items()
            if context.run_id != run_id
        }

    def allowed_context_for_case(
        self, case_id: str
    ) -> PredictionExecutionContext | None:
        return self._allowed_contexts.get(case_id)

    def is_allowed_context_current(self, case_id: str, run_id: str) -> bool:
        context = self._allowed_contexts.get(case_id)
        if context is None or context.run_id != run_id:
            return False
        try:
            return context.case_input_revision == self.case_store.get_case(case_id).input_revision
        except KeyError:
            return False

    def reconcile_result_currentness(
        self,
        semantics: PredictionExecutionSemantics,
        model: PredictionModelIdentity,
    ) -> None:
        for case_id, result in tuple(self.results_by_case_id.items()):
            context = result.execution_context
            if context is None or result.freshness == "stale":
                continue
            reason = (
                "loaded_model_changed" if context.model != model
                else "execution_semantics_changed"
                if context.semantics.currentness_key != semantics.currentness_key
                else ""
            )
            if reason:
                self.results_by_case_id[case_id] = result.marked_stale(reason)
                self._touch()

    def clear_result(self, case_id: str) -> None:
        if self.results_by_case_id.pop(case_id, None) is not None:
            self._touch()

    def clear_all_results(self) -> None:
        if self.results_by_case_id:
            self.results_by_case_id.clear()
            self._touch()

    def remove_results_for_cases(self, case_ids: list[str]) -> None:
        for case_id in case_ids:
            self.clear_result(case_id)

    def apply_runtime_projection(self, projection: PredictSessionProjection, *, expected_revision: int) -> None:
        if self._revision != expected_revision:
            raise ValueError("Predict session changed after prepare")
        self._validate_projection(projection)
        for case_id, inputs, autofill, dirty, input_revision in projection.cases:
            case = self.case_store.get_case(case_id)
            case.input_values = dict(inputs)
            case.autofill_values = dict(autofill)
            case.dirty_fields = set(dirty)
            case.input_revision = input_revision
        self.results_by_case_id = {
            result.case_id: _copy_result(result) for result in projection.results
        }
        self._allowed_contexts.clear()
        self._touch()

    def restore_runtime_projection(self, projection: PredictSessionProjection) -> None:
        self.apply_runtime_projection(projection, expected_revision=self._revision)

    def snapshot_runtime_projection(self) -> PredictSessionProjection:
        return PredictSessionProjection(
            self.case_order,
            tuple((case_id, dict(case.input_values), dict(case.autofill_values),
                   set(case.dirty_fields), case.input_revision)
                  for case_id in self.case_order
                  for case in (self.case_store.get_case(case_id),)),
            tuple(_copy_result(self.results_by_case_id[case_id])
                  for case_id in self.case_order if case_id in self.results_by_case_id),
        )

    def _validate_projection(self, projection: PredictSessionProjection) -> None:
        if projection.case_order != self.case_order:
            raise ValueError("Predict case structure changed after prepare")
        if tuple(item[0] for item in projection.cases) != projection.case_order:
            raise ValueError("Predict case projection order is invalid")
        result_ids = tuple(result.case_id for result in projection.results)
        if len(result_ids) != len(set(result_ids)) or not set(result_ids).issubset(projection.case_order):
            raise ValueError("Predict result projection identity is invalid")

    def _mark_case_result_stale(self, case_id: str, reason: str) -> None:
        existing = self.results_by_case_id.get(case_id)
        if existing is not None and existing.status == "running":
            self.results_by_case_id[case_id] = ResultRow(case_id)
        elif existing is not None:
            self.results_by_case_id[case_id] = existing.marked_stale(reason)

    def _acceptance_reason(self, case_id: str, context: PredictionExecutionContext | None) -> str:
        if context is None:
            return "missing_execution_context"
        if context.session_id != self._session_id:
            return "session_mismatch"
        try:
            case = self.case_store.get_case(case_id)
        except KeyError:
            return "case_removed"
        if context.case_id != case_id:
            return "case_mismatch"
        allowed = self._allowed_contexts.get(case_id)
        if allowed is None:
            return "run_not_active"
        if context.run_id != allowed.run_id:
            return "run_superseded"
        if context.case_input_revision != case.input_revision:
            return "input_revision_changed"
        if context.semantics != allowed.semantics:
            return "execution_semantics_changed"
        if context.model != allowed.model:
            return "loaded_model_changed"
        return ""

    def summary_counts(self) -> dict[str, int]:
        statuses = [result.status for result in self.results_by_case_id.values()]
        return {
            "total": len(self.case_store), "completed": statuses.count("complete"),
            "errors": statuses.count("error"), "running": statuses.count("running"),
            "invalid": statuses.count("invalid"), "cancelled": statuses.count("cancelled"),
            "warnings": sum(status in {"partial", "warning", "cancelled"} for status in statuses),
            "dirty": sum(self.case_store.get_case(case_id).is_dirty for case_id in self.case_order),
        }


def _copy_result(result: ResultRow) -> ResultRow:
    return ResultRow(
        result.case_id, result.status, dict(result._legacy_result_values), result.message,
        target_outcomes=result.target_outcomes,
        execution_context=result.execution_context,
        freshness=result.freshness,
        stale_reason=result.stale_reason,
    )
