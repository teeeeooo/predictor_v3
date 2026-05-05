from core.calculator_ahri_hspf2 import AHRIHSPF2Calculator


def row_at_temp(result, temp_f):
    return next(row for row in result["bin_details"] if row["temp_F"] == temp_f)


def test_hspf2_v3_smoke_and_legacy_delta():
    calc = AHRIHSPF2Calculator("data/region_configs/usa_hspf2.json")
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
    canonical_h4_full_anchor_mock = {
        "H12": (24000, 2200),
        "H22": (23200, 2160),
        "H32": (22000, 2100),
    }
    q_h4full = 18000
    q_h3full = canonical_h4_full_anchor_mock["H32"][0]
    kwargs = {
        "t_off": -10,
        "t_on": -5,
        "defrost_t_test_minutes": 90,
        "defrost_t_max_minutes": 720,
    }

    v2 = calc.calculate_hspf2_v2(legacy_points)
    v3_with_h42 = calc.calculate_hspf2_v3(canonical_with_h42, **kwargs)
    v3_without_h42 = calc.calculate_hspf2_v3(canonical_without_h42, **kwargs)
    q_low_42, p_low_42 = calc._canonical_low_capacity_power_at_temp(
        42,
        canonical_low_speed_mock,
    )
    q_full_at_5, _ = calc._cert_full_capacity_power_at_temp(
        5,
        canonical_h4_full_anchor_mock,
        canonical_h4_full_anchor_mock["H12"],
        (q_h4full, 1900),
    )
    q_full_at_17, _ = calc._cert_full_capacity_power_at_temp(
        17,
        canonical_h4_full_anchor_mock,
        canonical_h4_full_anchor_mock["H12"],
        (q_h4full, 1900),
    )

    v2_raw = v2["total_heating_Btu"] / v2["total_energy_Wh"]
    assert v2["HSPF2"] == 9.602
    assert round(v2_raw, 6) != round(v3_with_h42["raw_hspf2"], 6)
    assert v3_with_h42["h42_source"] == "provided"
    assert v3_without_h42["h42_source"] == "not_provided"
    assert v3_with_h42["summary"]["metadata"]["h12_source"] == "tested"
    assert v3_without_h42["summary"]["metadata"]["h12_source"] == "tested"
    assert v3_with_h42["summary"]["metadata"]["h22_source"] == "tested"
    assert v3_without_h42["summary"]["metadata"]["h22_source"] == "tested"
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
    assert abs(q_full_at_5 - q_h4full) < 1e-6
    assert abs(q_full_at_17 - q_h3full) < 1e-6
    with_h42_low_row = row_at_temp(v3_with_h42, 7)
    without_h42_low_row = row_at_temp(v3_without_h42, 7)
    assert with_h42_low_row["debug_info"]["full_capacity_method"] == "h4full_low_temp_line"
    assert (
        without_h42_low_row["debug_info"]["full_capacity_method"]
        == "no_h4full_h1full_h3full_line"
    )
    assert with_h42_low_row["q_full"] != without_h42_low_row["q_full"]
    assert with_h42_low_row["p_full"] != without_h42_low_row["p_full"]
    assert v3_with_h42["raw_hspf2"] < 9.937483
    assert v3_without_h42["raw_hspf2"] < 10.292969
