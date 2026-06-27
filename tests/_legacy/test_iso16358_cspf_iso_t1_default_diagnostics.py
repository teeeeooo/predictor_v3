import json
from pathlib import Path

from core._legacy.calculator_iso16358_legacy import ISO16358Calculator
from core.calculators.standards.ks_c9306 import KSC9306Calculator


FIXTURE_PATH = (
    Path(__file__).resolve().parents[1]
    / "fixtures/iso16358_cspf_golden_fixtures.json"
)
FIXTURE_ID = "southeast_asia_iso_basic_cspf_4_665"
ASEAN_FIXTURE_ID = "asean_report_table7_variable_speed_cspf_4_76"


def load_fixture():
    data = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    return data["fixtures"][FIXTURE_ID]


def load_fixtures():
    data = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    return data["fixtures"]


def base_config(fixture):
    return {
        "region": "ISO T1 Default 2-Point Diagnostic",
        "standard": "ISO16358-1",
        "t_100_load": 35.0,
        "t_0_load": 20.0,
        "reference_point": "35_full",
        "Cd": 0.25,
        "building_load_source": "measured",
        "points": {
            "35_full": "measure",
            "35_half": "measure",
            "29_full": "default",
            "29_half": "default",
        },
        "derived_rules": {
            "29_full": {
                "source": "35_full",
                "capacity_factor": 1.077,
                "power_factor": 0.914,
            },
            "29_half": {
                "source": "35_half",
                "capacity_factor": 1.077,
                "power_factor": 0.914,
            },
        },
        "bin_hours": fixture["bin_hours"],
    }


def run_cspf(tmp_path, label, config, measured_inputs):
    config_path = tmp_path / f"{label}.json"
    config_path.write_text(json.dumps(config), encoding="utf-8")
    calculator = ISO16358Calculator(str(config_path))
    result = calculator.calculate_cspf(measured_inputs)
    resolved = calculator.resolve_points(
        calculator._prepare_measured_inputs(measured_inputs)
    )
    return {
        "label": label,
        "cspf": result["cspf"],
        "cstl_wh": result["annual_cooling_kwh"] * 1000.0,
        "csec_wh": result["annual_power_kwh"] * 1000.0,
        "points": sorted(resolved),
    }


def config_with_manual_29_points(config, measured_inputs, round_derived=False):
    manual_config = dict(config)
    manual_config["points"] = {
        "35_full": "measure",
        "35_half": "measure",
        "29_full": "measure",
        "29_half": "measure",
    }
    manual_config["derived_rules"] = {}

    manual_inputs = dict(measured_inputs)
    derived = {
        "29_full": {
            "capacity": measured_inputs["35_full"]["capacity"] * 1.077,
            "power": measured_inputs["35_full"]["power"] * 0.914,
        },
        "29_half": {
            "capacity": measured_inputs["35_half"]["capacity"] * 1.077,
            "power": measured_inputs["35_half"]["power"] * 0.914,
        },
    }
    if round_derived:
        derived = {
            key: {
                "capacity": round(value["capacity"]),
                "power": round(value["power"]),
            }
            for key, value in derived.items()
        }
    manual_inputs.update(derived)
    return manual_config, manual_inputs


def test_iso_t1_default_cspf_diagnostic_variants(tmp_path):
    """Diagnostic test only; not a production regression or certification test."""
    fixture = load_fixture()
    measured_inputs = fixture["measured_points"]
    current_config = base_config(fixture)

    results = {}
    results["A_current"] = run_cspf(
        tmp_path, "a_current", current_config, measured_inputs
    )

    cd_zero_config = dict(current_config)
    cd_zero_config["Cd"] = 0.0
    results["B_cd_zero_diagnostic_only"] = run_cspf(
        tmp_path, "b_cd_zero", cd_zero_config, measured_inputs
    )

    for power_factor in (0.914, 0.864):
        pf_config = json.loads(json.dumps(current_config))
        pf_config["derived_rules"]["29_full"]["power_factor"] = power_factor
        pf_config["derived_rules"]["29_half"]["power_factor"] = power_factor
        results[f"C_power_factor_{power_factor}"] = run_cspf(
            tmp_path,
            f"c_power_factor_{str(power_factor).replace('.', '_')}",
            pf_config,
            measured_inputs,
        )

    for t_0_load in (20.0, 21.0, 23.0):
        t0_config = dict(current_config)
        t0_config["t_0_load"] = t_0_load
        results[f"D_t0_{t_0_load}"] = run_cspf(
            tmp_path,
            f"d_t0_{str(t_0_load).replace('.', '_')}",
            t0_config,
            measured_inputs,
        )

    unrounded_config, unrounded_inputs = config_with_manual_29_points(
        current_config, measured_inputs, round_derived=False
    )
    results["E_derived_unrounded_manual"] = run_cspf(
        tmp_path, "e_derived_unrounded_manual", unrounded_config, unrounded_inputs
    )

    rounded_config, rounded_inputs = config_with_manual_29_points(
        current_config, measured_inputs, round_derived=True
    )
    results["E_derived_nearest_integer_manual"] = run_cspf(
        tmp_path, "e_derived_nearest_integer_manual", rounded_config, rounded_inputs
    )

    print(json.dumps(results, indent=2, sort_keys=True))

    assert abs(results["A_current"]["cspf"] - 4.501) <= 0.001
    assert results["B_cd_zero_diagnostic_only"]["cspf"] > results["A_current"]["cspf"]
    for result in results.values():
        assert result["cspf"] > 0
        assert result["cstl_wh"] > 0
        assert result["csec_wh"] > 0


def test_korea_cspf_regression_matches_ks_c9306_calculator():
    calculator = KSC9306Calculator.from_config_path("data/region_configs/korea.json")
    result = calculator.calculate_cspf(
        {
            "35_full": {"capacity": 6035.8, "power": 1641.4},
            "35_half": {"capacity": 3420.4, "power": 679.4},
            "29_min": {"capacity": 1759.6, "power": 201.7},
        },
        declared_capacity=6000,
    )

    assert result["cspf"] == 6.504
    assert result["annual_cooling_kwh"] == 1943.798
    assert result["annual_power_kwh"] == 298.852


def test_iso_t1_default_and_asean_control_mismatch_direction(tmp_path):
    """Diagnostic comparison only; distinguishes fixture-specific vs shared path mismatch."""
    fixtures = load_fixtures()
    sample_ids = [FIXTURE_ID, ASEAN_FIXTURE_ID]
    comparison = {}

    for sample_id in sample_ids:
        fixture = fixtures[sample_id]
        result = run_cspf(
            tmp_path,
            sample_id,
            base_config(fixture),
            fixture["measured_points"],
        )
        expected_cspf = fixture["expected"]["cspf"]
        comparison[sample_id] = {
            "expected_cspf": expected_cspf,
            "actual_cspf": result["cspf"],
            "delta": result["cspf"] - expected_cspf,
        }

    print(json.dumps(comparison, indent=2, sort_keys=True))

    assert comparison[FIXTURE_ID]["delta"] < 0
    assert comparison[ASEAN_FIXTURE_ID]["delta"] < 0
