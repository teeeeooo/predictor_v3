"""Convert Predict session rows into core predictor inputs."""

from collections.abc import Mapping, Sequence
from dataclasses import replace
from typing import Any

from apps.predict.application.models import (
    PredictionInputOutcome,
    PredictionInputRequest,
)
from apps.predict.application.result_enrichment import (
    COOLING_CAPACITY_FEATURE_ID,
    HEATING_CAPACITY_FEATURE_ID,
    build_capacity_input_evidence,
)
from apps.predict.schema.column_schema_adapter import (
    PredictColumn,
    build_input_column_schema,
)
from apps.predict.state.case_row import CaseRow
from core.data_definition.contract import bootstrap_manifest
from core.data_definition.one_hot import (
    OneHotRuntimeCategory,
    OneHotRuntimeSnapshot,
    encode_one_hot_values,
    one_hot_runtime_snapshot,
)


class RowToMlInputAdapter:
    """Build core predictor input dictionaries without importing Qt."""

    def __init__(
        self,
        columns: tuple[PredictColumn, ...] | None = None,
        one_hot_groups: Mapping[str, Sequence[str]] | None = None,
        one_hot_snapshot: OneHotRuntimeSnapshot | None = None,
    ) -> None:
        if one_hot_groups is not None and one_hot_snapshot is not None:
            raise ValueError("provide one_hot_snapshot or legacy one_hot_groups, not both")
        self._columns = columns or build_input_column_schema()
        default_snapshot = one_hot_runtime_snapshot(bootstrap_manifest())
        self._one_hot_snapshot = (
            one_hot_snapshot
            if one_hot_snapshot is not None
            else self._legacy_snapshot(default_snapshot, one_hot_groups)
            if one_hot_groups is not None
            else default_snapshot
        )

    @property
    def generation_id(self) -> str:
        return self._one_hot_snapshot.generation_id

    def build_request(self, case: CaseRow) -> PredictionInputOutcome:
        """Return a structured request or row-level validation errors."""
        errors: list[str] = []
        warnings: list[str] = []
        row_input: dict[str, Any] = {}
        values = {**case.autofill_values, **case.input_values}

        cooling_column = next(
            (
                column for column in self._columns
                if column.feature_identity == COOLING_CAPACITY_FEATURE_ID
            ),
            None,
        )
        capacity = values.get(cooling_column.key) if cooling_column is not None else None
        if self._is_blank(capacity):
            key = cooling_column.key if cooling_column is not None else "cooling_capa"
            errors.append(f"{key} is required.")

        capacity_inputs = []
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
            if column.feature_identity in {
                COOLING_CAPACITY_FEATURE_ID,
                HEATING_CAPACITY_FEATURE_ID,
            }:
                capacity_inputs.append(
                    build_capacity_input_evidence(column, converted)
                )

        encoded = encode_one_hot_values(self._one_hot_snapshot, values)
        row_input.update(encoded.values)
        warnings.extend(encoded.warnings)

        if errors:
            return PredictionInputOutcome(
                case_id=case.case_id,
                errors=tuple(errors),
                warnings=tuple(warnings),
            )
        return PredictionInputOutcome(
            case_id=case.case_id,
            request=PredictionInputRequest(
                case_id=case.case_id,
                row_input=row_input,
                capacity_inputs=tuple(capacity_inputs),
            ),
            warnings=tuple(warnings),
        )

    def build_requests(self, cases: list[CaseRow]) -> list[PredictionInputOutcome]:
        """Build request outcomes for several case rows."""
        return [self.build_request(case) for case in cases]

    def _legacy_snapshot(
        self,
        default: OneHotRuntimeSnapshot,
        groups: Mapping[str, Sequence[str]],
    ) -> OneHotRuntimeSnapshot:
        """Adapt the pre-4F test seam without retaining a runtime group table."""
        normalized = []
        for group in default.groups:
            try:
                features = tuple(groups[group.group_key])
            except KeyError as exc:
                raise ValueError(
                    f"missing one-hot group '{group.group_key}' in feature catalog"
                ) from exc
            if not features:
                raise ValueError(
                    f"missing one-hot feature(s) for group '{group.group_key}'"
                )
            normalized.append(replace(
                group,
                categories=tuple(
                    OneHotRuntimeCategory(
                        f"legacy:{group.group_identity}:{index}",
                        name,
                        f"legacy:{group.group_identity}:{index}",
                        name,
                        index,
                    )
                    for index, name in enumerate(features, 1)
                ),
            ))
        return OneHotRuntimeSnapshot(default.generation_id, tuple(normalized))

    def _is_blank(self, value: Any) -> bool:
        return value is None or str(value).strip() == ""

    def _safe_float(self, value: Any) -> float | None:
        try:
            return float(value)
        except (TypeError, ValueError):
            return None


def build_prediction_input_request(case: CaseRow) -> PredictionInputOutcome:
    """Build one prediction input request with the default adapter."""
    return RowToMlInputAdapter().build_request(case)
