import json

from core.calculators.standards.ks_c9306 import KSC9306Calculator


# KS C 9306 HSPF official calculator total oracle.
# The full-bin KS load line uses rated_cooling_capacity=3600.0, not the
# sample's rated_heating_capacity=4300.0.
GOLDEN_EXPECTED = {
    "hspf": 3.689,
    "hstl": 6651225.0,
    "hsec": 1802769.7,
    "heat_pump_energy": 1785292.6,
    "auxiliary_energy": 17477.1,
}

KS_C9306_GOLDEN_BIN_EXPECTED = {
    "heat_pump_energy_wh_by_tj": {
        -15: 3672.7,
        -14: 5468.0,
        -13: 9045.0,
        -12: 10772.0,
        -11: 10690.0,
        -10: 15912.0,
        -9: 24560.7,
        -8: 36554.0,
        -7: 51810.0,
        -6: 63914.1,
        -5: 81230.8,
        -4: 97575.2,
        -3: 103028.9,
        -2: 119477.2,
        -1: 127630.9,
        0: 266658.2,
        1: 136041.9,
        2: 122255.6,
        3: 106972.0,
        4: 93336.9,
        5: 79827.2,
        6: 59895.5,
        7: 41132.5,
        8: 34267.6,
        9: 27577.5,
        10: 20680.9,
        11: 14642.0,
        12: 10079.5,
        13: 6062.6,
        14: 3208.4,
        15: 1312.9,
    },
    "auxiliary_energy_wh_by_tj": {
        -15: 2024.8,
        -14: 2579.3,
        -13: 3535.8,
        -12: 3327.3,
        -11: 2411.7,
        -10: 2244.0,
        -9: 1354.1,
        -8: 0.0,
        -7: 0.0,
        -6: 0.0,
        -5: 0.0,
        -4: 0.0,
        -3: 0.0,
        -2: 0.0,
        -1: 0.0,
        0: 0.0,
        1: 0.0,
        2: 0.0,
        3: 0.0,
        4: 0.0,
        5: 0.0,
        6: 0.0,
        7: 0.0,
        8: 0.0,
        9: 0.0,
        10: 0.0,
        11: 0.0,
        12: 0.0,
        13: 0.0,
        14: 0.0,
        15: 0.0,
    },
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


def adapt_official_golden_for_phase1_engine():
    points = OFFICIAL_GOLDEN_SAMPLE["measured_points"]
    return {
        "H1_full": points["7_full"],
        "H1_half": points["7_half"],
        "H1_min": points["7_min"],
        "H2_full": points["2_defrost"],
        "H3_full": points["-7_max"],
    }


def make_phase1_config_path(tmp_path, ks_profile=True):
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
            },
        ],
    }
    if ks_profile:
        config["hspf"] = hspf_config
    config_path.write_text(json.dumps(config), encoding="utf-8")
    return config_path


def make_ks_phase1_calculator(tmp_path):
    config_path = make_phase1_config_path(tmp_path, ks_profile=True)
    return KSC9306Calculator.from_config_path(str(config_path))
