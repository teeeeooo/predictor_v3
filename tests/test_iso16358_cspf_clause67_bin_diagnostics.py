import json
from pathlib import Path

from core.calculator_iso16358 import ISO16358Calculator


FIXTURE_PATH = (
    Path(__file__).resolve().parent
    / "fixtures/iso16358_cspf_golden_fixtures.json"
)
FIXTURE_ID = "asean_report_table7_variable_speed_cspf_4_76"


def load_fixture():
    data = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    return data["fixtures"][FIXTURE_ID]


def make_config(fixture):
    return {
        "region": "ASEAN Report Table 7 Clause 6.7 Bin Diagnostic",
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


def write_calculator(tmp_path, fixture):
    config_path = tmp_path / "asean_clause67_bin_diagnostic.json"
    config_path.write_text(json.dumps(make_config(fixture)), encoding="utf-8")
    return ISO16358Calculator(str(config_path))


def resolve_points(measured_inputs):
    return {
        "35_full": dict(measured_inputs["35_full"]),
        "35_half": dict(measured_inputs["35_half"]),
        "29_full": {
            "capacity": measured_inputs["35_full"]["capacity"] * 1.077,
            "power": measured_inputs["35_full"]["power"] * 0.914,
        },
        "29_half": {
            "capacity": measured_inputs["35_half"]["capacity"] * 1.077,
            "power": measured_inputs["35_half"]["power"] * 0.914,
        },
    }


def split_point_key(point_key):
    temp, load_type = point_key.split("_", 1)
    return float(temp), load_type


def linear(tj, t1, v1, t2, v2):
    if t1 == t2:
        return v1
    return v1 + (v2 - v1) * (tj - t1) / (t2 - t1)


def interpolate_at_tj(tj, resolved):
    grouped = {}
    for point_key, data in resolved.items():
        temp, load_type = split_point_key(point_key)
        grouped.setdefault(load_type, []).append((temp, data["capacity"], data["power"]))

    interpolated = {}
    for load_type, points in grouped.items():
        points.sort(key=lambda item: item[0])
        lower = points[0]
        upper = points[-1]
        for index in range(len(points) - 1):
            left = points[index]
            right = points[index + 1]
            if left[0] <= tj <= right[0]:
                lower = left
                upper = right
                break
            if tj < points[0][0]:
                lower = points[0]
                upper = points[1]
                break
            if tj > points[-1][0]:
                lower = points[-2]
                upper = points[-1]
                break
        interpolated[load_type] = {
            "capacity": linear(tj, lower[0], lower[1], upper[0], upper[1]),
            "power": linear(tj, lower[0], lower[2], upper[0], upper[2]),
        }
    return interpolated


def build_bin_table(fixture):
    resolved = resolve_points(fixture["measured_points"])
    l_c_ref = resolved["35_full"]["capacity"]
    t_0_load = 20.0
    t_100_load = 35.0
    cd = 0.25
    rows = []

    for bin_row in fixture["bin_hours"]:
        tj = float(bin_row["tj"])
        nj = float(bin_row["nj"])
        if nj <= 0:
            continue

        lc = l_c_ref * (tj - t_0_load) / (t_100_load - t_0_load)
        if lc <= 0:
            continue

        interp = interpolate_at_tj(tj, resolved)
        phi_full = interp["full"]["capacity"]
        p_full = interp["full"]["power"]
        phi_half = interp["half"]["capacity"]
        p_half = interp["half"]["power"]

        loads = [
            (data["capacity"], data["power"], load_type)
            for load_type, data in interp.items()
        ]
        loads.sort(key=lambda item: item[0])
        lowest_cap, lowest_pow, _ = loads[0]
        highest_cap, highest_pow, _ = loads[-1]

        cooling_output = lc
        if lc <= lowest_cap:
            operating_case = "load_below_half_capacity"
            x = lc / lowest_cap
            plf = max(1e-6, 1.0 - cd * (1.0 - x))
            p_tj = (x * lowest_pow) / plf
        elif lc > highest_cap:
            operating_case = "load_above_full_capacity"
            x = lc / phi_full
            plf = None
            cooling_output = highest_cap
            p_tj = highest_pow
        else:
            operating_case = "load_between_half_and_full"
            x = lc / phi_half
            plf = None
            p_tj = p_half + (p_full - p_half) * (lc - phi_half) / (
                phi_full - phi_half
            )

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
                "PLF": plf,
                "operating_case": operating_case,
                "P_tj": p_tj,
                "CSEC_tj": p_tj * nj,
                "CSTL_tj": cooling_output * nj,
            }
        )

    return rows


def summarize_rows(rows):
    total_csec = sum(row["CSEC_tj"] for row in rows)
    groups = {
        "21-23 very_low_load": lambda row: 21 <= row["tj"] <= 23,
        "24-27 load_below_half": lambda row: 24 <= row["tj"] <= 27,
        "28 half_boundary": lambda row: row["tj"] == 28,
        "29-35 load_between_half_and_full": lambda row: 29 <= row["tj"] <= 35,
    }
    summary = {}
    for label, predicate in groups.items():
        selected = [row for row in rows if predicate(row)]
        csec = sum(row["CSEC_tj"] for row in selected)
        summary[label] = {
            "hours": sum(row["nj"] for row in selected),
            "cstl_kwh": sum(row["CSTL_tj"] for row in selected) / 1000.0,
            "csec_kwh": csec / 1000.0,
            "csec_share": csec / total_csec,
            "cases": sorted({row["operating_case"] for row in selected}),
        }
    return summary


def test_asean_table7_clause67_current_engine_bin_diagnostics(tmp_path):
    """Diagnostic worksheet only; this does not assert certification correctness."""
    fixture = load_fixture()
    rows = build_bin_table(fixture)
    calculator = write_calculator(tmp_path, fixture)
    result = calculator.calculate_cspf(fixture["measured_points"])

    total_cstl_kwh = sum(row["CSTL_tj"] for row in rows) / 1000.0
    total_csec_kwh = sum(row["CSEC_tj"] for row in rows) / 1000.0
    expected_energy_kwh = fixture["expected"]["annual_energy_consumption_kwh"]
    csec_overage_kwh = total_csec_kwh - expected_energy_kwh
    low_load_csec_kwh = sum(
        row["CSEC_tj"]
        for row in rows
        if row["operating_case"] == "load_below_half_capacity"
    ) / 1000.0

    diagnostic = {
        "totals": {
            "current_cstl_kwh": total_cstl_kwh,
            "current_csec_kwh": total_csec_kwh,
            "current_cspf": total_cstl_kwh / total_csec_kwh,
            "expected_csec_kwh": expected_energy_kwh,
            "csec_overage_kwh": csec_overage_kwh,
            "low_load_csec_kwh": low_load_csec_kwh,
            "low_load_csec_share": low_load_csec_kwh / total_csec_kwh,
        },
        "range_summary": summarize_rows(rows),
        "bin_rows": rows,
    }
    print(json.dumps(diagnostic, indent=2, sort_keys=True))

    assert abs(result["annual_cooling_kwh"] - 2639.280) <= 0.001
    assert abs(result["annual_power_kwh"] - 565.355) <= 0.001
    assert abs(total_cstl_kwh - 2639.280) <= 0.001
    assert abs(total_csec_kwh - 565.355) <= 0.001
    assert abs(csec_overage_kwh - 10.355) <= 0.001
    assert low_load_csec_kwh > 0
    for row in rows:
        assert row["P_tj"] > 0
        assert row["CSEC_tj"] > 0
