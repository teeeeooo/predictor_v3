import math

from core.calculators.standards.ahri_hspf2 import AHRIHSPF2Calculator


def case_ii_rows(result):
    return [row for row in result["bin_details"] if row["operating_case"] == "Case II"]


def row_at_temp(result, temp_f):
    return next(row for row in result["bin_details"] if row["temp_F"] == temp_f)


def test_hspf2_v3_h2int_power_changes_intermediate_path_only():
    calc = AHRIHSPF2Calculator("data/region_configs/usa_hspf2.json")

    base_points = {
        "H01": (12500, 980),
        "H12": (24000, 2200),
        "H1N": (22000, 2000),
        "H11": (12000, 1000),
        "H22": (23200, 2160),
        "H2Int": (13000, 1200),
        "H32": (22000, 2100),
        "H42": (18000, 1900),
        "A_Full": (24000, 2500),
    }
    h2int_power_changed = dict(base_points)
    h2int_power_changed["H2Int"] = (13000, 1400)
    full_changed = dict(base_points)
    full_changed["H22"] = (24400, 2260)
    full_changed["H32"] = (23200, 2200)
    kwargs = {
        "t_off": -10,
        "t_on": -5,
        "defrost_t_test_minutes": 90,
        "defrost_t_max_minutes": 720,
    }

    base = calc.calculate_hspf2_v3(base_points, **kwargs)
    h2int_power = calc.calculate_hspf2_v3(h2int_power_changed, **kwargs)
    full = calc.calculate_hspf2_v3(full_changed, **kwargs)

    base_case_ii = case_ii_rows(base)
    h2int_case_ii = case_ii_rows(h2int_power)
    full_case_ii = case_ii_rows(full)

    assert base["bin_table"]["region"] == "IV"
    assert base["summary"]["metadata"]["t_OBO"] == 45
    assert base_case_ii
    assert h2int_case_ii
    assert full_case_ii
    assert base["raw_hspf2"] != h2int_power["raw_hspf2"]
    assert base["total_energy"] != h2int_power["total_energy"]

    base_row = base_case_ii[0]
    h2int_row = h2int_case_ii[0]
    full_row = full_case_ii[0]

    assert math.isclose(base_row["q_full"], h2int_row["q_full"], abs_tol=0.01)
    assert math.isclose(base_row["p_full"], h2int_row["p_full"], abs_tol=0.01)
    assert math.isclose(base_row["q_int"], h2int_row["q_int"], abs_tol=0.01)
    assert not math.isclose(base_row["p_int"], h2int_row["p_int"], abs_tol=0.01)
    assert not math.isclose(base_row["COP_bin"], h2int_row["COP_bin"], abs_tol=0.000001)

    assert not math.isclose(base_row["q_full"], full_row["q_full"], abs_tol=0.01)
    assert not math.isclose(base_row["p_full"], full_row["p_full"], abs_tol=0.01)
    assert base_row["debug_info"]["intermediate_capacity_method"] == (
        "ahri_210_240_2026_eq_11_199_to_11_204"
    )
    assert base["summary"]["ahri_210_240_2026_ready"] is True

    for row in base_case_ii:
        assert row["q_aux"] == 0.0
        assert row["e_aux"] == 0.0
        assert row["COP_bin"] > 0.0
        assert row["q_low"] < row["q_int"] < row["q_full"]


def test_hspf2_v3_h2int_power_changes_minimum_speed_limited_low_path():
    calc = AHRIHSPF2Calculator("data/region_configs/usa_hspf2.json")

    base_points = {
        "H01": (12500, 980),
        "H12": (24000, 2200),
        "H1N": (22000, 2000),
        "H11": (12000, 1000),
        "H22": (23200, 2160),
        "H2Int": (13000, 1200),
        "H32": (22000, 2100),
        "H42": (18000, 1900),
        "A_Full": (24000, 2500),
    }
    h2int_power_changed = dict(base_points)
    h2int_power_changed["H2Int"] = (13000, 1400)
    kwargs = {
        "t_off": -10,
        "t_on": -5,
        "defrost_t_test_minutes": 90,
        "defrost_t_max_minutes": 720,
    }

    non_limited_base = calc.calculate_hspf2_v3(base_points, **kwargs)
    non_limited_changed = calc.calculate_hspf2_v3(h2int_power_changed, **kwargs)
    limited_base = calc.calculate_hspf2_v3(
        base_points,
        **kwargs,
        minimum_speed_limited=True,
    )
    limited_changed = calc.calculate_hspf2_v3(
        h2int_power_changed,
        **kwargs,
        minimum_speed_limited=True,
    )

    non_limited_base_row = row_at_temp(non_limited_base, 42)
    non_limited_changed_row = row_at_temp(non_limited_changed, 42)
    limited_base_row = row_at_temp(limited_base, 42)
    limited_changed_row = row_at_temp(limited_changed, 42)

    assert limited_base["summary"]["metadata"]["minimum_speed_limited"] is True
    assert limited_base["summary"]["metadata"]["case_i_low_source"] == "eq_11_189_194"
    assert non_limited_base["summary"]["metadata"]["case_i_low_source"] == "eq_11_187_188"
    assert limited_base["raw_hspf2"] != limited_changed["raw_hspf2"]
    assert limited_base["total_energy"] != limited_changed["total_energy"]

    assert math.isclose(
        non_limited_base_row["p_low"],
        non_limited_changed_row["p_low"],
        abs_tol=0.01,
    )
    assert not math.isclose(
        limited_base_row["p_low"],
        limited_changed_row["p_low"],
        abs_tol=0.01,
    )
    assert math.isclose(limited_base_row["q_low"], limited_changed_row["q_low"], abs_tol=0.01)
    assert math.isclose(limited_base_row["q_full"], limited_changed_row["q_full"], abs_tol=0.01)
    assert math.isclose(limited_base_row["p_full"], limited_changed_row["p_full"], abs_tol=0.01)
    assert math.isclose(limited_base_row["q_int"], limited_changed_row["q_int"], abs_tol=0.01)
    assert not math.isclose(limited_base_row["p_int"], limited_changed_row["p_int"], abs_tol=0.01)
