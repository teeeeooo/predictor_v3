"""Convert Predict session rows into core predictor inputs."""

from dataclasses import dataclass, field
from typing import Any

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

    _FIELD_TO_FEATURE = {
        "capacity": "Cooling Capa",
        "heating_capacity": "Heating Capa",
        "mapped_volume": "ID Volume",
        "evap_area": "Evap Area",
        "evap_volume": "Evap Volume",
        "od_volume": "OD Volume",
        "cond_area": "Cond Area",
        "cond_volume": "Cond Volume",
        "comp_eer": "Comp EER",
        "comp_cc": "Comp cc",
    }
    _REFRIGERANT_FEATURES = {
        "R410A": "R410A",
        "R32": "R32",
        "R290": "R290",
    }
    _EXPANSION_FEATURES = {
        "EEV": "EEV",
        "Capi": "Capi",
    }

    def build_request(self, case: CaseRow) -> RowInputOutcome:
        """Return a structured request or row-level validation errors."""
        errors: list[str] = []
        warnings: list[str] = []
        row_input: dict[str, Any] = {}
        values = {**case.autofill_values, **case.input_values}

        capacity = values.get("capacity")
        if self._is_blank(capacity):
            errors.append("Cooling capacity is required.")

        for key, feature in self._FIELD_TO_FEATURE.items():
            value = values.get(key)
            if self._is_blank(value):
                continue
            try:
                row_input[feature] = float(value)
            except (TypeError, ValueError):
                errors.append(f"{key} must be numeric.")

        self._apply_one_hot(
            values.get("refrigerant"),
            self._REFRIGERANT_FEATURES,
            row_input,
            warnings,
        )
        self._apply_one_hot(
            values.get("expansion_device"),
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
        mapping: dict[str, str],
        row_input: dict[str, Any],
        warnings: list[str],
    ) -> None:
        if self._is_blank(raw_value):
            return
        selected = str(raw_value).strip()
        for feature in mapping.values():
            row_input[feature] = 0
        if selected in mapping:
            row_input[mapping[selected]] = 1
        else:
            warnings.append(f"Unsupported option ignored: {selected}")

    def _is_blank(self, value: Any) -> bool:
        return value is None or str(value).strip() == ""
