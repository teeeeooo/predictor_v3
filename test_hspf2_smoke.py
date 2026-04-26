from core.calculator_ahri_hspf2 import AHRIHSPF2Calculator

calc = AHRIHSPF2Calculator("data/usa_hspf2.json")

test_points = {
    "H1_Full": (24000, 2200),
    "H2_Full": (22000, 2100),
    "H3_Full": (18000, 1900),
}

result = calc.calculate_hspf2(test_points)

print("HSPF2:", result["HSPF2"])
print("Total Load:", result["total_heating_Btu"])
print("Total Energy:", result["total_energy_Wh"])

for row in result["bin_details"]:
    print(row)
