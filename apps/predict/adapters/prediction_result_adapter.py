"""Convert prediction service outcomes into session result rows."""

from math import isfinite
from typing import Any

from apps.predict.services.prediction_service import PredictionServiceResult
from apps.predict.state.result_row import ResultRow


class PredictionResultAdapter:
    """Map service results to user-facing ResultRow values."""

    _TARGET_TO_RESULT_KEY = {
        "Cooling Power": "cooling_power",
        "Heating Power": "heating_power",
        "Ref Qty": "ref_qty",
        "Cooling Hz": "cooling_hz",
        "Heating Hz": "heating_hz",
    }

    def from_service_result(self, result: PredictionServiceResult) -> ResultRow:
        """Convert one service result into a ResultRow."""
        if result.status != "complete":
            return ResultRow(
                case_id=result.case_id,
                status=result.status,
                message=self._clean_message(result.message),
            )

        values = {
            result_key: self._format_number(result.predictions.get(target))
            for target, result_key in self._TARGET_TO_RESULT_KEY.items()
        }
        return ResultRow(
            case_id=result.case_id,
            status="complete",
            result_values=values,
            message=self._clean_message(result.message),
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
