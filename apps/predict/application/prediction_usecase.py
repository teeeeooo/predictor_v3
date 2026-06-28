"""UI/runtime-neutral prediction usecase."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from uuid import uuid4

from apps.predict.adapters.prediction_result_adapter import PredictionResultAdapter
from apps.predict.adapters.row_to_ml_input_adapter import (
    PredictionInputRequest,
    RowToMlInputAdapter,
)
from apps.predict.ports.prediction_execution_port import (
    PredictionJob,
    PredictionWorkerSummary,
)
from apps.predict.services.prediction_service import PredictionServiceResult
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
        input_adapter: RowToMlInputAdapter | None = None,
        result_adapter: PredictionResultAdapter | None = None,
    ) -> None:
        self._session = session
        self._input_adapter = input_adapter or RowToMlInputAdapter()
        self._result_adapter = result_adapter or PredictionResultAdapter()

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
            outcome = self._input_adapter.build_request(case)
            if not outcome.is_valid:
                self._record_result(
                    self._result_adapter.invalid_result(
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
                self._result_adapter.running_result(case_id),
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
            self._result_adapter.from_service_result(service_result),
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
                self._result_adapter.cancelled_result(case_id),
                result_callback,
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
