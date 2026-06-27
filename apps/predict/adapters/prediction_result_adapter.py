"""Convert prediction service outcomes into session result rows."""

from math import isfinite
from typing import Any

from apps.predict.schema.column_schema_adapter import (
    PredictColumn,
    build_result_column_schema,
)
from apps.predict.state.result_row import ResultRow
from core.ml.features import TARGETS


class PredictionResultAdapter:
    """Map service results to user-facing ResultRow values."""

    def __init__(self, columns: tuple[PredictColumn, ...] | None = None) -> None:
        self._columns = columns or build_result_column_schema()
        self._target_to_result_key = {
            column.ml_target: column.key for column in self._columns if column.ml_target
        }

    def from_service_result(self, result: Any) -> ResultRow:
        """Convert one service result into a ResultRow."""
        if result.status != "complete":
            return ResultRow(
                case_id=result.case_id,
                status=result.status,
                message=self._clean_message(result.message),
            )

        missing_targets = [
            target
            for target in TARGETS
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


def apply_prediction_result(result: Any) -> ResultRow:
    """Convert one prediction service result with the default adapter."""
    return PredictionResultAdapter().from_service_result(result)
