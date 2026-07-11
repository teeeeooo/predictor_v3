"""Brazil CSPF batch matrix schema and row result contract."""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType

from apps.calculator.ui.batch.matrix_models import (
    BatchMatrixSpec,
    MatrixMeasurementPointSpec,
    MatrixPhysicalRowType,
)
from apps.calculator.ui.batch.models import BatchRowState
from apps.calculator.ui.layout_constants import (
    BATCH_MATRIX_RESULT_PRIMARY_WIDTH_CHARS,
    BATCH_MATRIX_RESULT_SECONDARY_WIDTH_CHARS,
)


FULL_CAPACITY = "full_capacity"
FULL_POWER = "full_power"
HALF_CAPACITY = "half_capacity"
HALF_POWER = "half_power"
HALF_29_CAPACITY = "half_29_capacity"
HALF_29_POWER = "half_29_power"
THREE_POINT_CSPF = "three_point_cspf"
THREE_POINT_CSTL = "three_point_cstl"
THREE_POINT_CSEC = "three_point_csec"
TWO_POINT_CSPF = "two_point_cspf"
TWO_POINT_CSTL = "two_point_cstl"
TWO_POINT_CSEC = "two_point_csec"
RULE_1 = "rule_1"
MEASURED_29_HALF_EER = "measured_29_half_eer"
CALCULATED_29_BIN_EER = "calculated_29_bin_eer"
RULE_2 = "rule_2"
FINAL = "final"
ROW_STATUS = "row_status"

_REQUIRED_INPUT_KEYS = (
    FULL_CAPACITY,
    FULL_POWER,
    HALF_CAPACITY,
    HALF_POWER,
    HALF_29_CAPACITY,
    HALF_29_POWER,
)


BRAZIL_CSPF_MATRIX_SPEC = BatchMatrixSpec(
    profile_key="brazil_cspf_compliance",
    title="Brazil CSPF Compliance Batch Matrix",
    physical_rows=(MatrixPhysicalRowType.CAPACITY, MatrixPhysicalRowType.POWER),
    row_type_labels=MappingProxyType(
        {
            MatrixPhysicalRowType.CAPACITY: "Capacity",
            MatrixPhysicalRowType.POWER: "Power",
        }
    ),
    measurement_points=(
        MatrixMeasurementPointSpec(
            "35_full",
            "35 Full",
            MappingProxyType(
                {
                    MatrixPhysicalRowType.CAPACITY: FULL_CAPACITY,
                    MatrixPhysicalRowType.POWER: FULL_POWER,
                }
            ),
        ),
        MatrixMeasurementPointSpec(
            "35_half",
            "35 Half",
            MappingProxyType(
                {
                    MatrixPhysicalRowType.CAPACITY: HALF_CAPACITY,
                    MatrixPhysicalRowType.POWER: HALF_POWER,
                }
            ),
        ),
        MatrixMeasurementPointSpec(
            "29_half",
            "29 Half",
            MappingProxyType(
                {
                    MatrixPhysicalRowType.CAPACITY: HALF_29_CAPACITY,
                    MatrixPhysicalRowType.POWER: HALF_29_POWER,
                }
            ),
        ),
    ),
    result_metrics=(
        (THREE_POINT_CSPF, "3-point CSPF", BATCH_MATRIX_RESULT_PRIMARY_WIDTH_CHARS),
        (THREE_POINT_CSTL, "3-point CSTL", BATCH_MATRIX_RESULT_SECONDARY_WIDTH_CHARS),
        (THREE_POINT_CSEC, "3-point CSEC", BATCH_MATRIX_RESULT_SECONDARY_WIDTH_CHARS),
        (TWO_POINT_CSPF, "2-point CSPF", BATCH_MATRIX_RESULT_PRIMARY_WIDTH_CHARS),
        (TWO_POINT_CSTL, "2-point CSTL", BATCH_MATRIX_RESULT_SECONDARY_WIDTH_CHARS),
        (TWO_POINT_CSEC, "2-point CSEC", BATCH_MATRIX_RESULT_SECONDARY_WIDTH_CHARS),
        (RULE_1, "Rule 1", BATCH_MATRIX_RESULT_PRIMARY_WIDTH_CHARS),
        (MEASURED_29_HALF_EER, "Measured 29 Half EER", BATCH_MATRIX_RESULT_SECONDARY_WIDTH_CHARS),
        (CALCULATED_29_BIN_EER, "Calculated 29°C Bin EER", BATCH_MATRIX_RESULT_SECONDARY_WIDTH_CHARS),
        (RULE_2, "Rule 2", BATCH_MATRIX_RESULT_PRIMARY_WIDTH_CHARS),
        (FINAL, "Final", BATCH_MATRIX_RESULT_PRIMARY_WIDTH_CHARS),
        (ROW_STATUS, "Row Status", BATCH_MATRIX_RESULT_SECONDARY_WIDTH_CHARS),
    ),
    default_cases=({}, {}, {}, {}, {}),
)


@dataclass(frozen=True)
class BrazilCspfBatchCalculationResult:
    """UI batch row values and shared controller state."""

    values: dict[str, str]
    state: BatchRowState


__all__ = [
    "BRAZIL_CSPF_MATRIX_SPEC",
    "BrazilCspfBatchCalculationResult",
    "CALCULATED_29_BIN_EER",
    "FINAL",
    "FULL_CAPACITY",
    "FULL_POWER",
    "HALF_29_CAPACITY",
    "HALF_29_POWER",
    "HALF_CAPACITY",
    "HALF_POWER",
    "MEASURED_29_HALF_EER",
    "ROW_STATUS",
    "RULE_1",
    "RULE_2",
    "THREE_POINT_CSEC",
    "THREE_POINT_CSPF",
    "THREE_POINT_CSTL",
    "TWO_POINT_CSEC",
    "TWO_POINT_CSPF",
    "TWO_POINT_CSTL",
]
