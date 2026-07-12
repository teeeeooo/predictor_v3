import pytest

from core.calculators.capability import (
    AhriHspf2Request,
    AhriSeer2Request,
    execute_standard_calculation,
)
from core.calculators.standards._ahri.hspf2_multicapacity import (
    RESISTANCE_BTU_PER_WH,
)
from core.calculators.standards._ahri.hspf2_triple_northern import (
    HSPF2TripleNorthernEngine,
)
from core.calculators.standards.ahri_hspf2 import AHRIHSPF2Calculator
from core.calculators.standards.ahri_seer2 import AHRICalculator

HEATING_LOAD_HOURS = 1701.0

DUAL_SEER_POINTS = {
    "AFull": (48000.0, 4300.0),
    "BFull": (52000.0, 3900.0),
    "BLow": (30000.0, 2200.0),
    "FLow": (34000.0, 2500.0),
}

DUAL_HSPF_POINTS = {
    "AFull": (30000.0, 1.0),
    "H0Low": (22000.0, 1450.0),
    "H1Full": (25000.0, 1800.0),
    "H1Low": (18000.0, 1350.0),
    "H2Full": (21500.0, 1900.0),
    "H2Low": (14500.0, 1450.0),
    "H3Full": (19500.0, 2100.0),
    "H3Low": (10500.0, 1600.0),
}

TRIPLE_POINTS = {
    "AFull": (30000.0, 1.0),
    "H0Low": (26000.0, 1350.0),
    "H1Full": (28000.0, 1850.0),
    "H1Low": (21000.0, 1300.0),
    "H2Boost": (30000.0, 2400.0),
    "H2Full": (25500.0, 2050.0),
    "H3Boost": (28000.0, 3000.0),
    "H3Full": (22000.0, 2350.0),
    "H3Low": (14500.0, 1750.0),
    "H4Boost": (25000.0, 3400.0),
}


def test_dual_stage_seer2_matches_accepted_2026_golden():
    calculator = AHRICalculator("data/region_configs/usa.json")
    result = calculator.calculate_seer2(
        DUAL_SEER_POINTS,
        product_classification="dual_stage",
        cd_low=0.24,
        options={"cd_full": 0.18},
    )

    assert result["raw_seer2"] == pytest.approx(12.454035205677503)
    assert result["published_seer2"] == 12.45
    assert result["total_cooling_Btu"] == pytest.approx(17117.202797202794)
    assert result["total_energy_Wh"] == pytest.approx(1374.4302560987994)
    assert [row["case"] for row in result["bin_details"]] == [
        1,
        1,
        1,
        1,
        2,
        2,
        2,
        4,
    ]


def test_dual_stage_seer2_lockout_activates_case_three():
    calculator = AHRICalculator("data/region_configs/usa.json")
    result = calculator.calculate_seer2(
        DUAL_SEER_POINTS,
        product_classification="dual_stage",
        options={
            "cd_low": 0.20,
            "cd_full": 0.20,
            "low_stage_lockout_enabled": True,
            "low_stage_lockout_temp_f": 82.0,
        },
    )

    assert any(row["case"] == 3 for row in result["bin_details"])
    assert all(
        not row["low_permitted"]
        for row in result["bin_details"]
        if row["temp_F"] >= 82.0
    )


def test_dual_stage_hspf2_matches_recalculated_2026_golden():
    calculator = AHRIHSPF2Calculator("data/region_configs/usa_hspf2.json")
    result = calculator.calculate_hspf2(
        DUAL_HSPF_POINTS,
        product_classification="dual_stage",
        cd_low=0.18,
        cd_full=0.22,
        defrost_mode="explicit_override",
        defrost_factor=1.03,
        t_off=-40.0,
        t_on=-40.0,
    )

    assert result["normalized_heating_aggregate"] == pytest.approx(10398.99)
    assert result["normalized_compressor_energy_wh"] == pytest.approx(
        934.5634003919118
    )
    assert result["normalized_resistance_energy_wh"] == pytest.approx(
        315.41845773088437
    )
    assert result["total_heating_btu"] == pytest.approx(
        10398.99 * HEATING_LOAD_HOURS
    )
    assert result["total_compressor_energy_wh"] == pytest.approx(
        934.5634003919118 * HEATING_LOAD_HOURS
    )
    assert result["total_resistance_energy_wh"] == pytest.approx(
        315.41845773088437 * HEATING_LOAD_HOURS
    )
    assert result["total_energy_wh"] == pytest.approx(
        (934.5634003919118 + 315.41845773088437)
        * HEATING_LOAD_HOURS
    )
    assert result["raw_hspf2"] == pytest.approx(8.56889212463095)
    assert result["published_hspf2"] == 8.55
    assert result["summary"]["metadata"]["heating_load_hours"] == 1701.0
    assert sum(row["seasonal_q_j"] for row in result["bin_details"]) == (
        pytest.approx(result["total_heating_btu"])
    )
    assert sum(row["seasonal_E_j"] for row in result["bin_details"]) == (
        pytest.approx(result["total_energy_wh"])
    )


def test_dual_stage_hspf2_cutout_uses_3412_resistance_conversion():
    calculator = AHRIHSPF2Calculator("data/region_configs/usa_hspf2.json")
    result = calculator.calculate_hspf2(
        {**DUAL_HSPF_POINTS, "H4Full": (17000.0, 2300.0)},
        product_classification="dual_stage",
        cd_low=0.18,
        cd_full=0.22,
        defrost_mode="none",
        t_off=35.0,
        t_on=45.0,
    )

    assert result["normalized_compressor_energy_wh"] == pytest.approx(
        167.7699938393656
    )
    assert result["normalized_resistance_energy_wh"] == pytest.approx(
        2504.9912075029306
    )
    assert result["total_compressor_energy_wh"] == pytest.approx(
        167.7699938393656 * HEATING_LOAD_HOURS
    )
    assert result["total_resistance_energy_wh"] == pytest.approx(
        2504.9912075029306 * HEATING_LOAD_HOURS
    )
    assert result["raw_hspf2"] == pytest.approx(3.890729181034762)
    assert result["published_hspf2"] == 3.90


def test_dual_h2low_untested_uses_equations_11_44_and_11_50():
    calculator = AHRIHSPF2Calculator("data/region_configs/usa_hspf2.json")
    points = {key: value for key, value in DUAL_HSPF_POINTS.items() if key != "H2Low"}
    result = calculator.calculate_hspf2(
        points,
        product_classification="dual_stage",
        h2_low_tested=False,
        defrost_mode="none",
        t_off=-40.0,
        t_on=-40.0,
    )

    metadata = result["summary"]["metadata"]
    expected_capacity = 0.90 * (10500.0 + 0.6 * (18000.0 - 10500.0))
    expected_power = 0.985 * (1600.0 + 0.6 * (1350.0 - 1600.0))
    assert metadata["point_sources"]["H2Low"] == "eq_11_44_11_50"
    assert metadata["resolved_points"]["H2Low"] == pytest.approx(
        (expected_capacity, expected_power)
    )
    assert metadata["resolved_points"]["H2Low"] == pytest.approx(
        (13500.0, 1428.25)
    )


def test_triple_northern_matches_covered_official_compressor_path_and_2026_corrections():
    calculator = AHRIHSPF2Calculator("data/region_configs/usa_hspf2.json")
    result = calculator.calculate_hspf2(
        TRIPLE_POINTS,
        product_classification="triple_capacity_northern",
        cd_low=0.28,
        cd_full=0.22,
        cd_boost=0.18,
        defrost_mode="explicit_override",
        defrost_factor=1.028571429,
        t_off=-45.0,
        t_on=-45.0,
        stage_ranges_f={
            "low": (40.0, 65.0),
            "full": (20.0, 50.0),
            "boost": (-20.0, 30.0),
        },
    )

    metadata = result["summary"]["metadata"]
    assert result["normalized_compressor_energy_wh"] == pytest.approx(
        975.3371449127085
    )
    assert result["normalized_resistance_energy_wh"] == pytest.approx(
        89.29073856975371
    )
    assert result["total_compressor_energy_wh"] == pytest.approx(
        975.3371449127085 * HEATING_LOAD_HOURS
    )
    assert result["total_resistance_energy_wh"] == pytest.approx(
        89.29073856975371 * HEATING_LOAD_HOURS
    )
    assert result["raw_hspf2"] == pytest.approx(10.046800549191993)
    assert result["published_hspf2"] == 10.05
    assert metadata["point_sources"]["H2Low"] == (
        "not_applicable_to_permitted_range"
    )
    assert metadata["point_sources"]["H3Low"] == (
        "not_applicable_to_permitted_range"
    )
    assert "H2Low" not in metadata["resolved_points"]
    assert "H3Low" not in metadata["resolved_points"]
    assert [row["case"] for row in result["bin_details"]] == [
        1,
        1,
        1,
        2,
        2,
        2,
        2,
        3,
        8,
        8,
        8,
        8,
        8,
    ]


def test_triple_h3low_test_forces_equations_11_253_and_11_254():
    calculator = AHRIHSPF2Calculator("data/region_configs/usa_hspf2.json")
    result = calculator.calculate_hspf2(
        {**TRIPLE_POINTS, "H2Low": (18500.0, 1550.0)},
        product_classification="triple_capacity_northern",
        h3_low_tested=True,
        h2_low_tested=True,
        defrost_mode="none",
        t_off=-45.0,
        t_on=-45.0,
        stage_ranges_f={
            "low": (37.0, 65.0),
            "full": (20.0, 50.0),
            "boost": (-20.0, 30.0),
        },
    )

    metadata = result["summary"]["metadata"]
    expected_capacity = 0.90 * (14500.0 + 0.6 * (21000.0 - 14500.0))
    expected_power = 0.985 * (1750.0 + 0.6 * (1300.0 - 1750.0))
    assert metadata["point_sources"]["H2Low"] == (
        "eq_11_253_11_254_from_tested_h3low"
    )
    assert metadata["resolved_points"]["H2Low"] == pytest.approx(
        (expected_capacity, expected_power)
    )
    assert metadata["resolved_points"]["H2Low"] == pytest.approx(
        (16560.0, 1457.8)
    )


@pytest.mark.parametrize(
    (
        "equation_reference",
        "expected_case",
        "load",
        "permitted",
        "expected_fractions",
        "expected_delta",
        "expected_comp",
        "expected_resistance",
    ),
    (
        (
            "Section 11.2.2.6 Case 4 / Equation 11.269",
            4,
            150.0,
            {"low": True, "full": True, "boost": True},
            {"low": 0.5, "full": 0.5},
            0.8,
            1.2,
            0.8792497069167643,
        ),
        (
            "Section 11.2.2.6 Case 5 Full/Boost interpolation",
            5,
            250.0,
            {"low": False, "full": True, "boost": True},
            {"full": 0.5, "boost": 0.5},
            0.6,
            1.5,
            2.9308323563892147,
        ),
        (
            "Section 11.2.2.6 Case 6 Low continuous plus resistance",
            6,
            150.0,
            {"low": True, "full": False, "boost": False},
            {"low": 1.0},
            0.8,
            0.8,
            2.0515826494724503,
        ),
        (
            "Section 11.2.2.6 Case 7 Full continuous plus resistance",
            7,
            250.0,
            {"low": False, "full": True, "boost": False},
            {"full": 1.0},
            0.7,
            1.4,
            3.223915592028136,
        ),
    ),
    ids=("case4-eq11-269", "case5", "case6", "case7"),
)
def test_triple_cases_4_to_7_equation_level_contributions(
    equation_reference,
    expected_case,
    load,
    permitted,
    expected_fractions,
    expected_delta,
    expected_comp,
    expected_resistance,
):
    fraction = 0.1
    capacities = {"low": 100.0, "full": 200.0, "boost": 300.0}
    powers = {"low": 10.0, "full": 20.0, "boost": 30.0}
    deltas = {"low": 0.8, "full": 0.7, "boost": 0.6}
    cds = {"low": 0.20, "full": 0.20, "boost": 0.20}

    case, e_comp, e_res, stage_fractions, plf = (
        HSPF2TripleNorthernEngine._evaluate_case(
            load=load,
            fraction=fraction,
            permitted=permitted,
            capacities=capacities,
            powers=powers,
            deltas=deltas,
            cds=cds,
        )
    )

    assert equation_reference.startswith("Section 11.2.2.6")
    assert case == expected_case
    assert stage_fractions == pytest.approx(expected_fractions)
    assert plf is None
    assert expected_delta in deltas.values()
    assert e_comp == pytest.approx(expected_comp)
    assert e_res == pytest.approx(expected_resistance)
    assert e_comp + e_res == pytest.approx(expected_comp + expected_resistance)
    assert (e_comp + e_res) * HEATING_LOAD_HOURS == pytest.approx(
        (expected_comp + expected_resistance) * HEATING_LOAD_HOURS
    )
    assert load * fraction * HEATING_LOAD_HOURS == pytest.approx(
        load * 0.1 * 1701.0
    )
    assert e_res * RESISTANCE_BTU_PER_WH >= 0.0


def test_stable_capability_ids_route_product_discriminators():
    seer_result = execute_standard_calculation(
        "ahri210240.seer2",
        AhriSeer2Request(
            DUAL_SEER_POINTS,
            product_classification="dual_stage",
            parameters={"cd_full": 0.18},
            cd_low=0.24,
        ),
    )
    hspf_result = execute_standard_calculation(
        "ahri210240.hspf2",
        AhriHspf2Request(
            DUAL_HSPF_POINTS,
            product_classification="dual_stage",
            parameters={
                "cd_low": 0.18,
                "cd_full": 0.22,
                "defrost_mode": "explicit_override",
                "defrost_factor": 1.03,
                "t_off": -40.0,
                "t_on": -40.0,
            },
        ),
    )

    assert seer_result["product_classification"] == "dual_stage"
    assert hspf_result["product_classification"] == "dual_stage"
