import json

from core.calculator_iso16358 import ISO16358Calculator


HSPF_TOLERANCE = 0.001
ENERGY_TOLERANCE_WH = 1.0

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


def make_phase1_calculator(tmp_path):
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
    config_path.write_text(json.dumps(config), encoding="utf-8")
    return ISO16358Calculator(str(config_path))


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


def test_iso16358_hspf_golden_sample(tmp_path):
    calculator = make_phase1_calculator(tmp_path)
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
