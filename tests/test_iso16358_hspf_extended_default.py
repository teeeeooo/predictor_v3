import pytest

from tests.test_iso16358_hspf_formula_micro import make_iso_micro_calculator


def test_minus7_ext_measured_passthrough(tmp_path):
    calculator = make_iso_micro_calculator(
        tmp_path, [{"j": 1, "tj": 0.0, "nj": 1.0}]
    )
    resolved = {
        "2_ext": {"capacity": 4200.0, "power": 1700.0},
        "-7_ext": {"capacity": 1700.0, "power": 1300.0},
    }
    result = calculator._iso_hspf_extended_minus7_default(resolved)
    assert result["capacity"] == pytest.approx(1700.0)
    assert result["power"] == pytest.approx(1300.0)


def test_minus7_ext_default_uses_two_step_factor(tmp_path):
    # No -7_ext measured: factor must be applied via 2°C frost → 2°C non-frost
    # (×1.12 / ×1.06) then 2°C non-frost → -7°C (×0.734 / ×0.877).
    calculator = make_iso_micro_calculator(
        tmp_path, [{"j": 1, "tj": 0.0, "nj": 1.0}]
    )
    cap_2f, pow_2f = 4200.0, 1700.0
    resolved = {"2_ext": {"capacity": cap_2f, "power": pow_2f}}
    result = calculator._iso_hspf_extended_minus7_default(resolved)
    expected_capacity = cap_2f * 1.12 * 0.734
    expected_power = pow_2f * 1.06 * 0.877
    assert result["capacity"] == pytest.approx(expected_capacity)
    assert result["power"] == pytest.approx(expected_power)
    # Sanity check approximate target values from ISO original-text audit.
    assert result["capacity"] == pytest.approx(3452.7, abs=1.0)
    assert result["power"] == pytest.approx(1580.4, abs=2.0)


def test_minus7_ext_default_differs_from_direct_factor(tmp_path):
    # Guard against regression: applying 0.734/0.877 directly to 2_ext frost
    # (the old behavior) must NOT equal the new two-step result.
    calculator = make_iso_micro_calculator(
        tmp_path, [{"j": 1, "tj": 0.0, "nj": 1.0}]
    )
    cap_2f, pow_2f = 4200.0, 1700.0
    resolved = {"2_ext": {"capacity": cap_2f, "power": pow_2f}}
    result = calculator._iso_hspf_extended_minus7_default(resolved)
    direct_capacity = cap_2f * 0.734
    direct_power = pow_2f * 0.877
    assert abs(result["capacity"] - direct_capacity) > 100.0
    assert abs(result["power"] - direct_power) > 50.0
