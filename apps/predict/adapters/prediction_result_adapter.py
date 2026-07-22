"""Convert prediction service outcomes into session result rows."""

from math import isfinite
from typing import Any

from apps.predict.application.models import PredictionServiceResult
from apps.predict.schema.column_schema_adapter import (
    PredictColumn,
    build_result_column_schema,
)
from apps.predict.state.result_row import ResultRow


class PredictionResultAdapter:
    """Map service results to user-facing ResultRow values."""

    def __init__(
        self,
        columns: tuple[PredictColumn, ...] | None = None,
        *,
        active_targets: tuple[str, ...] | None = None,
        target_result_keys: tuple[tuple[str, str], ...] | None = None,
        generation_id: str = "legacy",
    ) -> None:
        self._columns = columns or build_result_column_schema()
        self._target_to_result_key = dict(target_result_keys) if target_result_keys is not None else {
            column.ml_target: column.key for column in self._columns if column.ml_target
        }
        self._active_targets = (
            active_targets if active_targets is not None else tuple(self._target_to_result_key)
        )
        self._generation_id = generation_id

    @property
    def generation_id(self) -> str:
        return self._generation_id

    @property
    def active_targets(self) -> tuple[str, ...]:
        return self._active_targets

    def from_service_result(self, result: PredictionServiceResult) -> ResultRow:
        """Convert one service result into a ResultRow."""
        if result.status != "complete":
            return ResultRow(
                case_id=result.case_id,
                status=result.status,
                message=self._clean_message(result.message),
            )

        missing_targets = [
            target
            for target in self._active_targets
            if target in self._target_to_result_key and target not in result.predictions
        ]
        values = {
            result_key: self._format_number(result.predictions.get(target))
            for target, result_key in self._target_to_result_key.items()
        }
        status = "partial" if missing_targets else "complete"
        message = (
            f"Missing prediction target(s): {', '.join(missing_targets)}"
            if missing_targets
            else result.message
        )
        return ResultRow(
            case_id=result.case_id,
            status=status,
            result_values=values,
            message=self._clean_message(message),
        )

    def invalid_result(self, case_id: str, message: str) -> ResultRow:
        """Build a row-level invalid result without model execution."""
        return ResultRow(case_id=case_id, status="invalid", message=self._clean_message(message))

    def running_result(self, case_id: str) -> ResultRow:
        """Build a row-level running result."""
        return ResultRow(case_id=case_id, status="running")

    def cancelled_result(
        self,
        case_id: str,
        message: str = "Prediction cancelled.",
    ) -> ResultRow:
        """Build a row-level cancelled result."""
        return ResultRow(
            case_id=case_id,
            status="cancelled",
            message=self._clean_message(message),
        )

    def infrastructure_failure_result(self, case_id: str, message: str) -> ResultRow:
        """Build an error row for a runner/infrastructure failure."""
        return ResultRow(
            case_id=case_id,
            status="error",
            message=self._clean_message(message),
        )

    def _format_number(self, value: Any) -> str:
        if value is None:
            return ""
        try:
            number = float(value)
        except (TypeError, ValueError):
            return str(value)
        if not isfinite(number):
            return ""
        text = f"{number:.4f}".rstrip("0").rstrip(".")
        return text if text != "-0" else "0"

    def _clean_message(self, message: str) -> str:
        if not message:
            return ""
        first_line = str(message).strip().splitlines()[0]
        if not first_line:
            return ""
        return first_line[:160]


def apply_prediction_result(result: PredictionServiceResult) -> ResultRow:
    """Convert one prediction service result with the default adapter."""
    return PredictionResultAdapter().from_service_result(result)
