import pytest

from core.calculators.capability import (
    AhriHspf2Request,
    AhriSeer2Request,
    execute_standard_calculation,
)
from core.calculators.standards.ahri_hspf2 import AHRIHSPF2Calculator
from core.calculators.standards.ahri_seer2 import AHRICalculator


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
    assert [row["case"] for row in result["bin_details"]] == [1, 1, 1, 1, 2, 2, 2, 4]


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

    assert result["total_heating_btu"] == pytest.approx(10398.99)
    assert result["total_compressor_energy_wh"] == pytest.approx(934.5634003919118)
    assert result["total_resistance_energy_wh"] == pytest.approx(315.41845773088437)
    assert result["raw_hspf2"] == pytest.approx(8.56889212463095)
    assert result["published_hspf2"] == 8.55


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

    assert result["total_compressor_energy_wh"] == pytest.approx(167.7699938393656)
    assert result["total_resistance_energy_wh"] == pytest.approx(2504.9912075029306)
    assert result["raw_hspf2"] == pytest.approx(3.890729181034762)
    assert result["published_hspf2"] == 3.90


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
    assert result["total_compressor_energy_wh"] == pytest.approx(975.3371449127085)
    assert result["total_resistance_energy_wh"] == pytest.approx(89.29073856975371)
    assert result["raw_hspf2"] == pytest.approx(10.046800549191993)
    assert result["published_hspf2"] == 10.05
    assert metadata["point_sources"]["H2Low"] == "eq_11_253_11_254"
    assert [row["case"] for row in result["bin_details"]] == [1, 1, 1, 2, 2, 2, 2, 3, 8, 8, 8, 8, 8]


@pytest.mark.parametrize(
    "ranges, expected_case",
    (
        ({"low": (-30, 65), "full": (-30, 65), "boost": (-30, 65)}, 4),
        ({"low": (60, 65), "full": (-30, 65), "boost": (-30, 65)}, 5),
        ({"low": (-30, 65), "full": (60, 65), "boost": (60, 65)}, 6),
        ({"low": (60, 65), "full": (-30, 65), "boost": (60, 65)}, 7),
    ),
)
def test_triple_northern_additional_cases_are_reachable(ranges, expected_case):
    calculator = AHRIHSPF2Calculator("data/region_configs/usa_hspf2.json")
    result = calculator.calculate_hspf2(
        TRIPLE_POINTS,
        product_classification="triple_capacity_northern",
        defrost_mode="none",
        t_off=-45.0,
        t_on=-45.0,
        stage_ranges_f=ranges,
    )
    assert any(row["case"] == expected_case for row in result["bin_details"])


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
