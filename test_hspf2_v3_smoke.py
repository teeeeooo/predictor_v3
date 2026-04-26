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


calc = AHRIHSPF2Calculator("data/usa_hspf2.json")

legacy_points = {
    "H1_Full": (24000, 2200),
    "H2_Full": (22000, 2100),
    "H3_Full": (18000, 1900),
}

canonical_with_h42 = {
    "H12": (24000, 2200),
    "H32": (22000, 2100),
    "H42": (18000, 1900),
}

canonical_without_h42 = {
    "H12": (24000, 2200),
    "H32": (22000, 2100),
}

v2 = calc.calculate_hspf2_v2(legacy_points)
v3_with_h42 = calc.calculate_hspf2_v3(canonical_with_h42)
v3_without_h42 = calc.calculate_hspf2_v3(canonical_without_h42)

v2_raw = v2["total_heating_Btu"] / v2["total_energy_Wh"]
assert v2["HSPF2"] == round(v3_with_h42["raw_hspf2"], 3)
assert v2["total_heating_Btu"] == v3_with_h42["total_load"]
assert v2["total_energy_Wh"] == v3_with_h42["total_energy"]
assert v3_with_h42["h42_source"] == "provided"
assert v3_without_h42["h42_source"] == "extrapolated"

print_comparison("H42 provided: v2 vs v3", v2, v3_with_h42)
print()
print("H42 omitted: v3 extrapolation")
print("  v3 raw_hspf2:", round(v3_without_h42["raw_hspf2"], 6))
print("  v3 rounded_hspf2:", v3_without_h42["rounded_hspf2"])
print("  v3 total_load:", v3_without_h42["total_load"])
print("  v3 total_energy:", v3_without_h42["total_energy"])
print("  v3 H42 source:", v3_without_h42["h42_source"])
