from copy import deepcopy

import pytest

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


def test_ks_c9306_hspf_input_must_be_dict(tmp_path):
    calculator = make_phase1_calculator(tmp_path)

    with pytest.raises(ValueError, match="ks_c_9306_hspf: must be dict"):
        calculator.calculate_hspf({"ks_c_9306_hspf": "invalid"})


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


def test_ks_c9306_hspf_lower_stage_2c_and_minus7_are_optional(tmp_path):
    calculator = make_phase1_calculator(tmp_path)
    data = schema_completeness_fixture_not_expected_tuning()

    for quantity in ("capacity", "power"):
        for stage in ("min", "intermediate", "rated"):
            data["ks_c_9306_hspf"][quantity][stage].pop("-7", None)
            data["ks_c_9306_hspf"][quantity][stage].pop("2", None)

    result = calculator.calculate_hspf(data)

    assert result["hspf"] > 0


def test_ks_c9306_hspf_golden_fixture_passes_validation(tmp_path):
    calculator = make_phase1_calculator(tmp_path)
    data = schema_completeness_fixture_not_expected_tuning()

    result = calculator.calculate_hspf(data)

    assert result["HSPF"] > 0
