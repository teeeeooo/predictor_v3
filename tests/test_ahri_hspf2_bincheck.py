from core.calculators.standards.ahri_hspf2 import AHRIHSPF2Calculator


def canonical_hspf2_points():
    return {
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


def ahri_kwargs():
    return {
        "t_off": -10,
        "t_on": -5,
        "defrost_t_test_minutes": 90,
        "defrost_t_max_minutes": 720,
    }


def test_hspf2_v3_bin_values_are_non_negative():
    calc = AHRIHSPF2Calculator("data/region_configs/usa_hspf2.json")
    result = calc.calculate_hspf2_v3(canonical_hspf2_points(), **ahri_kwargs())

    for row in result["bin_details"]:
        assert row["q_full"] >= 0
        assert row["p_full"] >= 0
        assert row["building_load"] >= 0
        assert row["E_j"] >= 0


def test_hspf2_v3_capacity_shortage_bins_use_case_iii():
    calc = AHRIHSPF2Calculator("data/region_configs/usa_hspf2.json")
    result = calc.calculate_hspf2_v3(canonical_hspf2_points(), **ahri_kwargs())

    capacity_lt_load_rows = [
        row for row in result["bin_details"]
        if row["q_full"] < row["building_load"]
    ]

    assert capacity_lt_load_rows
    assert all(row["operating_case"] == "Case III" for row in capacity_lt_load_rows)
