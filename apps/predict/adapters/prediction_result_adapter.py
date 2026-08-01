"""Convert prediction service outcomes into session result rows."""

import logging
from math import isfinite
import re

from apps.predict.application.models import PredictionServiceResult
from apps.predict.application.result_contract import PredictionExecutionContext
from apps.predict.application.result_enrichment import enrich_target_outcomes
from apps.predict.application.target_outcome import (
    PredictionTargetDescriptor,
    TargetOutcome,
)
from apps.predict.schema.column_schema_adapter import (
    PredictColumn,
    build_input_column_schema,
    build_result_column_schema,
)
from apps.predict.state.result_row import ResultRow


logger = logging.getLogger(__name__)


class PredictionResultAdapter:
    """Map service results to user-facing ResultRow values."""

    def __init__(
        self,
        columns: tuple[PredictColumn, ...] | None = None,
        *,
        input_columns: tuple[PredictColumn, ...] | None = None,
        active_targets: tuple[str, ...] | None = None,
        target_result_keys: tuple[tuple[str, str], ...] | None = None,
        target_descriptors: tuple[PredictionTargetDescriptor, ...] | None = None,
        generation_id: str = "legacy",
    ) -> None:
        self._columns = columns or build_result_column_schema()
        self._input_labels = {
            column.key: column.header
            for column in (input_columns or build_input_column_schema())
        }
        self._target_to_result_key = dict(target_result_keys) if target_result_keys is not None else {
            column.ml_target: column.key for column in self._columns if column.ml_target
        }
        self._active_targets = (
            active_targets if active_targets is not None else tuple(self._target_to_result_key)
        )
        self._target_descriptors = target_descriptors or tuple(
            PredictionTargetDescriptor(
                target_identity=f"legacy-target:{column.ml_target}",
                result_feature_identity=column.feature_identity,
                ml_name=column.ml_target,
                result_key=column.key,
                canonical_unit=_canonical_legacy_unit(column.key),
            )
            for column in self._columns
            if column.ml_target
        )
        if tuple(item.ml_name for item in self._target_descriptors) != self._active_targets:
            raise ValueError("Predict target descriptor projection is incomplete")
        self._generation_id = generation_id

    @property
    def generation_id(self) -> str:
        return self._generation_id

    @property
    def active_targets(self) -> tuple[str, ...]:
        return self._active_targets

    @property
    def target_descriptors(self) -> tuple[PredictionTargetDescriptor, ...]:
        """Expose the immutable runtime projection used by this adapter."""
        return self._target_descriptors

    def from_service_result(self, result: PredictionServiceResult) -> ResultRow:
        """Convert one service result into a ResultRow."""
        if result.status != "complete":
            message = result.message
            if result.status == "error":
                self._log_runtime_failure(result.case_id, message)
                message = _RUNTIME_FAILURE_MESSAGE
            return ResultRow(
                case_id=result.case_id,
                status=result.status,
                message=self._clean_message(message),
                execution_context=result.context,
            )

        outcomes = tuple(
            self._target_outcome(descriptor, result.predictions)
            for descriptor in self._target_descriptors
        )
        available = sum(item.status == "available" for item in outcomes)
        status = (
            "complete" if available == len(outcomes)
            else "partial" if available
            else "error"
        )
        missing_targets = tuple(
            item.ml_name
            for item in self._target_descriptors
            if item.ml_name not in result.predictions
        )
        if status != "complete":
            logger.warning(
                "Predict non-complete target result for %s; missing target(s): %s",
                result.case_id,
                ", ".join(missing_targets),
            )
        message = (
            _PARTIAL_RESULT_MESSAGE if status == "partial"
            else _RUNTIME_FAILURE_MESSAGE if status == "error"
            else result.message
        )
        return ResultRow(
            case_id=result.case_id,
            status=status,
            message=self._clean_message(message),
            target_outcomes=outcomes,
            derived_metrics=enrich_target_outcomes(
                result.context.capacity_inputs if result.context is not None else (),
                outcomes,
            ),
            execution_context=result.context,
        )

    def invalid_result(self, case_id: str, message: str) -> ResultRow:
        """Build a row-level invalid result without model execution."""
        return ResultRow(
            case_id=case_id,
            status="invalid",
            message=self._clean_message(self._validation_message(case_id, message)),
        )

    def running_result(self, case_id: str) -> ResultRow:
        """Build a row-level running result."""
        return ResultRow(case_id=case_id, status="running")

    def cancelled_result(
        self,
        case_id: str,
        message: str = "Prediction cancelled.",
        *,
        context: PredictionExecutionContext,
    ) -> ResultRow:
        """Build a row-level cancelled result."""
        return ResultRow(
            case_id=case_id,
            status="cancelled",
            message=self._clean_message(message),
            execution_context=context,
        )

    def infrastructure_failure_result(
        self,
        case_id: str,
        message: str,
        *,
        context: PredictionExecutionContext,
    ) -> ResultRow:
        """Build an error row for a runner/infrastructure failure."""
        self._log_runtime_failure(case_id, message)
        return ResultRow(
            case_id=case_id,
            status="error",
            message=_RUNTIME_FAILURE_MESSAGE,
            execution_context=context,
        )

    def _validation_message(self, case_id: str, message: str) -> str:
        raw_messages = tuple(
            item.strip() for item in str(message).split(";") if item.strip()
        )
        projected = tuple(
            self._project_validation_item(item) for item in raw_messages
        )
        if projected and all(projected):
            return " / ".join(projected)
        logger.warning(
            "Unrecognized Predict validation detail for %s: %s",
            case_id,
            message,
        )
        return "입력값을 확인해 주세요."

    def _project_validation_item(self, message: str) -> str:
        for pattern, formatter in _VALIDATION_MESSAGE_PATTERNS:
            match = pattern.fullmatch(message.strip())
            if match is None:
                continue
            values = match.groupdict()
            label = self._input_labels.get(values["key"], "해당 입력 항목")
            return formatter(label, values)
        if _contains_korean(message):
            return message
        return ""

    def _log_runtime_failure(self, case_id: str, message: str) -> None:
        logger.error("Predict runtime failure for %s: %s", case_id, message)

    def _target_outcome(
        self,
        descriptor: PredictionTargetDescriptor,
        predictions,
    ) -> TargetOutcome:  # noqa: ANN001
        common = dict(
            target_identity=descriptor.target_identity,
            result_feature_identity=descriptor.result_feature_identity,
            result_key=descriptor.result_key,
            canonical_unit=descriptor.canonical_unit,
            value_source=descriptor.value_source,
        )
        if descriptor.ml_name not in predictions:
            return TargetOutcome(
                **common,
                status="unavailable",
                reason_code="missing_service_output",
                message="Expected target output was not provided.",
            )
        try:
            number = float(predictions[descriptor.ml_name])
        except (TypeError, ValueError):
            return TargetOutcome(
                **common,
                status="failed",
                reason_code="invalid_numeric_output",
                message="Target output is not numeric.",
            )
        if not isfinite(number):
            return TargetOutcome(
                **common,
                status="failed",
                reason_code="non_finite_output",
                message="Target output is not finite.",
            )
        return TargetOutcome(**common, status="available", raw_value=number)

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


_RUNTIME_FAILURE_MESSAGE = (
    "예측 실행 중 문제가 발생했습니다. 잠시 후 다시 실행해 주세요."
)
_PARTIAL_RESULT_MESSAGE = (
    "일부 예측 결과를 생성하지 못했습니다. 생성된 결과를 확인해 주세요."
)
_UNIT_BY_RESULT_KEY = {
    "cooling_power": "W",
    "heating_power": "W",
    "ref_qty": "kg",
    "cooling_hz": "Hz",
    "heating_hz": "Hz",
}


def _canonical_legacy_unit(result_key: str) -> str:
    try:
        return _UNIT_BY_RESULT_KEY[result_key]
    except KeyError as exc:
        raise ValueError(
            f"Predict canonical unit is missing for result key {result_key}"
        ) from exc


def _required_message(label: str, _values: dict[str, str]) -> str:
    return f"{label}: 필수 입력값입니다."


def _numeric_message(label: str, _values: dict[str, str]) -> str:
    return f"{label}: 숫자로 입력해 주세요."


def _range_message(label: str, values: dict[str, str]) -> str:
    return (
        f"{label}: {values['minimum']} 이상 {values['maximum']} 이하로 입력해 주세요."
    )


def _allowed_values_message(label: str, values: dict[str, str]) -> str:
    return f"{label}: 허용된 값({values['allowed']}) 중에서 선택해 주세요."


_FIELD_KEY = r"(?P<key>[A-Za-z_][A-Za-z0-9_]*)"
_VALIDATION_MESSAGE_PATTERNS = (
    (
        re.compile(rf"{_FIELD_KEY} is required\.?", re.IGNORECASE),
        _required_message,
    ),
    (
        re.compile(rf"{_FIELD_KEY} must be numeric\.?", re.IGNORECASE),
        _numeric_message,
    ),
    (
        re.compile(
            rf"{_FIELD_KEY} must be between "
            r"(?P<minimum>.+?) and (?P<maximum>.+?)\.?",
            re.IGNORECASE,
        ),
        _range_message,
    ),
    (
        re.compile(
            rf"{_FIELD_KEY} must be one of: (?P<allowed>.+?)\.?",
            re.IGNORECASE,
        ),
        _allowed_values_message,
    ),
)


def _contains_korean(message: str) -> bool:
    return any("\uac00" <= character <= "\ud7a3" for character in message)
