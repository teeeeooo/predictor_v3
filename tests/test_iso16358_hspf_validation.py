from copy import deepcopy
import json

import pytest

from core.calculator_iso16358 import ISO16358Calculator
from tests.test_iso16358_hspf_golden import (
    OFFICIAL_GOLDEN_SAMPLE,
    make_phase1_calculator,
)


def schema_completeness_fixture_not_expected_tuning():
    return deepcopy(OFFICIAL_GOLDEN_SAMPLE)


def remove_nested(data, *keys):
    target = data
    for key in keys[:-1]:
        target = target[key]
    target.pop(keys[-1])


def make_ks_config_calculator(tmp_path, load_line):
    config_path = tmp_path / "iso16358_hspf_validation_config.json"
    config = {
        "mode": "heating",
        "hspf": {
            "enabled": True,
            "profile": "ks_c_9306_hspf",
            "required_points": {
                "7": ["full", "half", "min"],
                "2": ["defrost"],
                "-7": ["max"],
            },
            "load_line": load_line,
            "bin_hours_key": "hspf_bin_hours",
        },
        "hspf_bin_hours": [{"j": 1, "tj": 7, "nj": 1}],
    }
    config_path.write_text(json.dumps(config), encoding="utf-8")
    return ISO16358Calculator(str(config_path))


def test_ks_c9306_hspf_input_must_be_dict(tmp_path):
    calculator = make_phase1_calculator(tmp_path)

    with pytest.raises(ValueError, match="ks_c_9306_hspf: must be dict"):
        calculator.calculate_hspf({"ks_c_9306_hspf": "invalid"})


def test_ks_c9306_hspf_profile_requires_ks_input(tmp_path):
    calculator = make_phase1_calculator(tmp_path)

    with pytest.raises(ValueError, match="Missing ks_c_9306_hspf input"):
        calculator.calculate_hspf({})


def test_ks_c9306_hspf_capacity_is_required(tmp_path):
    calculator = make_phase1_calculator(tmp_path)
    data = schema_completeness_fixture_not_expected_tuning()
    remove_nested(data, "ks_c_9306_hspf", "capacity")

    with pytest.raises(ValueError, match="Missing KS C 9306 HSPF capacity input"):
        calculator.calculate_hspf(data)


def test_ks_c9306_hspf_power_is_required(tmp_path):
    calculator = make_phase1_calculator(tmp_path)
    data = schema_completeness_fixture_not_expected_tuning()
    remove_nested(data, "ks_c_9306_hspf", "power")

    with pytest.raises(ValueError, match="Missing KS C 9306 HSPF power input"):
        calculator.calculate_hspf(data)


def test_ks_c9306_hspf_capacity_rated_7_is_required(tmp_path):
    calculator = make_phase1_calculator(tmp_path)
    data = schema_completeness_fixture_not_expected_tuning()
    remove_nested(data, "ks_c_9306_hspf", "capacity", "rated", "7")

    with pytest.raises(
        ValueError,
        match=r"Missing KS C 9306 HSPF capacity\.rated\.7 input",
    ):
        calculator.calculate_hspf(data)


def test_ks_c9306_hspf_capacity_intermediate_7_is_required(tmp_path):
    calculator = make_phase1_calculator(tmp_path)
    data = schema_completeness_fixture_not_expected_tuning()
    remove_nested(data, "ks_c_9306_hspf", "capacity", "intermediate", "7")

    with pytest.raises(
        ValueError,
        match=r"Missing KS C 9306 HSPF capacity\.intermediate\.7 input",
    ):
        calculator.calculate_hspf(data)


def test_ks_c9306_hspf_capacity_min_7_is_required(tmp_path):
    calculator = make_phase1_calculator(tmp_path)
    data = schema_completeness_fixture_not_expected_tuning()
    remove_nested(data, "ks_c_9306_hspf", "capacity", "min", "7")

    with pytest.raises(
        ValueError,
        match=r"Missing KS C 9306 HSPF capacity\.min\.7 input",
    ):
        calculator.calculate_hspf(data)


def test_ks_c9306_hspf_capacity_defrost_2_is_required(tmp_path):
    calculator = make_phase1_calculator(tmp_path)
    data = schema_completeness_fixture_not_expected_tuning()
    remove_nested(data, "ks_c_9306_hspf", "capacity", "max", "def")

    with pytest.raises(
        ValueError,
        match=r"Missing KS C 9306 HSPF capacity\.max\.def input",
    ):
        calculator.calculate_hspf(data)


def test_ks_c9306_hspf_capacity_max_minus7_is_required(tmp_path):
    calculator = make_phase1_calculator(tmp_path)
    data = schema_completeness_fixture_not_expected_tuning()
    remove_nested(data, "ks_c_9306_hspf", "capacity", "max", "-7")

    with pytest.raises(
        ValueError,
        match=r"Missing KS C 9306 HSPF capacity\.max\.-7 input",
    ):
        calculator.calculate_hspf(data)


def test_ks_c9306_hspf_power_max_def_is_required(tmp_path):
    calculator = make_phase1_calculator(tmp_path)
    data = schema_completeness_fixture_not_expected_tuning()
    remove_nested(data, "ks_c_9306_hspf", "power", "max", "def")

    with pytest.raises(
        ValueError,
        match=r"Missing KS C 9306 HSPF power\.max\.def input",
    ):
        calculator.calculate_hspf(data)


def test_ks_c9306_hspf_negative_capacity_is_invalid(tmp_path):
    calculator = make_phase1_calculator(tmp_path)
    data = schema_completeness_fixture_not_expected_tuning()
    data["ks_c_9306_hspf"]["capacity"]["min"]["7"] = -1.0

    with pytest.raises(
        ValueError,
        match=r"Invalid KS C 9306 HSPF capacity\.min\.7: must be positive number",
    ):
        calculator.calculate_hspf(data)


def test_ks_c9306_hspf_correction_cd_must_be_less_than_one(tmp_path):
    calculator = make_phase1_calculator(tmp_path)
    data = schema_completeness_fixture_not_expected_tuning()
    data["ks_c_9306_hspf"]["correction"]["cd"] = 1.0

    with pytest.raises(
        ValueError,
        match=r"Invalid KS C 9306 HSPF correction\.cd: must be >= 0 and < 1",
    ):
        calculator.calculate_hspf(data)


def test_ks_c9306_hspf_load_line_requires_slope_and_intercept(tmp_path):
    calculator = make_phase1_calculator(tmp_path)
    data = schema_completeness_fixture_not_expected_tuning()
    data["ks_c_9306_hspf"]["load_line"] = {"slope": 100.0}

    with pytest.raises(
        ValueError,
        match="load_line: slope and intercept are required together",
    ):
        calculator.calculate_hspf(data)


def test_ks_c9306_hspf_config_load_line_empty_dict_is_invalid(tmp_path):
    calculator = make_ks_config_calculator(tmp_path, {})

    with pytest.raises(
        ValueError,
        match="Invalid KS C 9306 HSPF load_line: source is required",
    ):
        calculator.calculate_hspf(schema_completeness_fixture_not_expected_tuning())


def test_ks_c9306_hspf_config_load_line_source_is_required(tmp_path):
    calculator = make_ks_config_calculator(
        tmp_path,
        {
            "zero_load_temp": 16.0,
            "full_load_temp": -7.0,
            "rated_capacity_factor": 0.82,
        },
    )

    with pytest.raises(
        ValueError,
        match="Invalid KS C 9306 HSPF load_line: source is required",
    ):
        calculator.calculate_hspf(schema_completeness_fixture_not_expected_tuning())


def test_ks_c9306_hspf_config_load_line_required_fields(tmp_path):
    calculator = make_ks_config_calculator(
        tmp_path,
        {"source": "rated_heating_capacity"},
    )

    with pytest.raises(
        ValueError,
        match=(
            "Invalid KS C 9306 HSPF load_line: zero_load_temp, "
            "full_load_temp, and rated_capacity_factor are required"
        ),
    ):
        calculator.calculate_hspf(schema_completeness_fixture_not_expected_tuning())


def test_ks_c9306_hspf_config_load_line_source_must_be_allowed(tmp_path):
    calculator = make_ks_config_calculator(
        tmp_path,
        {
            "source": "unknown_capacity",
            "zero_load_temp": 16.0,
            "full_load_temp": -7.0,
            "rated_capacity_factor": 0.82,
        },
    )

    with pytest.raises(
        ValueError,
        match="Invalid KS C 9306 HSPF load_line source: unknown_capacity",
    ):
        calculator.calculate_hspf(schema_completeness_fixture_not_expected_tuning())


def test_ks_c9306_hspf_config_load_line_rated_heating_source_passes(tmp_path):
    calculator = make_ks_config_calculator(
        tmp_path,
        {
            "source": "rated_heating_capacity",
            "zero_load_temp": 16.0,
            "full_load_temp": -7.0,
            "rated_capacity_factor": 0.82,
        },
    )

    result = calculator.calculate_hspf(schema_completeness_fixture_not_expected_tuning())

    assert result["HSPF"] > 0


def test_ks_c9306_hspf_lower_stage_2c_and_minus7_are_optional(tmp_path):
    calculator = make_phase1_calculator(tmp_path)
    data = schema_completeness_fixture_not_expected_tuning()

    for quantity in ("capacity", "power"):
        for stage in ("min", "intermediate", "rated"):
            data["ks_c_9306_hspf"][quantity][stage].pop("-7", None)
            data["ks_c_9306_hspf"][quantity][stage].pop("2", None)

    result = calculator.calculate_hspf(data)

    assert result["hspf"] > 0


def test_ks_c9306_hspf_stage_2c_derived_from_rule_based_minus7(tmp_path):
    calculator = make_phase1_calculator(tmp_path)
    data = schema_completeness_fixture_not_expected_tuning()
    hspf_input = data["ks_c_9306_hspf"]

    for quantity in ("capacity", "power"):
        hspf_input[quantity]["rated"].pop("2", None)
        hspf_input[quantity]["rated"].pop("-7", None)

    capacity_7 = hspf_input["capacity"]["rated"]["7"]
    power_7 = hspf_input["power"]["rated"]["7"]
    expected_capacity_minus7 = capacity_7 * 0.601
    expected_power_minus7 = power_7 * 0.801
    expected_capacity_2 = (
        expected_capacity_minus7 + (capacity_7 - expected_capacity_minus7) * 9 / 14
    )
    expected_power_2 = (
        expected_power_minus7 + (power_7 - expected_power_minus7) * 9 / 14
    )

    actual_capacity_2 = calculator._ks_hspf_stage_value(
        hspf_input, "capacity", "rated", "2"
    )
    actual_power_2 = calculator._ks_hspf_stage_value(
        hspf_input, "power", "rated", "2"
    )

    assert actual_capacity_2 == pytest.approx(expected_capacity_2)
    assert actual_power_2 == pytest.approx(expected_power_2)


def test_ks_c9306_hspf_stage_2c_derived_from_input_minus7(tmp_path):
    calculator = make_phase1_calculator(tmp_path)
    data = schema_completeness_fixture_not_expected_tuning()
    hspf_input = data["ks_c_9306_hspf"]

    hspf_input["capacity"]["intermediate"]["-7"] = 1200.0
    hspf_input["power"]["intermediate"]["-7"] = 400.0
    hspf_input["capacity"]["intermediate"].pop("2", None)
    hspf_input["power"]["intermediate"].pop("2", None)

    capacity_7 = hspf_input["capacity"]["intermediate"]["7"]
    power_7 = hspf_input["power"]["intermediate"]["7"]
    expected_capacity_2 = 1200.0 + (capacity_7 - 1200.0) * 9 / 14
    expected_power_2 = 400.0 + (power_7 - 400.0) * 9 / 14

    actual_capacity_2 = calculator._ks_hspf_stage_value(
        hspf_input, "capacity", "intermediate", "2"
    )
    actual_power_2 = calculator._ks_hspf_stage_value(
        hspf_input, "power", "intermediate", "2"
    )

    assert actual_capacity_2 == pytest.approx(expected_capacity_2)
    assert actual_power_2 == pytest.approx(expected_power_2)


def test_ks_c9306_hspf_stage_2c_input_overrides_fallback(tmp_path):
    calculator = make_phase1_calculator(tmp_path)
    data = schema_completeness_fixture_not_expected_tuning()
    hspf_input = data["ks_c_9306_hspf"]

    hspf_input["capacity"]["min"]["2"] = 1234.5
    hspf_input["power"]["min"]["2"] = 345.6
    hspf_input["capacity"]["min"]["-7"] = 700.0
    hspf_input["power"]["min"]["-7"] = 150.0

    assert (
        calculator._ks_hspf_stage_value(hspf_input, "capacity", "min", "2")
        == 1234.5
    )
    assert (
        calculator._ks_hspf_stage_value(hspf_input, "power", "min", "2")
        == 345.6
    )


def test_ks_c9306_hspf_frost_runtime_accepts_missing_lower_stage_2c(tmp_path):
    calculator = make_phase1_calculator(tmp_path)
    data = schema_completeness_fixture_not_expected_tuning()

    for quantity in ("capacity", "power"):
        for stage in ("min", "intermediate", "rated"):
            data["ks_c_9306_hspf"][quantity][stage].pop("2", None)

    detail = calculator._ks_hspf_bin(
        2.0, 2000.0, 1.0, data["ks_c_9306_hspf"]
    )

    assert detail["bin_energy"] > 0


def test_ks_c9306_hspf_golden_fixture_passes_validation(tmp_path):
    calculator = make_phase1_calculator(tmp_path)
    data = schema_completeness_fixture_not_expected_tuning()

    result = calculator.calculate_hspf(data)

    assert result["HSPF"] > 0
