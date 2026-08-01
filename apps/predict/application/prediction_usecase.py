"""UI/runtime-neutral prediction usecase."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from dataclasses import replace
from uuid import uuid4

from apps.predict.application.models import (
    PredictionInputRequest,
    PredictionServiceResult,
)
from apps.predict.application.result_contract import (
    PredictionExecutionContext,
    PredictionExecutionSemantics,
    PredictionModelIdentity,
)
from apps.predict.ports.prediction_execution_port import (
    PredictionJob,
    PredictionWorkerSummary,
)
from apps.predict.ports.prediction_workflow_ports import (
    PredictionInputMapper,
    PredictionResultMapper,
)
from apps.predict.state.predict_session import PredictSession
from apps.predict.state.result_row import ResultRow


ResultCallback = Callable[[ResultRow], None]


@dataclass(frozen=True)
class PredictionRunSummary:
    """Batch prediction run counts."""

    total: int
    complete: int
    error: int
    invalid: int
    cancelled: int = 0
    partial: int = 0
    unresolved: int = 0


@dataclass(frozen=True)
class PredictionRunPlan:
    """Prepared prediction run and initial summary."""

    job: PredictionJob | None
    summary: PredictionRunSummary


class PredictionUseCase:
    """Prepare prediction runs and apply runner results without Qt."""

    def __init__(
        self,
        session: PredictSession,
        input_mapper: PredictionInputMapper,
        result_mapper: PredictionResultMapper,
        execution_semantics: PredictionExecutionSemantics | None = None,
        model_identity: PredictionModelIdentity | None = None,
    ) -> None:
        self._session = session
        self._input_mapper = input_mapper
        self._result_mapper = result_mapper
        self._execution_semantics = execution_semantics or PredictionExecutionSemantics(
            "legacy", "legacy", "legacy", "legacy", "legacy", "legacy"
        )
        self._model_identity = model_identity or PredictionModelIdentity(
            "unmanaged", 0, "legacy"
        )
        self._target_descriptors = tuple(result_mapper.target_descriptors)
        if not self._target_descriptors:
            raise ValueError("Predict result mapper has no target descriptors")

    def update_execution_environment(
        self,
        semantics: PredictionExecutionSemantics,
        model_identity: PredictionModelIdentity,
    ) -> None:
        self._execution_semantics = semantics
        self._model_identity = model_identity

    @property
    def execution_environment(
        self,
    ) -> tuple[PredictionExecutionSemantics, PredictionModelIdentity]:
        return self._execution_semantics, self._model_identity

    def prepare_run(
        self,
        case_ids: list[str],
        result_callback: ResultCallback | None = None,
    ) -> PredictionRunPlan:
        """Validate rows, mark initial state, and return a runnable job."""
        valid_requests: list[PredictionInputRequest] = []
        invalid_count = 0
        run_id = f"predict-{uuid4().hex}"
        for case_id in case_ids:
            case = self._session.case_store.get_case(case_id)
            outcome = self._input_mapper.build_request(case)
            if not outcome.is_valid:
                self._record_result(
                    self._result_mapper.invalid_result(
                        case_id=case_id,
                        message="; ".join(outcome.errors),
                    ),
                    result_callback,
                )
                invalid_count += 1
                continue
            if outcome.request is None:
                continue
            context = PredictionExecutionContext(
                session_id=self._session.session_id,
                case_id=case_id,
                run_id=run_id,
                case_input_revision=case.input_revision,
                semantics=self._execution_semantics,
                model=self._model_identity,
            )
            request = replace(outcome.request, context=context)
            self._session.allow_result(context, self._target_descriptors)
            self._record_result(
                self._result_mapper.running_result(case_id),
                result_callback,
            )
            valid_requests.append(request)

        summary = PredictionRunSummary(
            total=len(case_ids),
            complete=0,
            error=0,
            invalid=invalid_count,
        )
        if not valid_requests:
            return PredictionRunPlan(job=None, summary=summary)
        return PredictionRunPlan(
            job=PredictionJob(
                run_id=run_id,
                requests=tuple(valid_requests),
                total=len(valid_requests),
            ),
            summary=summary,
        )

    def apply_service_result(
        self,
        service_result: PredictionServiceResult,
        result_callback: ResultCallback | None = None,
    ) -> bool:
        """Apply one service result to session state."""
        result = self._result_mapper.from_service_result(service_result)
        acceptance = self._session.accept_result(
            result, self._execution_semantics, self._model_identity
        )
        if acceptance.accepted and result_callback is not None:
            result_callback(result)
        return acceptance.accepted

    def apply_cancelled_rows(
        self,
        case_ids: tuple[str, ...],
        result_callback: ResultCallback | None = None,
        *,
        run_id: str = "",
    ) -> tuple[ResultRow, ...]:
        """Apply cancelled row state for requests not run by the runner."""
        effective_run_ids: set[str] = set()
        accepted: list[ResultRow] = []
        for case_id in case_ids:
            effective_run_id = run_id or self._run_id_for_case(case_id)
            context = self._session.allowed_context_for_case(case_id)
            if context is None or context.run_id != effective_run_id:
                continue
            effective_run_ids.add(effective_run_id)
            result = self._result_mapper.cancelled_result(
                case_id, context=context
            )
            if self._accept_executed_result(result, result_callback):
                accepted.append(result)
        for effective_run_id in effective_run_ids:
            self._session.revoke_run(effective_run_id)
        return tuple(accepted)

    def apply_infrastructure_failure(
        self,
        case_ids: tuple[str, ...],
        message: str,
        result_callback: ResultCallback | None = None,
        *,
        run_id: str = "",
    ) -> PredictionRunSummary:
        """Turn only still-running rows into terminal infrastructure errors."""
        effective_run_ids: set[str] = set()
        for case_id in case_ids:
            effective_run_id = run_id or self._run_id_for_case(case_id)
            context = self._session.allowed_context_for_case(case_id)
            if context is None or context.run_id != effective_run_id:
                continue
            effective_run_ids.add(effective_run_id)
            result = self._result_mapper.infrastructure_failure_result(
                case_id, message, context=context
            )
            self._accept_executed_result(result, result_callback)
        for effective_run_id in effective_run_ids:
            self._session.revoke_run(effective_run_id)
        return self.summary_from_case_ids(case_ids)

    def _run_id_for_case(self, case_id: str) -> str:
        context = self._session.allowed_context_for_case(case_id)
        return context.run_id if context is not None else ""

    def summary_from_case_ids(
        self,
        case_ids: tuple[str, ...],
    ) -> PredictionRunSummary:
        """Summarize the actual session states for one active run."""
        statuses = [self._session.result_for_case(case_id).status for case_id in case_ids]
        resolved = sum(
            status in {"complete", "partial", "error", "invalid", "cancelled"}
            for status in statuses
        )
        return PredictionRunSummary(
            total=len(case_ids),
            complete=statuses.count("complete"),
            error=statuses.count("error"),
            invalid=statuses.count("invalid"),
            cancelled=statuses.count("cancelled"),
            partial=statuses.count("partial"),
            unresolved=len(case_ids) - resolved,
        )

    def summary_from_worker(
        self,
        summary: PredictionWorkerSummary,
        invalid_count: int,
    ) -> PredictionRunSummary:
        """Combine runner counts with pre-run invalid rows."""
        return PredictionRunSummary(
            total=summary.total + invalid_count,
            complete=summary.complete,
            error=summary.error,
            invalid=invalid_count,
            cancelled=summary.cancelled,
        )

    def _record_result(
        self,
        result: ResultRow,
        result_callback: ResultCallback | None,
    ) -> None:
        self._session.set_result(result)
        if result_callback is not None:
            result_callback(result)

    def _accept_executed_result(
        self,
        result: ResultRow,
        result_callback: ResultCallback | None,
    ) -> bool:
        acceptance = self._session.accept_result(
            result, self._execution_semantics, self._model_identity
        )
        if acceptance.accepted and result_callback is not None:
            result_callback(result)
        return acceptance.accepted
