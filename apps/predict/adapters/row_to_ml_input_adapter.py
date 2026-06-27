"""Convert Predict session rows into core predictor inputs."""

from dataclasses import dataclass, field
from typing import Any

from apps.predict.schema.column_schema_adapter import (
    PredictColumn,
    build_input_column_schema,
)
from apps.predict.state.case_row import CaseRow


@dataclass(frozen=True)
class PredictionInputRequest:
    """Validated input for one core prediction call."""

    case_id: str
    row_input: dict[str, Any]


@dataclass(frozen=True)
class RowInputOutcome:
    """Adapter outcome for one case row."""

    case_id: str
    request: PredictionInputRequest | None = None
    errors: tuple[str, ...] = ()
    warnings: tuple[str, ...] = field(default_factory=tuple)

    @property
    def is_valid(self) -> bool:
        """Return whether this row can be sent to prediction service."""
        return self.request is not None and not self.errors


class RowToMlInputAdapter:
    """Build core predictor input dictionaries without importing Qt."""

    _REFRIGERANT_FEATURES = ("R410A", "R32", "R290")
    _EXPANSION_FEATURES = ("EEV", "Capi")

    def __init__(self, columns: tuple[PredictColumn, ...] | None = None) -> None:
        self._columns = columns or build_input_column_schema()

    def build_request(self, case: CaseRow) -> RowInputOutcome:
        """Return a structured request or row-level validation errors."""
        errors: list[str] = []
        warnings: list[str] = []
        row_input: dict[str, Any] = {}
        values = {**case.autofill_values, **case.input_values}

        capacity = values.get("cooling_capa")
        if self._is_blank(capacity):
            errors.append("cooling_capa is required.")

        for column in self._columns:
            if not column.ml_feature:
                continue
            value = values.get(column.key)
            if self._is_blank(value):
                continue
            converted = self._safe_float(value)
            if converted is None:
                errors.append(f"{column.key} must be numeric.")
                continue
            row_input[column.ml_feature] = converted

        self._apply_one_hot(
            values.get("ref_type"),
            self._REFRIGERANT_FEATURES,
            row_input,
            warnings,
        )
        self._apply_one_hot(
            values.get("exp_type"),
            self._EXPANSION_FEATURES,
            row_input,
            warnings,
        )

        if errors:
            return RowInputOutcome(
                case_id=case.case_id,
                errors=tuple(errors),
                warnings=tuple(warnings),
            )
        return RowInputOutcome(
            case_id=case.case_id,
            request=PredictionInputRequest(case_id=case.case_id, row_input=row_input),
            warnings=tuple(warnings),
        )

    def build_requests(self, cases: list[CaseRow]) -> list[RowInputOutcome]:
        """Build request outcomes for several case rows."""
        return [self.build_request(case) for case in cases]

    def _apply_one_hot(
        self,
        raw_value: Any,
        features: tuple[str, ...],
        row_input: dict[str, Any],
        warnings: list[str],
    ) -> None:
        for feature in features:
            row_input[feature] = 0.0
        if self._is_blank(raw_value):
            return
        selected = str(raw_value).strip()
        if selected in features:
            row_input[selected] = 1.0
        else:
            warnings.append(f"Unsupported option ignored: {selected}")

    def _is_blank(self, value: Any) -> bool:
        return value is None or str(value).strip() == ""

    def _safe_float(self, value: Any) -> float | None:
        try:
            return float(value)
        except (TypeError, ValueError):
            return None


def build_prediction_input_request(case: CaseRow) -> RowInputOutcome:
    """Build one prediction input request with the default adapter."""
    return RowToMlInputAdapter().build_request(case)
