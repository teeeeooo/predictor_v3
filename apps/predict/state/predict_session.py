"""Qt-free canonical Predict workspace session state."""

from collections import deque
from types import MappingProxyType
from typing import Mapping
from uuid import uuid4

from apps.predict.application.result_contract import (
    PredictionExecutionContext,
    PredictionExecutionSemantics,
    PredictionModelIdentity,
    ResultAcceptance,
    execution_semantics_from_runtime,
)
from apps.predict.application.result_validation import canonical_result_rejection_reason
from apps.predict.application.runtime_snapshot import validate_runtime_target_contract
from apps.predict.application.target_outcome import PredictionTargetDescriptor
from apps.predict.state.case_store import CaseStore
from apps.predict.state.result_state_boundary import (
    AllowedExecution,
    PredictSessionProjection,
    ResultProjectionAuthority,
    copy_result,
    validate_direct_result,
    validate_canonical_results,
    validate_migration_relation,
    validate_projection_structure,
    validate_projected_results,
    without_case_dependencies,
)
from apps.predict.state.result_row import ResultRow


class PredictSession:
    """Own cases, typed results, and the stale-result acceptance gate."""
    def __init__(self, case_store: CaseStore | None = None, *, session_id: str | None = None) -> None:
        self._revision = 0
        self._session_id = session_id or f"predict-session-{uuid4().hex}"
        self.case_store = case_store or CaseStore()
        self.case_store.bind_mutation_callback(self._touch)
        self.case_store.bind_removal_callback(
            lambda case_ids: self._remove_case_dependencies(case_ids)
        )
        self._results_by_case_id: dict[str, ResultRow] = {}
        self._allowed_executions: dict[str, AllowedExecution] = {}
        self._active_target_contract: tuple[PredictionTargetDescriptor, ...] | None = None
        self._active_semantics: PredictionExecutionSemantics | None = None
        self._active_model: PredictionModelIdentity | None = None
        self._projection_authority = ResultProjectionAuthority()
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

    @property
    def results_by_case_id(self) -> Mapping[str, ResultRow]:
        return MappingProxyType(self._results_by_case_id)

    @property
    def issued_projection_count(self) -> int:
        return self._projection_authority.count

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
        return self._results_by_case_id.get(case_id, ResultRow(case_id=case_id))

    def set_result(self, result: ResultRow) -> None:
        """Attach only non-executed state; terminal results use accept_result."""
        validate_direct_result(result)
        self._store_result(result)

    def _store_result(self, result: ResultRow) -> None:
        self.case_store.get_case(result.case_id)
        if self._results_by_case_id.get(result.case_id) != result:
            self._results_by_case_id[result.case_id] = result
            self._touch()

    def set_results(self, results: list[ResultRow]) -> None:
        for result in results:
            validate_direct_result(result)
        for result in results:
            self._store_result(result)

    def allow_result(
        self,
        context: PredictionExecutionContext,
        expected_targets: tuple[PredictionTargetDescriptor, ...],
    ) -> None:
        case = self.case_store.get_case(context.case_id)
        if context.session_id != self._session_id:
            raise ValueError("execution context session identity mismatch")
        if context.case_input_revision != case.input_revision:
            raise ValueError("execution context input revision is stale")
        identities = tuple(item.target_identity for item in expected_targets)
        if not identities or len(identities) != len(set(identities)):
            raise ValueError("expected target contract is invalid")
        target_contract = tuple(expected_targets)
        if (
            self._active_target_contract is not None
            and self._active_target_contract != target_contract
        ):
            raise ValueError("execution target contract differs from active runtime")
        if (
            self._active_semantics is not None
            and self._active_semantics.currentness_key
            != context.semantics.currentness_key
        ):
            raise ValueError("execution semantics differ from active runtime")
        if self._active_model is not None and self._active_model != context.model:
            raise ValueError("loaded model differs from active runtime")
        self._active_target_contract = target_contract
        self._active_semantics = context.semantics
        self._active_model = context.model
        self._allowed_executions[context.case_id] = AllowedExecution(
            context, target_contract
        )

    def accept_result(
        self,
        result: ResultRow,
        current_semantics: PredictionExecutionSemantics,
        current_model: PredictionModelIdentity,
    ) -> ResultAcceptance:
        context = result.execution_context
        reason = self._acceptance_reason(
            result.case_id, context, current_semantics, current_model
        )
        allowed = self._allowed_executions.get(result.case_id)
        if not reason and allowed is not None:
            reason = canonical_result_rejection_reason(
                result, allowed.expected_targets
            )
        acceptance = ResultAcceptance(
            not reason, reason, result.case_id, context.run_id if context else ""
        )
        if reason:
            self._acceptance_diagnostics.append(acceptance)
            return acceptance
        self._store_result(result)
        self._allowed_executions.pop(result.case_id, None)
        return acceptance

    def revoke_run(self, run_id: str) -> None:
        self._allowed_executions = {
            case_id: allowed
            for case_id, allowed in self._allowed_executions.items()
            if allowed.context.run_id != run_id
        }

    def allowed_context_for_case(self, case_id: str) -> PredictionExecutionContext | None:
        allowed = self._allowed_executions.get(case_id)
        return allowed.context if allowed is not None else None

    def is_allowed_context_current(self, case_id: str, run_id: str) -> bool:
        allowed = self._allowed_executions.get(case_id)
        if allowed is None or allowed.context.run_id != run_id:
            return False
        try:
            return (
                allowed.context.case_input_revision
                == self.case_store.get_case(case_id).input_revision
            )
        except KeyError:
            return False

    def reconcile_result_currentness(
        self,
        semantics: PredictionExecutionSemantics,
        model: PredictionModelIdentity,
    ) -> None:
        for case_id, result in tuple(self._results_by_case_id.items()):
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
                self._results_by_case_id[case_id] = result.marked_stale(reason)
                self._touch()
        self._active_semantics = semantics
        self._active_model = model

    def clear_result(self, case_id: str) -> None:
        if self._results_by_case_id.pop(case_id, None) is not None:
            self._touch()

    def clear_all_results(self) -> None:
        if self._results_by_case_id:
            self._results_by_case_id.clear()
            self._touch()

    def remove_results_for_cases(self, case_ids: list[str]) -> None:
        for case_id in case_ids:
            self.clear_result(case_id)

    def _remove_case_dependencies(self, case_ids: tuple[str, ...]) -> None:
        self._validate_canonical_state()
        remaining = without_case_dependencies(
            self._results_by_case_id, self._allowed_executions, case_ids)
        self._results_by_case_id, self._allowed_executions = remaining

    def prepare_runtime_projection(
        self,
        *,
        cases: tuple[tuple[str, dict, dict, set, int], ...],
        results: tuple[ResultRow, ...],
        runtime_snapshot,
        model_identity: PredictionModelIdentity,
    ) -> PredictSessionProjection:
        """Issue an atomic migration artifact after validating both boundaries."""
        self._validate_canonical_state()
        validate_runtime_target_contract(runtime_snapshot)
        projection = PredictSessionProjection(
            self.case_order,
            cases,
            tuple(copy_result(result) for result in results),
            tuple(runtime_snapshot.target_descriptors),
            execution_semantics_from_runtime(runtime_snapshot),
            model_identity,
            (),
            self._revision,
        )
        validate_projection_structure(projection, self.case_order)
        validate_migration_relation(self._results_by_case_id, projection.results)
        validate_projected_results(projection, session_id=self._session_id)
        return self._projection_authority.issue(projection, "migration")

    def apply_runtime_projection(
        self, projection: PredictSessionProjection, *, expected_revision: int
    ) -> None:
        if self._revision != expected_revision:
            raise ValueError("Predict session changed after prepare")
        self._projection_authority.validate(projection, "migration")
        self._validate_canonical_state()
        validate_projection_structure(projection, self.case_order)
        validate_migration_relation(self._results_by_case_id, projection.results)
        validate_projected_results(projection, session_id=self._session_id)
        for case_id, inputs, autofill, dirty, input_revision in projection.cases:
            case = self.case_store.get_case(case_id)
            case.input_values = dict(inputs)
            case.autofill_values = dict(autofill)
            case.dirty_fields = set(dirty)
            case.input_revision = input_revision
        self._results_by_case_id = {
            result.case_id: copy_result(result) for result in projection.results
        }
        self._active_target_contract = tuple(projection.target_contract)
        self._active_semantics = projection.execution_semantics
        self._active_model = projection.model_identity
        self._allowed_executions.clear()
        self._projection_authority.consume(projection)
        self._touch()

    def restore_runtime_projection(self, projection: PredictSessionProjection) -> None:
        self._projection_authority.validate(projection, "snapshot")
        self._validate_canonical_state()
        validate_projection_structure(projection, self.case_order)
        validate_projected_results(projection, session_id=self._session_id)
        for case_id, inputs, autofill, dirty, input_revision in projection.cases:
            case = self.case_store.get_case(case_id)
            case.input_values = dict(inputs)
            case.autofill_values = dict(autofill)
            case.dirty_fields = set(dirty)
            case.input_revision = input_revision
        self._results_by_case_id = {
            result.case_id: copy_result(result) for result in projection.results
        }
        self._active_target_contract = (
            tuple(projection.target_contract) if projection.target_contract else None
        )
        self._active_semantics = projection.execution_semantics
        self._active_model = projection.model_identity
        self._allowed_executions = dict(projection.allowed_executions)
        self._revision = projection.session_revision
        self._projection_authority.consume(projection)

    def snapshot_runtime_projection(self) -> PredictSessionProjection:
        self._validate_canonical_state()
        projection = PredictSessionProjection(
            self.case_order,
            tuple((case_id, dict(case.input_values), dict(case.autofill_values),
                   set(case.dirty_fields), case.input_revision)
                  for case_id in self.case_order
                  for case in (self.case_store.get_case(case_id),)),
            tuple(copy_result(self._results_by_case_id[case_id])
                  for case_id in self.case_order if case_id in self._results_by_case_id),
            tuple(self._active_target_contract or ()),
            self._active_semantics,
            self._active_model,
            tuple(self._allowed_executions.items()),
            self._revision,
        )
        return self._projection_authority.issue(projection, "snapshot")

    def release_runtime_projection(
        self, projection: PredictSessionProjection, *, kind: str
    ) -> bool:
        return self._projection_authority.release(projection, kind)

    def _validate_canonical_state(self) -> None:
        case_revisions = {
            case_id: self.case_store.get_case(case_id).input_revision
            for case_id in self.case_order
        }
        validate_canonical_results(
            self._results_by_case_id,
            case_order=self.case_order,
            case_revisions=case_revisions,
            target_contract=self._active_target_contract,
            execution_semantics=self._active_semantics,
            model_identity=self._active_model,
            session_id=self._session_id,
        )

    def _mark_case_result_stale(self, case_id: str, reason: str) -> None:
        existing = self._results_by_case_id.get(case_id)
        if existing is not None and existing.status == "running":
            self._results_by_case_id[case_id] = ResultRow(case_id)
        elif existing is not None:
            self._results_by_case_id[case_id] = existing.marked_stale(reason)

    def _acceptance_reason(
        self,
        case_id: str,
        context: PredictionExecutionContext | None,
        current_semantics: PredictionExecutionSemantics,
        current_model: PredictionModelIdentity,
    ) -> str:
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
        allowed_execution = self._allowed_executions.get(case_id)
        allowed = allowed_execution.context if allowed_execution is not None else None
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
        if context.capacity_inputs != allowed.capacity_inputs:
            return "execution_input_changed"
        if allowed.semantics.currentness_key != current_semantics.currentness_key:
            return "execution_semantics_changed"
        if allowed.model != current_model:
            return "loaded_model_changed"
        return ""

    def summary_counts(self) -> dict[str, int]:
        statuses = [result.status for result in self._results_by_case_id.values()]
        return {
            "total": len(self.case_store), "completed": statuses.count("complete"),
            "errors": statuses.count("error"), "running": statuses.count("running"),
            "invalid": statuses.count("invalid"), "cancelled": statuses.count("cancelled"),
            "warnings": sum(status in {"partial", "warning", "cancelled"} for status in statuses),
            "dirty": sum(self.case_store.get_case(case_id).is_dirty for case_id in self.case_order),
        }
