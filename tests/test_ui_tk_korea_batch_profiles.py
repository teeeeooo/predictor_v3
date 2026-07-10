"""Focused tests for KOREA CSPF/HSPF batch profiles."""

from __future__ import annotations

from apps.calculator.ui.batch.controller import BatchMatrixCalculationController
from apps.calculator.ui.batch.models import BatchRowState
from apps.calculator.ui.batch_dialogs.profiles.korea_cspf import (
    CSEC,
    CSPF,
    DECLARED_CAPACITY,
    FULL_CAPACITY,
    FULL_POWER,
    HALF_CAPACITY,
    HALF_POWER,
    KOREA_CSPF_MATRIX_SPEC,
    KoreaCspfBatchHandler,
    MIN_CAPACITY,
    MIN_POWER,
)
from apps.calculator.ui.batch_dialogs.profiles.korea_hspf import (
    DEFROST_CAPACITY,
    DEFROST_POWER,
    HSEC,
    HSPF,
    HSTL,
    KOREA_HSPF_MATRIX_SPEC,
    KoreaHspfBatchHandler,
    MAX_CAPACITY,
    MAX_POWER,
    RATED_COOLING_CAPACITY,
)


KOREA_CSPF_SAMPLE = {
    DECLARED_CAPACITY: "3500",
    FULL_CAPACITY: "3600",
    FULL_POWER: "900",
    HALF_CAPACITY: "1700",
    HALF_POWER: "380",
    MIN_CAPACITY: "900",
    MIN_POWER: "250",
}
KOREA_HSPF_SAMPLE = {
    RATED_COOLING_CAPACITY: "3500",
    FULL_CAPACITY: "4200",
    FULL_POWER: "1200",
    HALF_CAPACITY: "2400",
    HALF_POWER: "650",
    MIN_CAPACITY: "1200",
    MIN_POWER: "360",
    DEFROST_CAPACITY: "3000",
    DEFROST_POWER: "1100",
    MAX_CAPACITY: "3600",
    MAX_POWER: "1400",
}


class _HeadlessMatrixTable:
    """Headless stand-in for BatchMatrixTable."""

    def __init__(self, spec, cases: list[dict[str, str]] | None = None) -> None:
        self.spec = spec
        self.cases = (
            [dict(c) for c in cases]
            if cases is not None
            else [dict(c) for c in self.spec.default_cases]
        )
        self._results: dict[int, dict[str, str]] = {}

    def set_result(self, logical_index: int, values: dict[str, str]) -> None:
        self._results[logical_index] = dict(values)
        if logical_index < len(self.cases):
            self.cases[logical_index].update(values)


def test_korea_cspf_batch_spec_contract() -> None:
    assert KOREA_CSPF_MATRIX_SPEC.profile_key == "korea_cspf"
    assert KOREA_CSPF_MATRIX_SPEC.input_keys == (
        DECLARED_CAPACITY,
        FULL_CAPACITY,
        FULL_POWER,
        HALF_CAPACITY,
        HALF_POWER,
        MIN_CAPACITY,
        MIN_POWER,
    )
    assert KOREA_CSPF_MATRIX_SPEC.result_keys == (CSPF, CSEC)
    assert len(KOREA_CSPF_MATRIX_SPEC.default_cases) == 5


def test_korea_hspf_batch_spec_contract() -> None:
    assert KOREA_HSPF_MATRIX_SPEC.profile_key == "korea_hspf"
    assert KOREA_HSPF_MATRIX_SPEC.input_keys == (
        RATED_COOLING_CAPACITY,
        FULL_CAPACITY,
        FULL_POWER,
        HALF_CAPACITY,
        HALF_POWER,
        MIN_CAPACITY,
        MIN_POWER,
        DEFROST_CAPACITY,
        DEFROST_POWER,
        MAX_CAPACITY,
        MAX_POWER,
    )
    assert KOREA_HSPF_MATRIX_SPEC.result_keys == (HSPF, HSTL, HSEC)
    assert len(KOREA_HSPF_MATRIX_SPEC.default_cases) == 5


def test_korea_cspf_batch_handler_calculates_sample_row_without_guide_outputs():
    result = KoreaCspfBatchHandler().calculate_row(dict(KOREA_CSPF_SAMPLE))

    assert result.state is BatchRowState.OK
    assert result.values == {CSPF: "4.559", CSEC: "248.8"}
    assert "current_tc" not in result.values
    assert "recommended_tc" not in result.values


def test_korea_hspf_batch_handler_calculates_sample_row_without_guide_outputs():
    result = KoreaHspfBatchHandler().calculate_row(dict(KOREA_HSPF_SAMPLE))

    assert result.state is BatchRowState.OK
    assert result.values == {HSPF: "2.874", HSTL: "6466.5", HSEC: "2250.0"}
    assert "current_tc" not in result.values
    assert "recommended_tc" not in result.values


def test_korea_batch_handlers_blank_and_invalid_rows() -> None:
    assert KoreaCspfBatchHandler().calculate_row({}).state is BatchRowState.PENDING
    assert KoreaHspfBatchHandler().calculate_row({}).state is BatchRowState.PENDING

    invalid_cspf = dict(KOREA_CSPF_SAMPLE)
    invalid_cspf[FULL_POWER] = "bad"
    invalid_hspf = dict(KOREA_HSPF_SAMPLE)
    invalid_hspf[MAX_POWER] = "bad"

    assert KoreaCspfBatchHandler().calculate_row(invalid_cspf).state is BatchRowState.ERROR
    assert KoreaHspfBatchHandler().calculate_row(invalid_hspf).state is BatchRowState.ERROR


def test_korea_batch_matrix_controller_calculates_cases() -> None:
    cspf_table = _HeadlessMatrixTable(KOREA_CSPF_MATRIX_SPEC, [KOREA_CSPF_SAMPLE, {}])
    hspf_table = _HeadlessMatrixTable(KOREA_HSPF_MATRIX_SPEC, [KOREA_HSPF_SAMPLE, {}])

    cspf_summary = BatchMatrixCalculationController(
        cspf_table,
        KoreaCspfBatchHandler(),
    ).recalculate()
    hspf_summary = BatchMatrixCalculationController(
        hspf_table,
        KoreaHspfBatchHandler(),
    ).recalculate()

    assert cspf_summary.valid_rows == 1
    assert cspf_summary.blank_rows == 1
    assert cspf_table._results[0][CSPF] == "4.559"
    assert hspf_summary.valid_rows == 1
    assert hspf_summary.blank_rows == 1
    assert hspf_table._results[0][HSPF] == "2.874"
