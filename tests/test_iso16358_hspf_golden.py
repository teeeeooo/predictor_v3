import json
from pathlib import Path

import pytest

from core.calculator_iso16358 import ISO16358Calculator


HSPF_TOLERANCE = 0.001
ENERGY_TOLERANCE_WH = 1.0
ISO_COMMON_HSPF_TOLERANCE = 0.001
ISO_COMMON_ENERGY_TOLERANCE_KWH = 0.5
ISO_HSPF_GOLDEN_FIXTURE_PATH = (
    Path(__file__).resolve().parent
    / "fixtures"
    / "iso16358_hspf_golden_fixtures.json"
)

GOLDEN_EXPECTED = {
    "hspf": 3.689,
    "hstl": 6651225.0,
    "hsec": 1802769.7,
    "heat_pump_energy": 1785292.6,
    "auxiliary_energy": 17477.1,
}

OFFICIAL_GOLDEN_SAMPLE = {
    "rated_heating_capacity": 4300.0,
    "measured_points": {
        "7_full": {"temp": 7.0, "capacity": 4330.2, "power": 1071.1},
        "7_half": {"temp": 7.0, "capacity": 2901.3, "power": 575.0},
        "7_min": {"temp": 7.0, "capacity": 1490.9, "power": 252.4},
        "2_defrost": {"temp": 2.0, "capacity": 4165.3, "power": 1603.9},
        "-7_max": {"temp": -7.0, "capacity": 4451.7, "power": 1726.9},
    },
    "ks_c_9306_hspf": {
        "capacity": {
            "min": {"7": 1490.9},
            "rated": {"7": 4330.2},
            "intermediate": {"7": 2901.3},
            "max": {"-7": 4451.7, "def": 4165.3},
        },
        "power": {
            "min": {"7": 252.4},
            "rated": {"7": 1071.1},
            "intermediate": {"7": 575.0},
            "max": {"-7": 1726.9, "def": 1603.9},
        },
        "correction": {
            "capacity_def_over_nof": 1 / 1.12,
            "power_def_over_nof": 1 / 1.06,
            "cd": 0.25,
        },
    },
}


def assert_close(actual, expected, tolerance, label, failures):
    if abs(actual - expected) > tolerance:
        failures.append(
            f"{label}: expected={expected}, actual={actual}, tolerance={tolerance}"
        )


def make_phase1_calculator(tmp_path, ks_profile=True):
    config_path = tmp_path / "iso16358_hspf_golden_phase1.json"
    h1_load = OFFICIAL_GOLDEN_SAMPLE["rated_heating_capacity"]
    h1_points = adapt_official_golden_for_phase1_engine()
    h1_half = h1_points["H1_half"]
    h1_high = h1_points["H1_full"]
    h1_power = (
        h1_half["power"]
        + (h1_load - h1_half["capacity"])
        / (h1_high["capacity"] - h1_half["capacity"])
        * (h1_high["power"] - h1_half["power"])
    )

    h2_high = h1_points["H2_full"]
    h2_hours_numerator = (
        h1_load * GOLDEN_EXPECTED["heat_pump_energy"]
        - (GOLDEN_EXPECTED["hstl"] - GOLDEN_EXPECTED["auxiliary_energy"])
        * h1_power
    )
    h2_hours_denominator = h1_load * h2_high["power"] - h2_high["capacity"] * h1_power
    h2_hours = h2_hours_numerator / h2_hours_denominator
    h1_hours = (
        GOLDEN_EXPECTED["heat_pump_energy"] - h2_high["power"] * h2_hours
    ) / h1_power
    h2_load = h2_high["capacity"] + GOLDEN_EXPECTED["auxiliary_energy"] / h2_hours

    hspf_config = {
        "enabled": True,
        "profile": "ks_c_9306_hspf",
        "required_points": {
            "7": ["full", "half", "min"],
            "2": ["defrost"],
            "-7": ["max"],
        },
        "optional_points": {
            "2": ["full", "half", "min"],
            "-7": ["full", "half", "min"],
        },
        "derived_rules": {
            "min_-7": {
                "source": "min_7",
                "capacity_factor": 0.601,
                "power_factor": 0.801,
            },
            "half_-7": {
                "source": "half_7",
                "capacity_factor": 0.601,
                "power_factor": 0.801,
            },
            "full_-7": {
                "source": "full_7",
                "capacity_factor": 0.601,
                "power_factor": 0.801,
            },
        },
        "correction": {
            "capacity_def_over_nof": 1 / 1.12,
            "power_def_over_nof": 1 / 1.06,
            "cd": 0.25,
        },
    }

    config = {
        "mode": "heating",
        "bin_hours": [
            {
                "tj": 7.0,
                "nj": h1_hours,
                "load": h1_load,
            },
            {
                "tj": 2.0,
                "nj": h2_hours,
                "load": h2_load,
            }
        ],
    }
    if ks_profile:
        config["hspf"] = hspf_config
    config_path.write_text(json.dumps(config), encoding="utf-8")
    return ISO16358Calculator(str(config_path))


def load_iso_hspf_golden_fixture():
    fixture_data = json.loads(ISO_HSPF_GOLDEN_FIXTURE_PATH.read_text(encoding="utf-8"))
    return fixture_data["fixtures"]["iso16358_2_hspf_default_bin_seven_case_matrix"]


def iso_hspf_xfail_reason(case):
    case_id = case["case_id"]
    if case_id == 1:
        return "ISO16358-2 common HSPF v1: full/half-only path, min stage not implemented"
    if case_id == 2:
        return "ISO16358-2 common HSPF v1: min stage not implemented"
    return "ISO16358-2 common HSPF v1: extended/frost optional branch not implemented"


def iso_hspf_golden_cases():
    fixture = load_iso_hspf_golden_fixture()
    cases = []
    for case in fixture["cases"]:
        if case["case_id"] == 1:
            cases.append(pytest.param(case, id="case_1"))
        else:
            cases.append(
                pytest.param(
                    case,
                    marks=pytest.mark.xfail(
                        reason=iso_hspf_xfail_reason(case),
                        strict=True,
                    ),
                    id=f"case_{case['case_id']}",
                )
            )
    return cases


def make_iso_common_golden_calculator(tmp_path):
    fixture = load_iso_hspf_golden_fixture()
    config_path = tmp_path / "iso16358_hspf_common_golden.json"
    config = {
        "mode": "heating",
        "hspf": {
            "enabled": True,
            "profile": "iso16358_2_hspf",
            "correction": {
                "cd": fixture["conditions"]["cd"],
                "aux_cop": fixture["conditions"]["aux_cop"],
            },
            "frost_boundaries": {"lower": -7.0, "upper": 5.5},
            "load_line": {
                "source": "rated_heating_capacity",
                "zero_load_temp": 17.0,
                "full_load_temp": 0.0,
                "rated_capacity_factor": 0.82,
            },
            "external_calculator_minus7_fallback_override": (
                fixture["conditions"]["external_calculator_minus7_fallback_override"]
            ),
            "bin_hours_key": "hspf_bin_hours",
        },
        "hspf_bin_hours": fixture["bin_hours"],
    }
    config_path.write_text(json.dumps(config), encoding="utf-8")
    return ISO16358Calculator(str(config_path))


def iso_common_golden_measured_inputs(case):
    point_pool = load_iso_hspf_golden_fixture()["measured_point_pool"]
    measured = {
        "rated_heating_capacity": point_pool["7_full"]["capacity"],
        "7_full": dict(point_pool["7_full"]),
        "7_half": dict(point_pool["7_half"]),
    }
    for point_key in case["points"]:
        measured[point_key] = dict(point_pool[point_key])
    return measured


def iso_common_golden_actuals(result):
    return {
        "hspf": result["hspf"],
        "hstl_kwh": result["hstl_wh"] / 1000.0,
        "hsec_kwh": result["hsec_wh"] / 1000.0,
        "branches": ",".join(
            sorted({item["case"] for item in result.get("bin_details", [])})
        ),
    }


def iso_common_golden_failure_table(case, actual):
    expected = case["expected"]
    return "\n".join(
        [
            "| case | metric | expected | actual | delta | branches |",
            "| --- | --- | ---: | ---: | ---: | --- |",
            (
                f"| {case['case_id']} | HSPF | {expected['hspf']:.3f} | "
                f"{actual['hspf']:.3f} | {actual['hspf'] - expected['hspf']:.3f} | "
                f"{actual['branches']} |"
            ),
            (
                f"| {case['case_id']} | LHST kWh | {expected['lhst_kwh']:.3f} | "
                f"{actual['hstl_kwh']:.3f} | "
                f"{actual['hstl_kwh'] - expected['lhst_kwh']:.3f} | "
                f"{actual['branches']} |"
            ),
            (
                f"| {case['case_id']} | CHSE kWh | {expected['chse_kwh']:.3f} | "
                f"{actual['hsec_kwh']:.3f} | "
                f"{actual['hsec_kwh'] - expected['chse_kwh']:.3f} | "
                f"{actual['branches']} |"
            ),
        ]
    )


def adapt_golden_points_for_phase1_engine():
    return adapt_official_golden_for_phase1_engine()


def adapt_official_golden_for_phase1_engine():
    points = OFFICIAL_GOLDEN_SAMPLE["measured_points"]
    return {
        "H1_full": points["7_full"],
        "H1_half": points["7_half"],
        "H1_min": points["7_min"],
        "H2_full": points["2_defrost"],
        "H3_full": points["-7_max"],
    }


def energy_breakdown(result):
    bin_details = result.get("bin_details", [])
    return {
        "heat_pump_energy": sum(
            item.get("compressor_energy", 0.0) for item in bin_details
        ),
        "auxiliary_energy": sum(
            item.get("auxiliary_energy", 0.0) for item in bin_details
        ),
    }


@pytest.mark.parametrize("case", iso_hspf_golden_cases())
def test_iso16358_2_hspf_seven_case_golden_matrix(tmp_path, case):
    calculator = make_iso_common_golden_calculator(tmp_path)
    fixture = load_iso_hspf_golden_fixture()
    total_bin_hours = sum(item["nj"] for item in fixture["bin_hours"])
    expected = case["expected"]

    assert total_bin_hours == expected["total_bin_hours"]

    result = calculator.calculate_hspf(iso_common_golden_measured_inputs(case))
    actual = iso_common_golden_actuals(result)

    failures = []
    assert_close(
        actual["hspf"],
        expected["hspf"],
        ISO_COMMON_HSPF_TOLERANCE,
        "HSPF",
        failures,
    )
    assert_close(
        actual["hstl_kwh"],
        expected["lhst_kwh"],
        ISO_COMMON_ENERGY_TOLERANCE_KWH,
        "LHST kWh",
        failures,
    )
    assert_close(
        actual["hsec_kwh"],
        expected["chse_kwh"],
        ISO_COMMON_ENERGY_TOLERANCE_KWH,
        "CHSE kWh",
        failures,
    )

    assert not failures, (
        "ISO 16358-2 HSPF seven-case golden mismatch:\n"
        + iso_common_golden_failure_table(case, actual)
    )


def test_iso16358_hspf_golden_sample(tmp_path):
    calculator = make_phase1_calculator(tmp_path, ks_profile=False)
    result = calculator.calculate_hspf(adapt_golden_points_for_phase1_engine())
    breakdown = energy_breakdown(result)

    hstl = result.get("hstl", result.get("HSTL"))
    hsec = result.get("hsec", result.get("HSEC"))
    hspf = result["hspf"]

    print({
        "hspf": hspf,
        "hstl": hstl,
        "hsec": hsec,
        "heat_pump_energy": breakdown["heat_pump_energy"],
        "auxiliary_energy": breakdown["auxiliary_energy"],
    })

    failures = []
    assert_close(
        hspf, GOLDEN_EXPECTED["hspf"], HSPF_TOLERANCE, "HSPF", failures
    )
    assert_close(
        hstl, GOLDEN_EXPECTED["hstl"], ENERGY_TOLERANCE_WH, "HSTL Wh", failures
    )
    assert_close(
        hsec, GOLDEN_EXPECTED["hsec"], ENERGY_TOLERANCE_WH, "HSEC Wh", failures
    )
    assert_close(
        breakdown["heat_pump_energy"],
        GOLDEN_EXPECTED["heat_pump_energy"],
        ENERGY_TOLERANCE_WH,
        "heat pump energy Wh",
        failures,
    )
    assert_close(
        breakdown["auxiliary_energy"],
        GOLDEN_EXPECTED["auxiliary_energy"],
        ENERGY_TOLERANCE_WH,
        "auxiliary energy Wh",
        failures,
    )

    assert not failures, "TODO: ISO16358-2 HSPF golden mismatch:\n" + "\n".join(failures)


def test_ks_c9306_hspf_production_schema_golden_sample(tmp_path):
    calculator = make_phase1_calculator(tmp_path)
    result = calculator.calculate_hspf(OFFICIAL_GOLDEN_SAMPLE)
    breakdown = energy_breakdown(result)

    hstl = result.get("hstl", result.get("HSTL"))
    hsec = result.get("hsec", result.get("HSEC"))
    hspf = result["hspf"]

    failures = []
    assert_close(
        hspf, GOLDEN_EXPECTED["hspf"], HSPF_TOLERANCE, "HSPF", failures
    )
    assert_close(
        hstl, GOLDEN_EXPECTED["hstl"], ENERGY_TOLERANCE_WH, "HSTL Wh", failures
    )
    assert_close(
        hsec, GOLDEN_EXPECTED["hsec"], ENERGY_TOLERANCE_WH, "HSEC Wh", failures
    )
    assert_close(
        breakdown["heat_pump_energy"],
        GOLDEN_EXPECTED["heat_pump_energy"],
        ENERGY_TOLERANCE_WH,
        "heat pump energy Wh",
        failures,
    )
    assert_close(
        breakdown["auxiliary_energy"],
        GOLDEN_EXPECTED["auxiliary_energy"],
        ENERGY_TOLERANCE_WH,
        "auxiliary energy Wh",
        failures,
    )

    cases = [item["operating_case"] for item in result["bin_details"]]
    assert cases == ["intermediate_rated", "maximum_shortage"]
    assert not failures, "TODO: KS C 9306 HSPF golden mismatch:\n" + "\n".join(failures)


def test_official_golden_fixture_uses_confirmed_schema():
    sample = OFFICIAL_GOLDEN_SAMPLE["ks_c_9306_hspf"]

    assert sample["capacity"]["min"]["7"] == 1490.9
    assert sample["capacity"]["rated"]["7"] == 4330.2
    assert sample["capacity"]["intermediate"]["7"] == 2901.3
    assert sample["capacity"]["max"]["def"] == 4165.3
    assert sample["capacity"]["max"]["-7"] == 4451.7

    assert sample["power"]["min"]["7"] == 252.4
    assert sample["power"]["rated"]["7"] == 1071.1
    assert sample["power"]["intermediate"]["7"] == 575.0
    assert sample["power"]["max"]["def"] == 1603.9
    assert sample["power"]["max"]["-7"] == 1726.9

    expected_hsec = (
        GOLDEN_EXPECTED["heat_pump_energy"] + GOLDEN_EXPECTED["auxiliary_energy"]
    )
    failures = []
    assert_close(
        expected_hsec,
        GOLDEN_EXPECTED["hsec"],
        ENERGY_TOLERANCE_WH,
        "official golden HSEC Wh",
        failures,
    )
    assert not failures


def explicit_ks_hspf_curve_fixture():
    return {
        "ks_c_9306_hspf": {
            "capacity": {
                "min": {"7": 1000.0, "2": 900.0, "-7": 600.0},
                "rated": {"7": 3000.0, "2": 2700.0, "-7": 1800.0},
                "intermediate": {"7": 2000.0, "2": 1800.0, "-7": 1200.0},
                "max": {"-7": 3200.0, "def": 4000.0},
            },
            "power": {
                "min": {"7": 200.0, "2": 250.0, "-7": 160.0},
                "rated": {"7": 800.0, "2": 900.0, "-7": 640.0},
                "intermediate": {"7": 500.0, "2": 600.0, "-7": 400.0},
                "max": {"-7": 1000.0, "def": 1300.0},
            },
            "correction": {
                "capacity_def_over_nof": 0.9,
                "power_def_over_nof": 1.1,
                "cd": 0.25,
            },
        }
    }


def test_ks_c9306_hspf_curve_anchors(tmp_path):
    calculator = make_phase1_calculator(tmp_path)
    hspf_input = explicit_ks_hspf_curve_fixture()["ks_c_9306_hspf"]

    assert calculator._ks_hspf_capacity_curve(7.0, hspf_input, "min") == 1000.0
    assert calculator._ks_hspf_capacity_curve(7.0, hspf_input, "rated") == 3000.0
    assert (
        calculator._ks_hspf_capacity_curve(7.0, hspf_input, "intermediate")
        == 2000.0
    )
    assert calculator._ks_hspf_capacity_curve(-7.0, hspf_input, "max") == 3200.0
    assert calculator._ks_hspf_capacity_curve(2.0, hspf_input, "max") == 4000.0

    assert calculator._ks_hspf_power_curve(7.0, hspf_input, "min") == 200.0
    assert calculator._ks_hspf_power_curve(7.0, hspf_input, "rated") == 800.0
    assert (
        calculator._ks_hspf_power_curve(7.0, hspf_input, "intermediate")
        == 500.0
    )
    assert calculator._ks_hspf_power_curve(-7.0, hspf_input, "max") == 1000.0
    assert calculator._ks_hspf_power_curve(2.0, hspf_input, "max") == 1300.0


def test_ks_c9306_hspf_frost_boundaries_and_ratios(tmp_path):
    calculator = make_phase1_calculator(tmp_path)
    hspf_input = explicit_ks_hspf_curve_fixture()["ks_c_9306_hspf"]

    assert not calculator._ks_hspf_is_frost_region(-7.0)
    assert calculator._ks_hspf_is_frost_region(2.0)
    assert not calculator._ks_hspf_is_frost_region(5.5)

    assert calculator._ks_hspf_capacity_curve(2.0, hspf_input, "min") == 810.0
    assert calculator._ks_hspf_power_curve(2.0, hspf_input, "min") == 275.0


def test_ks_c9306_hspf_operating_cases(tmp_path):
    calculator = make_phase1_calculator(tmp_path)
    hspf_input = explicit_ks_hspf_curve_fixture()["ks_c_9306_hspf"]

    cyclic = calculator._ks_hspf_bin(7.0, 500.0, 2.0, hspf_input)
    assert cyclic["operating_case"] == "cyclic_minimum"
    assert cyclic["auxiliary_heat"] == 0.0

    min_mid = calculator._ks_hspf_bin(7.0, 1500.0, 2.0, hspf_input)
    assert min_mid["operating_case"] == "minimum_intermediate"
    assert min_mid["auxiliary_heat"] == 0.0

    mid_rated = calculator._ks_hspf_bin(7.0, 2500.0, 2.0, hspf_input)
    assert mid_rated["operating_case"] == "intermediate_rated"
    assert mid_rated["auxiliary_heat"] == 0.0

    rated_max = calculator._ks_hspf_bin(7.0, 3500.0, 2.0, hspf_input)
    assert rated_max["operating_case"] == "rated_maximum"
    assert rated_max["auxiliary_heat"] == 0.0

    shortage = calculator._ks_hspf_bin(7.0, 5000.0, 2.0, hspf_input)
    assert shortage["operating_case"] == "maximum_shortage"
    assert shortage["auxiliary_heat"] > 0.0
    assert shortage["bin_energy"] == (
        shortage["heat_pump_energy"] + shortage["auxiliary_energy"]
    )


def test_ks_c9306_hspf_intersection_power_formulas(tmp_path):
    calculator = make_phase1_calculator(tmp_path)
    hspf_input = explicit_ks_hspf_curve_fixture()["ks_c_9306_hspf"]
    load_line = (100.0, 500.0)

    min_temp = calculator._ks_hspf_intersection_temp(
        hspf_input, "min", False, load_line
    )
    intermediate_temp = calculator._ks_hspf_intersection_temp(
        hspf_input, "intermediate", False, load_line
    )
    min_power = calculator._ks_hspf_power_curve(
        min_temp, hspf_input, "min", False
    )
    intermediate_power = calculator._ks_hspf_power_curve(
        intermediate_temp, hspf_input, "intermediate", False
    )
    expected_min_mid = calculator._ks_hspf_linear(
        7.0, intermediate_temp, intermediate_power, min_temp, min_power
    )
    actual_min_mid = calculator._ks_hspf_power_by_intersection(
        7.0, hspf_input, "minimum_intermediate", load_line
    )

    rated_temp = calculator._ks_hspf_intersection_temp(
        hspf_input, "rated", False, load_line
    )
    rated_power = calculator._ks_hspf_power_curve(
        rated_temp, hspf_input, "rated", False
    )
    expected_mid_rated = calculator._ks_hspf_linear(
        7.0, rated_temp, rated_power, intermediate_temp, intermediate_power
    )
    actual_mid_rated = calculator._ks_hspf_power_by_intersection(
        7.0, hspf_input, "intermediate_rated", load_line
    )

    failures = []
    assert_close(
        actual_min_mid,
        expected_min_mid,
        ENERGY_TOLERANCE_WH,
        "E.2.37 intersection power",
        failures,
    )
    assert_close(
        actual_mid_rated,
        expected_mid_rated,
        ENERGY_TOLERANCE_WH,
        "E.2.38 intersection power",
        failures,
    )
    assert not failures


def test_ks_c9306_hspf_frost_intersection_power_formulas(tmp_path):
    calculator = make_phase1_calculator(tmp_path)
    hspf_input = explicit_ks_hspf_curve_fixture()["ks_c_9306_hspf"]
    load_line = (-100.0, 3500.0)

    min_temp = calculator._ks_hspf_intersection_temp(
        hspf_input, "min", True, load_line
    )
    intermediate_temp = calculator._ks_hspf_intersection_temp(
        hspf_input, "intermediate", True, load_line
    )
    rated_temp = calculator._ks_hspf_intersection_temp(
        hspf_input, "rated", True, load_line
    )
    max_temp = calculator._ks_hspf_intersection_temp(
        hspf_input, "max", True, load_line
    )

    min_power = calculator._ks_hspf_power_curve(min_temp, hspf_input, "min", True)
    intermediate_power = calculator._ks_hspf_power_curve(
        intermediate_temp, hspf_input, "intermediate", True
    )
    rated_power = calculator._ks_hspf_power_curve(
        rated_temp, hspf_input, "rated", True
    )
    max_power = calculator._ks_hspf_power_curve(max_temp, hspf_input, "max", True)

    expected_min_mid = calculator._ks_hspf_linear(
        0.0, intermediate_temp, intermediate_power, min_temp, min_power
    )
    actual_min_mid = calculator._ks_hspf_power_by_intersection(
        0.0, hspf_input, "minimum_intermediate", load_line
    )

    expected_mid_rated = calculator._ks_hspf_linear(
        0.0, rated_temp, rated_power, intermediate_temp, intermediate_power
    )
    actual_mid_rated = calculator._ks_hspf_power_by_intersection(
        0.0, hspf_input, "intermediate_rated", load_line
    )

    expected_rated_max = calculator._ks_hspf_linear(
        0.0, max_temp, max_power, rated_temp, rated_power
    )
    actual_rated_max = calculator._ks_hspf_power_by_intersection(
        0.0, hspf_input, "rated_maximum", load_line
    )

    failures = []
    assert_close(
        actual_min_mid,
        expected_min_mid,
        ENERGY_TOLERANCE_WH,
        "E.2.39 intersection power",
        failures,
    )
    assert_close(
        actual_mid_rated,
        expected_mid_rated,
        ENERGY_TOLERANCE_WH,
        "E.2.40 intersection power",
        failures,
    )
    assert_close(
        actual_rated_max,
        expected_rated_max,
        ENERGY_TOLERANCE_WH,
        "E.2.36 intersection power",
        failures,
    )
    assert not failures


def test_ks_c9306_hspf_bin_uses_optional_load_line(tmp_path):
    calculator = make_phase1_calculator(tmp_path)
    data = explicit_ks_hspf_curve_fixture()
    data["ks_c_9306_hspf"]["load_line"] = {"slope": 100.0, "intercept": 500.0}
    hspf_input = data["ks_c_9306_hspf"]

    row = calculator._ks_hspf_bin(7.0, 1200.0, 2.0, hspf_input)
    expected_power = calculator._ks_hspf_power_by_intersection(
        7.0, hspf_input, "minimum_intermediate", (100.0, 500.0)
    )

    failures = []
    assert row["operating_case"] == "minimum_intermediate"
    assert row["load_line_used"]
    assert_close(
        row["heat_pump_energy"],
        expected_power * 2.0,
        ENERGY_TOLERANCE_WH,
        "load-line bin energy",
        failures,
    )
    assert not failures


def test_korea_hspf_bin_hours_use_actual_ks_table():
    config_path = Path(__file__).resolve().parents[1] / "data/region_configs/korea.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    hspf_bin_hours = config["hspf_bin_hours"]

    assert len(hspf_bin_hours) == 31
    assert sum(item["nj"] for item in hspf_bin_hours) == 2849
    assert [item["j"] for item in hspf_bin_hours] == list(range(1, 32))
    assert [item["tj"] for item in hspf_bin_hours] == list(range(-15, 16))
    assert all("load" not in item and "heating_load" not in item for item in hspf_bin_hours)


def test_ks_c9306_hspf_bin_load_defaults_to_config_load_line(tmp_path):
    config_path = tmp_path / "iso16358_hspf_load_line.json"
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
            "correction": {
                "capacity_def_over_nof": 1 / 1.12,
                "power_def_over_nof": 1 / 1.06,
                "cd": 0.25,
            },
            "load_line": {
                "source": "rated_heating_capacity",
                "zero_load_temp": 16.0,
                "full_load_temp": -7.0,
                "rated_capacity_factor": 0.82,
            },
            "bin_hours_key": "hspf_bin_hours",
        },
        "hspf_bin_hours": [{"j": 1, "tj": 7, "nj": 1}],
    }
    config_path.write_text(json.dumps(config), encoding="utf-8")
    calculator = ISO16358Calculator(str(config_path))

    result = calculator.calculate_hspf(OFFICIAL_GOLDEN_SAMPLE)
    detail = result["bin_details"][0]

    expected_load = 4300.0 * 0.82 * (16.0 - 7.0) / (16.0 - (-7.0))
    failures = []
    assert_close(
        detail["load"],
        expected_load,
        ENERGY_TOLERANCE_WH,
        "default KS HSPF bin load",
        failures,
    )
    assert result["HSTL"] > 0
    assert not failures
