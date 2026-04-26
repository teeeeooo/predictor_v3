import math

from core.calculator_ahri_hspf2 import AHRIHSPF2Calculator


def assert_case_conservation(result):
    for row in result["bin_details"]:
        bin_no = row["bin"]
        operating_case = row["operating_case"]
        q_delivered = row["q_j"]
        q_comp = row["q_comp"]
        q_aux = row["q_aux"]
        e_total = row["E_j"]
        e_aux = row["e_aux"]
        e_comp = row["e_comp"]
        expected_load = row["building_load"] * row["hours"]

        assert math.isclose(q_delivered, q_comp + q_aux, abs_tol=0.05), (
            f"bin {bin_no} heat conservation mismatch: "
            f"q_j={q_delivered}, q_comp={q_comp}, q_aux={q_aux}"
        )
        assert math.isclose(e_total, e_comp + e_aux, abs_tol=0.05), (
            f"bin {bin_no} energy conservation mismatch: "
            f"E_j={e_total}, e_comp={e_comp}, e_aux={e_aux}"
        )
        assert math.isclose(q_delivered, expected_load, abs_tol=0.05), (
            f"bin {bin_no} load mismatch: "
            f"q_j={q_delivered}, building_load*hours={expected_load}"
        )

        if operating_case in ("Case I", "Case II", "Case S"):
            assert q_aux == 0.0, f"bin {bin_no} {operating_case}: q_aux must be 0"
            assert e_aux == 0.0, f"bin {bin_no} {operating_case}: e_aux must be 0"
            assert math.isclose(q_comp, q_delivered, abs_tol=0.05), (
                f"bin {bin_no} {operating_case}: q_comp must equal q_j"
            )
        elif operating_case == "Case III":
            expected_q_comp = row["q_full"] * row["hours"]
            assert math.isclose(q_comp, expected_q_comp, abs_tol=1.0), (
                f"bin {bin_no} Case III: q_comp={q_comp}, q_full*hours={expected_q_comp}"
            )
            assert q_aux > 0, f"bin {bin_no} Case III: q_aux must be > 0"
            assert e_aux > 0, f"bin {bin_no} Case III: e_aux must be > 0"


calc = AHRIHSPF2Calculator("data/usa_hspf2.json")

canonical_with_h42 = {
    "H12": (24000, 2200),
    "H32": (22000, 2100),
    "H42": (18000, 1900),
}

canonical_without_h42 = {
    "H12": (24000, 2200),
    "H32": (22000, 2100),
}

canonical_with_low = {
    "H12": (24000, 2200),
    "H32": (22000, 2100),
    "H42": (18000, 1900),
    "H11": (12000, 1000),
    "H21": (10000, 900),
    "H31": (8000, 800),
}

no_low_with_h42 = calc.calculate_hspf2_v3(canonical_with_h42)
no_low_without_h42 = calc.calculate_hspf2_v3(canonical_without_h42)
low_result = calc.calculate_hspf2_v3(canonical_with_low)

assert round(no_low_with_h42["raw_hspf2"], 6) == 9.211381
assert round(no_low_without_h42["raw_hspf2"], 6) == 9.511685
assert_case_conservation(no_low_with_h42)
assert_case_conservation(low_result)

frost_rows = [row for row in no_low_with_h42["bin_details"] if 17 < row["temp_F"] < 45]
assert frost_rows
for row in no_low_with_h42["bin_details"]:
    assert row["defrost_model"] == "default_linear_placeholder"
    assert row["f_def"] == 1.03
    assert row["defrost_control_type"] == "demand"
    assert row["defrost_t_test_minutes"] == 90
    assert row["defrost_t_max_minutes"] == 720
    expected_q_full_adj = round(row["q_full_raw"] * row["f_frost_capacity"] * row["f_def"], 2)
    assert math.isclose(row["q_full_adj"], expected_q_full_adj, abs_tol=0.02)
    if 17 < row["temp_F"] < 45:
        assert row["is_frost_region"] is True
        assert row["f_frost_capacity"] < 1.0
    else:
        assert row["f_frost_capacity"] == 1.0

operating_cases = {row["operating_case"] for row in low_result["bin_details"]}
assert "Case I" in operating_cases
assert "Case II" in operating_cases
assert "Case III" in operating_cases

print("No-low baseline check")
print("  H42 provided raw_hspf2:", round(no_low_with_h42["raw_hspf2"], 6))
print("  H42 omitted raw_hspf2:", round(no_low_without_h42["raw_hspf2"], 6))
print()
print("Low-speed case activation")
for case_name in ("Case I", "Case II", "Case S", "Case III"):
    bins = [
        row["bin"] for row in low_result["bin_details"]
        if row["operating_case"] == case_name
    ]
    print(f"  {case_name}: {bins}")
print("  raw_hspf2:", round(low_result["raw_hspf2"], 6))
print("  rounded_hspf2:", low_result["rounded_hspf2"])
