import json

from core.calculator_iso16358 import ISO16358Calculator


TOLERANCE = 1e-9


def assert_close(actual, expected, label):
    assert abs(actual - expected) < TOLERANCE, (
        f"{label} mismatch: expected={expected}, actual={actual}"
    )


def make_calculator(tmp_path):
    config_path = tmp_path / "iso16358_hspf_phase1.json"
    config = {
        "mode": "heating",
        "heating_test_temperatures": {
            "H1": 7.0,
            "H2": 2.0,
            "H3": -7.0
        },
        "bin_hours": [
            {"tj": 4.5, "nj": 2.0, "load": 5000.0},
            {"tj": -10.0, "nj": 1.0, "load": 3000.0}
        ]
    }
    config_path.write_text(json.dumps(config), encoding="utf-8")
    return ISO16358Calculator(str(config_path))


def hspf_points():
    return {
        "H1": {"capacity": 5000.0, "power": 1000.0},
        "H2": {"capacity": 4000.0, "power": 900.0},
        "H3": {"capacity": 2500.0, "power": 800.0}
    }


def variable_hspf_points():
    return {
        "H3_full": {"temp": -7.0, "capacity": 3000.0, "power": 800.0},
        "H2_full": {"temp": 2.0, "capacity": 4000.0, "power": 900.0},
        "H1_full": {"temp": 7.0, "capacity": 4500.0, "power": 1000.0},
        "H1_half": {"temp": 7.0, "capacity": 2500.0, "power": 600.0},
        "H1_min": {"temp": 7.0, "capacity": 1200.0, "power": 300.0},
    }


def test_hspf_phase1_auxiliary_heat_and_seasonal_totals(tmp_path):
    calculator = make_calculator(tmp_path)

    auxiliary = calculator.calc_auxiliary_heat(
        load=5000.0,
        available_capacity=4200.0,
        hours=3.0,
        aux_cop=2.0
    )
    assert_close(auxiliary["auxiliary_heat"], 800.0, "auxiliary_heat")
    assert_close(auxiliary["auxiliary_energy"], 1200.0, "auxiliary_energy")

    result = calculator.calculate_hspf(hspf_points(), aux_cop=2.0)
    first_bin = result["bin_details"][0]

    assert_close(first_bin["auxiliary_heat"], 500.0, "bin auxiliary_heat")
    assert_close(first_bin["auxiliary_energy"], 500.0, "bin auxiliary_energy")

    expected_hstl = sum(item["bin_load"] for item in result["bin_details"])
    expected_hsec = sum(item["bin_energy"] for item in result["bin_details"])
    assert_close(result["HSTL"], expected_hstl, "HSTL")
    assert_close(result["HSEC"], expected_hsec, "HSEC")
    assert_close(result["HSPF"], expected_hstl / expected_hsec, "HSPF")


def test_hspf_h1_h2_h3_interpolation_and_low_temp_extrapolation(tmp_path):
    calculator = make_calculator(tmp_path)

    interpolated = calculator.interpolate_heating(4.5, hspf_points())
    assert_close(interpolated["capacity"], 4500.0, "H1/H2 capacity interpolation")
    assert_close(interpolated["power"], 950.0, "H1/H2 power interpolation")

    extrapolated = calculator.interpolate_heating(-10.0, hspf_points())
    assert_close(extrapolated["capacity"], 2000.0, "below H3 capacity extrapolation")
    assert_close(extrapolated["power"], 2300.0 / 3.0, "below H3 power extrapolation")


def test_variable_hspf_auxiliary_energy_uses_aux_cop(tmp_path):
    calculator = make_calculator(tmp_path)

    result_cop_1 = calculator.calculate_hspf(variable_hspf_points(), aux_cop=1.0)
    result_cop_2 = calculator.calculate_hspf(variable_hspf_points(), aux_cop=2.0)
    first_bin_cop_1 = result_cop_1["bin_details"][0]
    first_bin_cop_2 = result_cop_2["bin_details"][0]

    assert first_bin_cop_1["operating_case"] == "shortage"
    assert_close(first_bin_cop_1["auxiliary_heat"], 750.0, "auxiliary heat COP 1")
    assert_close(first_bin_cop_1["auxiliary_energy"], 1500.0, "auxiliary energy COP 1")
    assert_close(first_bin_cop_2["auxiliary_energy"], 750.0, "auxiliary energy COP 2")
    assert_close(
        first_bin_cop_1["heat_pump_energy"],
        first_bin_cop_2["heat_pump_energy"],
        "heat pump energy independent of aux COP",
    )
    assert_close(
        result_cop_1["heat_pump_energy"],
        result_cop_2["heat_pump_energy"],
        "seasonal heat pump energy independent of aux COP",
    )

    expected_hsec_delta = result_cop_1["auxiliary_energy"] - result_cop_2["auxiliary_energy"]
    actual_hsec_delta = result_cop_1["HSEC"] - result_cop_2["HSEC"]
    assert_close(actual_hsec_delta, expected_hsec_delta, "HSEC aux COP delta")
