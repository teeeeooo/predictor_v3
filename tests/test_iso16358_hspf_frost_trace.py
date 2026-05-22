import pytest

from tests.test_iso16358_hspf_formula_micro import (
    iso_points_with_extended,
    make_iso_micro_calculator,
    rated_for_load_at_7c,
    HALF_CAPACITY,
)


FROST_BOUNDARY_CASES = [
    (-10.0, False),
    (-7.0, False),
    (-6.0, True),
    (-1.0, True),
    (0.0, True),
    (5.0, True),
    (5.5, False),
    (6.0, False),
]


@pytest.mark.parametrize("tj,expected_frost", FROST_BOUNDARY_CASES)
def test_iso_hspf_common_bin_exposes_frost_flag(tmp_path, tj, expected_frost):
    calculator = make_iso_micro_calculator(
        tmp_path,
        [{"j": 1, "tj": tj, "nj": 1.0}],
    )
    result = calculator.calculate_hspf(
        iso_points_with_extended(
            rated_heating_capacity=rated_for_load_at_7c(HALF_CAPACITY)
        )
    )
    assert len(result["bin_details"]) == 1
    detail = result["bin_details"][0]
    assert "frost" in detail
    assert detail["frost"] is expected_frost
