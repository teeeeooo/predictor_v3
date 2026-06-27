import json
from pathlib import Path

from core.calculators.standards.iso16358 import ISO16358Calculator


FIXTURE_PATH = (
    Path(__file__).resolve().parent
    / "fixtures/iso16358_cspf_golden_fixtures.json"
)

CONTROL_SAMPLE_IDS = [
    "southeast_asia_iso_basic_cspf_4_665",
    "asean_report_table7_variable_speed_cspf_4_76",
    "jatl_slide_variable_capacity_cspf_4_86",
    "jatl_tool_required_test_only_cspf_4_93",
]

JATL_TOOL_ID = "jatl_tool_required_test_only_cspf_4_93"

CAPACITY_FACTOR_29C = 1.077
POWER_FACTOR_29C = 0.914
CD = 0.25
T_0_LOAD = 20.0
T_100_LOAD = 35.0


def load_fixtures():
    data = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    return data["fixtures"]


def xlsm_linear_29_35(value_35, value_29, tj):
    return value_35 + (value_29 - value_35) / (35.0 - 29.0) * (35.0 - tj)


def xlsm_boundary_temperature(load_ref, capacity_35, capacity_29):
    return (
        6.0 * load_ref * T_0_LOAD
        + 6.0 * capacity_35 * (T_100_LOAD - T_0_LOAD)
        + 35.0 * (capacity_29 - capacity_35) * (T_100_LOAD - T_0_LOAD)
    ) / (
        6.0 * load_ref
        + (capacity_29 - capacity_35) * (T_100_LOAD - T_0_LOAD)
    )


def build_official_xlsm_mirror_rows(fixture):
    """Diagnostic only, formula mirror from official xlsm audit.

    Mirrors the T1 Variable Capacity unit block for Required test only /
    Minimum Not Measure path. It is intentionally separate from production
    code so it can expose where the current engine diverges.
    """
    measured = fixture["measured_points"]
    full = measured["35_full"]
    half = measured["35_half"]

    load_ref = full["capacity"]  # CC3 = H9 in the official tool.

    full_cap_35 = full["capacity"]
    full_pow_35 = full["power"]
    full_cap_29 = full_cap_35 * CAPACITY_FACTOR_29C
    full_pow_29 = full_pow_35 * POWER_FACTOR_29C

    half_cap_35 = half["capacity"]
    half_pow_35 = half["power"]
    half_cap_29 = half_cap_35 * CAPACITY_FACTOR_29C
    half_pow_29 = half_pow_35 * POWER_FACTOR_29C

    # Required-test-only / Minimum Not Measure replaces minimum with half.
    min_cap_35 = half_cap_35
    min_pow_35 = half_pow_35
    min_cap_29 = half_cap_29
    min_pow_29 = half_pow_29

    t_full = xlsm_boundary_temperature(load_ref, full_cap_35, full_cap_29)
    t_half = xlsm_boundary_temperature(load_ref, half_cap_35, half_cap_29)
    t_min = xlsm_boundary_temperature(load_ref, min_cap_35, min_cap_29)

    eer_full_boundary = xlsm_linear_29_35(
        full_cap_35, full_cap_29, t_full
    ) / xlsm_linear_29_35(full_pow_35, full_pow_29, t_full)
    eer_half_boundary = xlsm_linear_29_35(
        half_cap_35, half_cap_29, t_half
    ) / xlsm_linear_29_35(half_pow_35, half_pow_29, t_half)
    eer_min_boundary = xlsm_linear_29_35(
        min_cap_35, min_cap_29, t_min
    ) / xlsm_linear_29_35(min_pow_35, min_pow_29, t_min)

    rows = []
    for bin_row in fixture["bin_hours"]:
        tj = float(bin_row["tj"])
        nj = float(bin_row["nj"])
        lc = max(0.0, load_ref * (tj - T_0_LOAD) / (T_100_LOAD - T_0_LOAD))

        phi_full = xlsm_linear_29_35(full_cap_35, full_cap_29, tj)
        phi_half = xlsm_linear_29_35(half_cap_35, half_cap_29, tj)
        phi_min = xlsm_linear_29_35(min_cap_35, min_cap_29, tj)

        p_full = xlsm_linear_29_35(full_pow_35, full_pow_29, tj)
        p_half = xlsm_linear_29_35(half_pow_35, half_pow_29, tj)
        p_min = xlsm_linear_29_35(min_pow_35, min_pow_29, tj)

        x = lc / phi_min if lc < phi_min and phi_min > 0 else 1.0
        fpl = 1.0 - CD * (1.0 - x)

        if phi_min >= lc:
            operating_case = "load_at_or_below_min_replaced_by_half"
            p_tj = 0.0 if fpl == 0 else x * p_min / fpl
        elif phi_min < lc <= phi_half:
            operating_case = "load_between_min_and_half"
            if t_half == t_min:
                p_tj = 0.0
            else:
                eer = eer_min_boundary + (
                    (eer_half_boundary - eer_min_boundary) / (t_half - t_min)
                ) * (tj - t_min)
                p_tj = lc / eer if eer > 0 else 0.0
        elif phi_half < lc <= phi_full:
            operating_case = "load_between_half_and_full"
            eer = eer_half_boundary + (
                (eer_full_boundary - eer_half_boundary) / (t_full - t_half)
            ) * (tj - t_half)
            p_tj = lc / eer if eer > 0 else 0.0
        else:
            operating_case = "load_above_full"
            p_tj = p_full

        cooling_output = min(lc, phi_full)
        rows.append(
            {
                "tj": tj,
                "nj": nj,
                "Lc": lc,
                "phi_full": phi_full,
                "p_full": p_full,
                "phi_half": phi_half,
                "p_half": p_half,
                "phi_min": phi_min,
                "p_min": p_min,
                "X": x,
                "FPL": fpl,
                "operating_case": operating_case,
                "P_tj": p_tj,
                "CSEC_tj": p_tj * nj,
                "CSTL_tj": cooling_output * nj,
            }
        )
    return rows


def build_current_engine_formula_rows(fixture):
    measured = fixture["measured_points"]
    full = measured["35_full"]
    half = measured["35_half"]
    load_ref = full["capacity"]

    full_cap_29 = full["capacity"] * CAPACITY_FACTOR_29C
    full_pow_29 = full["power"] * POWER_FACTOR_29C
    half_cap_29 = half["capacity"] * CAPACITY_FACTOR_29C
    half_pow_29 = half["power"] * POWER_FACTOR_29C

    rows = []
    for bin_row in fixture["bin_hours"]:
        tj = float(bin_row["tj"])
        nj = float(bin_row["nj"])
        lc = load_ref * (tj - T_0_LOAD) / (T_100_LOAD - T_0_LOAD)
        if lc <= 0.0:
            continue

        phi_full = xlsm_linear_29_35(full["capacity"], full_cap_29, tj)
        p_full = xlsm_linear_29_35(full["power"], full_pow_29, tj)
        phi_half = xlsm_linear_29_35(half["capacity"], half_cap_29, tj)
        p_half = xlsm_linear_29_35(half["power"], half_pow_29, tj)

        if lc <= phi_half:
            operating_case = "load_at_or_below_lowest_capacity"
            x = lc / phi_half
            fpl = max(1e-6, 1.0 - CD * (1.0 - x))
            p_tj = x * p_half / fpl
            cooling_output = lc
        elif lc > phi_full:
            operating_case = "load_above_full"
            x = lc / phi_full
            fpl = None
            p_tj = p_full
            cooling_output = phi_full
        else:
            operating_case = "load_between_half_and_full"
            x = lc / phi_half
            fpl = None
            p_tj = p_half + (p_full - p_half) * (lc - phi_half) / (
                phi_full - phi_half
            )
            cooling_output = lc

        rows.append(
            {
                "tj": tj,
                "nj": nj,
                "Lc": lc,
                "phi_full": phi_full,
                "p_full": p_full,
                "phi_half": phi_half,
                "p_half": p_half,
                "X": x,
                "FPL": fpl,
                "operating_case": operating_case,
                "P_tj": p_tj,
                "CSEC_tj": p_tj * nj,
                "CSTL_tj": cooling_output * nj,
            }
        )
    return rows


def summarize_rows(rows):
    cstl = sum(row["CSTL_tj"] for row in rows) / 1000.0
    csec = sum(row["CSEC_tj"] for row in rows) / 1000.0
    return {
        "cstl_kwh": cstl,
        "csec_kwh": csec,
        "cspf": cstl / csec,
    }


def make_engine_config(fixture):
    return {
        "region": "Official XLSM Formula Diagnostic",
        "standard": "ISO16358-1",
        "t_100_load": T_100_LOAD,
        "t_0_load": T_0_LOAD,
        "reference_point": "35_full",
        "Cd": CD,
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
                "capacity_factor": CAPACITY_FACTOR_29C,
                "power_factor": POWER_FACTOR_29C,
            },
            "29_half": {
                "source": "35_half",
                "capacity_factor": CAPACITY_FACTOR_29C,
                "power_factor": POWER_FACTOR_29C,
            },
        },
        "bin_hours": fixture["bin_hours"],
    }


def calculate_current_engine(tmp_path, sample_id, fixture):
    config_path = tmp_path / f"{sample_id}.json"
    config_path.write_text(json.dumps(make_engine_config(fixture)), encoding="utf-8")
    return ISO16358Calculator(str(config_path)).calculate_cspf(
        fixture["measured_points"]
    )


def first_current_vs_official_divergence(current_rows, official_rows):
    for current, official in zip(current_rows, official_rows):
        for field in ("Lc", "phi_half", "p_half", "X", "FPL", "P_tj", "CSEC_tj"):
            current_value = current.get(field)
            official_value = official.get(field)
            if current_value is None and official_value is None:
                continue
            if current_value is None or official_value is None:
                return {
                    "tj": official["tj"],
                    "field": field,
                    "current": current_value,
                    "official": official_value,
                    "current_case": current["operating_case"],
                    "official_case": official["operating_case"],
                }
            if abs(current_value - official_value) > 1e-6:
                return {
                    "tj": official["tj"],
                    "field": field,
                    "current": current_value,
                    "official": official_value,
                    "current_case": current["operating_case"],
                    "official_case": official["operating_case"],
                }
    return None


def first_power_divergence(current_rows, official_rows):
    for current, official in zip(current_rows, official_rows):
        if abs(current["P_tj"] - official["P_tj"]) > 1e-6:
            return {
                "tj": official["tj"],
                "field": "P_tj",
                "current": current["P_tj"],
                "official": official["P_tj"],
                "current_case": current["operating_case"],
                "official_case": official["operating_case"],
            }
    return None


def test_official_xlsm_formula_mirror_reproduces_jatl_tool_sample(tmp_path):
    fixtures = load_fixtures()
    fixture = fixtures[JATL_TOOL_ID]
    official_rows = build_official_xlsm_mirror_rows(fixture)
    current_rows = build_current_engine_formula_rows(fixture)
    official = summarize_rows(official_rows)
    current_engine = calculate_current_engine(tmp_path, JATL_TOOL_ID, fixture)
    divergence = first_current_vs_official_divergence(current_rows, official_rows)
    power_divergence = first_power_divergence(current_rows, official_rows)

    diagnostic = {
        "sample_id": JATL_TOOL_ID,
        "expected": fixture["expected"],
        "official_xlsm_mirror": official,
        "current_engine": current_engine,
        "first_divergence": divergence,
        "first_energy_affecting_divergence": power_divergence,
    }
    print(json.dumps(diagnostic, indent=2, sort_keys=True))

    assert abs(official["cstl_kwh"] - fixture["expected"]["cstl_kwh"]) <= 1.0
    assert abs(official["csec_kwh"] - fixture["expected"]["csec_kwh"]) <= 1.0
    assert abs(official["cspf"] - fixture["expected"]["cspf"]) <= 0.01
    assert divergence is not None
    assert divergence["tj"] == 29.0
    assert power_divergence is not None
    assert power_divergence["tj"] == 29.0
    assert power_divergence["field"] == "P_tj"
    assert power_divergence["current_case"] == "load_between_half_and_full"
    assert power_divergence["official_case"] == "load_between_half_and_full"


def test_official_xlsm_formula_mirror_control_sample_matrix(tmp_path):
    fixtures = load_fixtures()
    results = []

    for sample_id in CONTROL_SAMPLE_IDS:
        fixture = fixtures[sample_id]
        official = summarize_rows(build_official_xlsm_mirror_rows(fixture))
        current_engine = calculate_current_engine(tmp_path, sample_id, fixture)
        expected = fixture["expected"]
        results.append(
            {
                "sample_id": sample_id,
                "expected_cspf": expected["cspf"],
                "official_cspf": official["cspf"],
                "current_cspf": current_engine["cspf"],
                "official_csec_kwh": official["csec_kwh"],
                "current_csec_kwh": current_engine["annual_power_kwh"],
                "official_minus_expected_cspf": official["cspf"]
                - expected["cspf"],
                "official_minus_current_cspf": official["cspf"]
                - current_engine["cspf"],
            }
        )

    print(json.dumps(results, indent=2, sort_keys=True))

    assert all(row["official_cspf"] > row["current_cspf"] for row in results)
    for row in results:
        assert abs(row["official_cspf"] - row["expected_cspf"]) <= 0.01
