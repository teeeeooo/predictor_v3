"""Focused EN14825 SEER additive core-detail regression tests."""

from __future__ import annotations

import pytest

from core.calculator_en14825 import EN14825Calculator


_POINTS = {
    "A": (3.6233, 0.847),
    "B": (2.4691, 0.389),
    "C": (1.5150, 0.137),
    "D": (1.1277, 0.062),
}
_ARGS = {
    "test_points": _POINTS,
    "p_to": 0.0066,
    "p_sb": 0.0012,
    "p_ck": 0.0,
    "p_off": 0.0012,
    "p_design_c": 3.5,
    "t_design_c": 35.0,
}


def test_seer_detail_path_preserves_public_result_and_uses_same_loop() -> None:
    calculator = EN14825Calculator()

    public_result = calculator.calculate_seer(**_ARGS)
    detail_result = calculator.calculate_seer_with_details(**_ARGS)

    assert tuple(public_result) == ("seer", "seer_on", "qc_kwh")
    assert {key: detail_result[key] for key in public_result} == public_result
    assert detail_result["bin_details"]
    numerator = sum(
        row["numerator_contribution"] for row in detail_result["bin_details"]
    )
    denominator = sum(
        row["energy_contribution"] for row in detail_result["bin_details"]
    )
    assert numerator / denominator == pytest.approx(public_result["seer_on"], abs=0.0005)
    assert all(row["interpolation"] for row in detail_result["bin_details"])
