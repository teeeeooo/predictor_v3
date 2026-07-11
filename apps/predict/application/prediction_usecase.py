"""UI/runtime-neutral prediction usecase."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from uuid import uuid4

from apps.predict.application.models import (
    PredictionInputRequest,
    PredictionServiceResult,
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
    ) -> None:
        self._session = session
        self._input_mapper = input_mapper
        self._result_mapper = result_mapper

    def prepare_run(
        self,
        case_ids: list[str],
        result_callback: ResultCallback | None = None,
    ) -> PredictionRunPlan:
        """Validate rows, mark initial state, and return a runnable job."""
        valid_requests: list[PredictionInputRequest] = []
        invalid_count = 0
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
            self._record_result(
                self._result_mapper.running_result(case_id),
                result_callback,
            )
            valid_requests.append(outcome.request)

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
                run_id=f"predict-{uuid4().hex}",
                requests=tuple(valid_requests),
                total=len(valid_requests),
            ),
            summary=summary,
        )

    def apply_service_result(
        self,
        service_result: PredictionServiceResult,
        result_callback: ResultCallback | None = None,
    ) -> None:
        """Apply one service result to session state."""
        self._record_result(
            self._result_mapper.from_service_result(service_result),
            result_callback,
        )

    def apply_cancelled_rows(
        self,
        case_ids: tuple[str, ...],
        result_callback: ResultCallback | None = None,
    ) -> None:
        """Apply cancelled row state for requests not run by the runner."""
        for case_id in case_ids:
            self._record_result(
                self._result_mapper.cancelled_result(case_id),
                result_callback,
            )

    def apply_infrastructure_failure(
        self,
        case_ids: tuple[str, ...],
        message: str,
        result_callback: ResultCallback | None = None,
    ) -> PredictionRunSummary:
        """Turn only still-running rows into terminal infrastructure errors."""
        for case_id in case_ids:
            if self._session.result_for_case(case_id).status != "running":
                continue
            self._record_result(
                self._result_mapper.infrastructure_failure_result(case_id, message),
                result_callback,
            )
        return self.summary_from_case_ids(case_ids)

    def summary_from_case_ids(
        self,
        case_ids: tuple[str, ...],
    ) -> PredictionRunSummary:
        """Summarize the actual session states for one active run."""
        statuses = [self._session.result_for_case(case_id).status for case_id in case_ids]
        return PredictionRunSummary(
            total=len(case_ids),
            complete=statuses.count("complete"),
            error=statuses.count("error"),
            invalid=statuses.count("invalid"),
            cancelled=statuses.count("cancelled"),
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
