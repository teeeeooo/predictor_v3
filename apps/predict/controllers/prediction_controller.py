"""Prediction execution controller foundation."""

from collections.abc import Callable
from dataclasses import dataclass

from apps.predict.adapters.prediction_result_adapter import PredictionResultAdapter
from apps.predict.adapters.row_to_ml_input_adapter import RowToMlInputAdapter
from apps.predict.services.prediction_service import PredictionService
from apps.predict.state.predict_session import PredictSession
from apps.predict.state.result_row import ResultRow


StatusCallback = Callable[[str], None]
ResultCallback = Callable[[ResultRow], None]


@dataclass(frozen=True)
class PredictionRunSummary:
    """Batch prediction run counts."""

    total: int
    complete: int
    error: int
    invalid: int


class PredictionController:
    """Coordinate prediction inputs, service calls, and session updates."""

    def __init__(
        self,
        session: PredictSession,
        input_adapter: RowToMlInputAdapter | None = None,
        service: PredictionService | None = None,
        result_adapter: PredictionResultAdapter | None = None,
    ) -> None:
        self._session = session
        self._input_adapter = input_adapter or RowToMlInputAdapter()
        self._service = service or PredictionService()
        self._result_adapter = result_adapter or PredictionResultAdapter()

    def run_all(
        self,
        status_callback: StatusCallback | None = None,
        result_callback: ResultCallback | None = None,
    ) -> PredictionRunSummary:
        """Run prediction for every current case row."""
        return self.run_case_ids(
            list(self._session.case_order),
            status_callback=status_callback,
            result_callback=result_callback,
        )

    def run_case_ids(
        self,
        case_ids: list[str],
        status_callback: StatusCallback | None = None,
        result_callback: ResultCallback | None = None,
    ) -> PredictionRunSummary:
        """Run prediction for selected case ids."""
        total = len(case_ids)
        self._notify(status_callback, f"Starting prediction for {total} rows.")

        valid_requests = []
        counts = {"complete": 0, "error": 0, "invalid": 0}
        for case_id in case_ids:
            case = self._session.case_store.get_case(case_id)
            outcome = self._input_adapter.build_request(case)
            if not outcome.is_valid:
                result = self._result_adapter.invalid_result(
                    case_id=case_id,
                    message="; ".join(outcome.errors),
                )
                self._record_result(result, result_callback)
                counts["invalid"] += 1
                continue
            running = self._result_adapter.running_result(case_id)
            self._record_result(running, result_callback)
            valid_requests.append(outcome.request)

        service_results = self._service.predict_many(
            [request for request in valid_requests if request is not None]
        )
        for service_result in service_results:
            result = self._result_adapter.from_service_result(service_result)
            self._record_result(result, result_callback)
            if result.status == "complete":
                counts["complete"] += 1
            elif result.status == "error":
                counts["error"] += 1

        self._notify(status_callback, "Prediction run finished.")
        return PredictionRunSummary(
            total=total,
            complete=counts["complete"],
            error=counts["error"],
            invalid=counts["invalid"],
        )

    def _record_result(
        self,
        result: ResultRow,
        result_callback: ResultCallback | None,
    ) -> None:
        self._session.set_result(result)
        if result_callback is not None:
            result_callback(result)

    def _notify(self, callback: StatusCallback | None, message: str) -> None:
        if callback is not None:
            callback(message)
