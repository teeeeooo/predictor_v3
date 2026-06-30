"""Convert Predict session rows into core predictor inputs."""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

from apps.predict.schema.column_schema_adapter import (
    PredictColumn,
    build_input_column_schema,
)
from apps.predict.state.case_row import CaseRow
from core.ml.feature_catalog import load_feature_catalog, validate_feature_catalog
from core.ml.feature_catalog_projection import one_hot_group


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

    _ONE_HOT_INPUT_GROUPS = {
        "ref_type": "refrigerant",
        "exp_type": "expansion_device",
    }

    def __init__(
        self,
        columns: tuple[PredictColumn, ...] | None = None,
        one_hot_groups: Mapping[str, Sequence[str]] | None = None,
    ) -> None:
        self._columns = columns or build_input_column_schema()
        self._one_hot_groups = (
            self._normalize_one_hot_groups(one_hot_groups)
            if one_hot_groups is not None
            else self._load_default_one_hot_groups()
        )

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

        for input_key, group_name in self._ONE_HOT_INPUT_GROUPS.items():
            self._apply_one_hot(
                values.get(input_key),
                self._one_hot_groups[group_name],
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

    def _load_default_one_hot_groups(self) -> dict[str, tuple[str, ...]]:
        catalog = load_feature_catalog()
        errors = validate_feature_catalog(catalog)
        if errors:
            joined = "; ".join(errors)
            raise RuntimeError(f"invalid predictor one-hot feature catalog: {joined}")
        return {
            group_name: one_hot_group(catalog.rows, group_name)
            for group_name in self._ONE_HOT_INPUT_GROUPS.values()
        }

    def _normalize_one_hot_groups(
        self,
        groups: Mapping[str, Sequence[str]],
    ) -> dict[str, tuple[str, ...]]:
        normalized: dict[str, tuple[str, ...]] = {}
        for group_name in self._ONE_HOT_INPUT_GROUPS.values():
            try:
                features = tuple(groups[group_name])
            except KeyError as exc:
                raise ValueError(
                    f"missing one-hot group '{group_name}' in feature catalog"
                ) from exc
            if not features:
                raise ValueError(
                    f"missing one-hot feature(s) for group '{group_name}'"
                )
            normalized[group_name] = features
        return normalized

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
