from core.calculators.standards.ahri_hspf2 import AHRIHSPF2Calculator


def test_hspf2_v2_legacy_smoke_result():
    calc = AHRIHSPF2Calculator("data/region_configs/usa_hspf2.json")
    test_points = {
        "H1_Full": (24000, 2200),
        "H2_Full": (22000, 2100),
        "H3_Full": (18000, 1900),
    }

    result = calc.calculate_hspf2_v2(test_points)

    assert result["HSPF2"] == 9.602
    assert result["total_heating_Btu"] == 11190000.0
    assert result["total_energy_Wh"] == 1165440.047
    assert len(result["bin_details"]) == 15
    assert all(row["q_full"] >= 0 for row in result["bin_details"])
    assert all(row["p_full"] >= 0 for row in result["bin_details"])
    assert all(row["E_j"] >= 0 for row in result["bin_details"])
