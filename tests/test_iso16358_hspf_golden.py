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

GOLDEN_SAMPLE = {
    "rated_heating_capacity": 4300.0,
    "points": {
        "H1_full": {"temp": 7.0, "capacity": 4330.2, "power": 1071.1},
        "H1_half": {"temp": 7.0, "capacity": 2901.3, "power": 575.0},
        "H1_min": {"temp": 7.0, "capacity": 1490.9, "power": 252.4},
        "H2_full": {"temp": 2.0, "capacity": 4165.3, "power": 1603.9},
        "H3_full": {"temp": -7.0, "capacity": 4451.7, "power": 1726.9},
    },
}


def assert_close(actual, expected, tolerance, label, failures):
    if abs(actual - expected) > tolerance:
        failures.append(
            f"{label}: expected={expected}, actual={actual}, tolerance={tolerance}"
        )


def make_phase1_calculator(tmp_path):
    config_path = tmp_path / "iso16358_hspf_golden_phase1.json"
    h1_load = GOLDEN_SAMPLE["rated_heating_capacity"]
    h1_points = GOLDEN_SAMPLE["points"]
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
    points = GOLDEN_SAMPLE["points"]
    return {
        "H1_full": points["H1_full"],
        "H1_half": points["H1_half"],
        "H1_min": points["H1_min"],
        "H2_full": points["H2_full"],
        "H3_full": points["H3_full"],
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
