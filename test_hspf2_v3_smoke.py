from core.calculator_ahri_hspf2 import AHRIHSPF2Calculator


def print_comparison(label, v2_result, v3_result):
    v2_raw = v2_result["total_heating_Btu"] / v2_result["total_energy_Wh"]
    print(label)
    print("  v2 HSPF2:", v2_result["HSPF2"])
    print("  v2 raw:", round(v2_raw, 6))
    print("  v3 raw_hspf2:", round(v3_result["raw_hspf2"], 6))
    print("  v3 rounded_hspf2:", v3_result["rounded_hspf2"])
    print("  v3 total_load:", v3_result["total_load"])
    print("  v3 total_energy:", v3_result["total_energy"])
    print("  v3 H42 source:", v3_result["h42_source"])
    print("  v3 bin region:", v3_result["bin_table"]["region"])
    print("  v3 bin hour sum:", v3_result["bin_table"]["fractional_bin_hours_sum"])


calc = AHRIHSPF2Calculator("data/usa_hspf2.json")

legacy_points = {
    "H1_Full": (24000, 2200),
    "H2_Full": (22000, 2100),
    "H3_Full": (18000, 1900),
}

canonical_with_h42 = {
    "H01": (12500, 980),
    "H11": (12000, 1000),
    "H12": (24000, 2200),
    "H1N": (22000, 2000),
    "H22": (23200, 2160),
    "H2Int": (13000, 1200),
    "H32": (22000, 2100),
    "H42": (18000, 1900),
    "A_Full": (24000, 2500),
}

canonical_without_h42 = {
    "H01": (12500, 980),
    "H11": (12000, 1000),
    "H12": (24000, 2200),
    "H1N": (22000, 2000),
    "H22": (23200, 2160),
    "H2Int": (13000, 1200),
    "H32": (22000, 2100),
    "A_Full": (24000, 2500),
}

canonical_low_speed_mock = {
    "H01": (12500, 980),
    "H11": (12000, 1000),
    "H2V": (10000, 900),
    "H31": (8000, 800),
}

# test fixture - not real test data
canonical_h4_full_anchor_mock = {
    "H12": (24000, 2200),
    "H22": (23200, 2160),
    "H32": (22000, 2100),
}
q_H4Full = 18000
q_H3Full = canonical_h4_full_anchor_mock["H32"][0]

kwargs = {
    "t_off": -10,
    "t_on": -5,
    "defrost_t_test_minutes": 90,
    "defrost_t_max_minutes": 720,
}

v2 = calc.calculate_hspf2_v2(legacy_points)
v3_with_h42 = calc.calculate_hspf2_v3(canonical_with_h42, **kwargs)
v3_without_h42 = calc.calculate_hspf2_v3(canonical_without_h42, **kwargs)
q_low_42, p_low_42 = calc._canonical_low_capacity_power_at_temp(42, canonical_low_speed_mock)
q_full_at_5, _ = calc._cert_full_capacity_power_at_temp(
    5,
    canonical_h4_full_anchor_mock,
    canonical_h4_full_anchor_mock["H12"],
    (q_H4Full, 1900),
)
q_full_at_17, _ = calc._cert_full_capacity_power_at_temp(
    17,
    canonical_h4_full_anchor_mock,
    canonical_h4_full_anchor_mock["H12"],
    (q_H4Full, 1900),
)

v2_raw = v2["total_heating_Btu"] / v2["total_energy_Wh"]
assert v2["HSPF2"] == 9.602
assert round(v2_raw, 6) != round(v3_with_h42["raw_hspf2"], 6)
assert v3_with_h42["h42_source"] == "provided"
assert v3_without_h42["h42_source"] == "not_provided"
assert v3_with_h42["bin_table"]["region"] == "IV"
assert v3_with_h42["bin_table"]["fractional_bin_hours_sum"] == 0.757
assert len(v3_with_h42["bin_details"]) == 13
assert v3_with_h42["HSPF2"] == v3_with_h42["rounded_hspf2"]
assert v3_with_h42["total_heating_btu"] == v3_with_h42["total_load"]
assert v3_with_h42["total_energy_wh"] == v3_with_h42["total_energy"]
assert v3_without_h42["HSPF2"] == v3_without_h42["rounded_hspf2"]
assert v3_without_h42["total_heating_btu"] == v3_without_h42["total_load"]
assert v3_without_h42["total_energy_wh"] == v3_without_h42["total_energy"]
assert round(q_low_42, 3) == 11166.667
assert round(p_low_42, 3) == 958.333
assert abs(q_full_at_5 - q_H4Full) < 1e-6, \
    "Eq.11.215: tj=5 기준점 불일치 (H4Full anchor)"
assert abs(q_full_at_17 - q_H3Full) < 1e-6, \
    "Eq.11.215: tj=17 기준점 불일치 (H3Full anchor)"

print_comparison("H42 provided: v2 vs v3", v2, v3_with_h42)
print()
print("H42 omitted: v3 extrapolation")
print("  v3 raw_hspf2:", round(v3_without_h42["raw_hspf2"], 6))
print("  v3 rounded_hspf2:", v3_without_h42["rounded_hspf2"])
print("  v3 total_load:", v3_without_h42["total_load"])
print("  v3 total_energy:", v3_without_h42["total_energy"])
print("  v3 H42 source:", v3_without_h42["h42_source"])
print("  v3 bin region:", v3_without_h42["bin_table"]["region"])
print("  v3 bin hour sum:", v3_without_h42["bin_table"]["fractional_bin_hours_sum"])

# PLF 적용 전 기준값 (P1-3 수정 전 마지막 확인값)
PRE_PLF_RAW_HSPF2_WITH_H42    = 9.937483
PRE_PLF_RAW_HSPF2_WITHOUT_H42 = 10.292969

print()
print("PLF 보정 전후 비교")
decreased_with    = v3_with_h42["raw_hspf2"]    < PRE_PLF_RAW_HSPF2_WITH_H42
decreased_without = v3_without_h42["raw_hspf2"] < PRE_PLF_RAW_HSPF2_WITHOUT_H42
print(f"  H42 있음 raw_hspf2: {round(v3_with_h42['raw_hspf2'], 6)}")
print(f"  PLF 적용 전 대비 감소 여부: {'yes' if decreased_with else 'no'}")
print(f"  H42 없음 raw_hspf2: {round(v3_without_h42['raw_hspf2'], 6)}")
print(f"  PLF 적용 전 대비 감소 여부: {'yes' if decreased_without else 'no'}")
