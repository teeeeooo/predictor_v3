import math

from core.calculators.standards.ahri_hspf2 import AHRIHSPF2Calculator


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
            expected_q_comp = row["q_full"] * row["delta_j"] * row["hours"]
            assert math.isclose(q_comp, expected_q_comp, abs_tol=1.0), (
                f"bin {bin_no} Case III: q_comp={q_comp}, q_full*hours={expected_q_comp}"
            )
            assert q_aux > 0, f"bin {bin_no} Case III: q_aux must be > 0"
            assert e_aux > 0, f"bin {bin_no} Case III: e_aux must be > 0"
        elif operating_case == "Cut-out":
            assert row["delta_j"] == 0, f"bin {bin_no} Cut-out: delta_j must be 0"
            assert q_comp == 0.0, f"bin {bin_no} Cut-out: q_comp must be 0"
            assert e_comp == 0.0, f"bin {bin_no} Cut-out: e_comp must be 0"
            assert math.isclose(q_aux, q_delivered, abs_tol=0.05), (
                f"bin {bin_no} Cut-out: q_aux must carry full load"
            )
        elif operating_case == "Fractional":
            delta_j = row["delta_j"]
            expected_q_comp = row["q_comp_hp_case"] * delta_j
            expected_e_comp = row["e_comp_hp_case"] * delta_j
            expected_q_aux = (
                row["q_aux_hp_case"] * delta_j
                + row["q_aux_cutout"] * (1.0 - delta_j)
            )
            expected_e_aux = (
                row["e_aux_hp_case"] * delta_j
                + row["e_aux_cutout"] * (1.0 - delta_j)
            )
            assert math.isclose(q_comp, expected_q_comp, abs_tol=0.05)
            assert math.isclose(e_comp, expected_e_comp, abs_tol=0.05)
            assert math.isclose(q_aux, expected_q_aux, abs_tol=0.05)
            assert math.isclose(e_aux, expected_e_aux, abs_tol=0.05)


def test_hspf2_v3_case_activation_and_conservation():
    calc = AHRIHSPF2Calculator("data/region_configs/usa_hspf2.json")
    canonical_points = {
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
    kwargs = {
        "t_off": -10,
        "t_on": -5,
        "defrost_t_test_minutes": 90,
        "defrost_t_max_minutes": 720,
    }

    result = calc.calculate_hspf2_v3(canonical_points, **kwargs)

    assert_case_conservation(result)
    assert result["summary"]["ahri_210_240_2026_ready"] is True

    operating_cases = {row["operating_case"] for row in result["bin_details"]}
    assert "Case I" in operating_cases
    assert "Case II" in operating_cases
    assert "Case III" in operating_cases

    for row in result["bin_details"]:
        if row["operating_case"] == "Case I":
            assert row["HLF_j"] is not None
            assert 0.0 <= row["HLF_j"] <= 1.0
            expected_plf_j = max(0.01, 1.0 - 0.25 * (1.0 - row["HLF_j"]))
            assert math.isclose(row["PLF_j"], expected_plf_j, abs_tol=0.000001)
        elif row["operating_case"] in ("Case II", "Case III"):
            assert row["PLF_j"] == 1.0
            assert row["HLF_j"] in (None, 1.0)

    fractional_rows = [row for row in result["bin_details"] if row["delta_j"] == 0.5]
    assert len(fractional_rows) == 1
    assert fractional_rows[0]["temp_F"] == -8
