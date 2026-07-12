import hashlib
import inspect
import json

from core.calculators.standards.ahri_hspf2 import AHRIHSPF2Calculator
from core.calculators.standards.ahri_seer2 import (
    AHRICalculator,
    get_default_ahri_seer2_config,
)


HSPF2_CONFIG_PATH = "data/region_configs/usa_hspf2.json"
SEER2_CONFIG_PATH = "data/region_configs/usa.json"

HSPF2_V3_POINTS = {
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
HSPF2_V3_KWARGS = {
    "t_off": -10,
    "t_on": -5,
    "defrost_t_test_minutes": 90,
    "defrost_t_max_minutes": 720,
}
SEER2_POINTS = {
    "A_Full": (36000, 3000),
    "B_Full": (30000, 2200),
    "B_Low": (18000, 1200),
    "E_Int": (24000, 1700),
    "F_Low": (12000, 900),
}


def _canonical_result_sha256(result):
    payload = json.dumps(result, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def test_hspf2_public_facade_contract_is_locked():
    calculator = AHRIHSPF2Calculator(HSPF2_CONFIG_PATH)

    assert str(inspect.signature(AHRIHSPF2Calculator)) == "(config_path: str)"
    assert str(inspect.signature(calculator.calculate_hspf2)) == (
        "(test_points: dict, *, product_classification: str = "
        "'variable_capacity', **kwargs) -> dict"
    )
    assert str(inspect.signature(calculator.calculate_hspf2_v3)) == (
        "(test_points: dict, **kwargs) -> dict"
    )
    assert str(inspect.signature(calculator.get_test_point_schema)) == (
        "(mode: str = None) -> dict"
    )
    assert str(inspect.signature(calculator.normalize_public_test_points)) == (
        "(test_points: dict) -> dict"
    )
    assert not hasattr(calculator, "calculate_hspf2_v2")

    for attribute in (
        "config",
        "bin_temps",
        "bin_hours",
        "canonical_hspf2_bin_tables",
        "test_point_schema",
        "test_point_aliases",
        "test_point_temps",
        "constants",
        "defaults",
    ):
        assert hasattr(calculator, attribute)


def test_hspf2_v3_characterization_is_deeply_locked():
    result = AHRIHSPF2Calculator(HSPF2_CONFIG_PATH).calculate_hspf2_v3(
        HSPF2_V3_POINTS,
        **HSPF2_V3_KWARGS,
    )

    assert list(result) == [
        "raw_hspf2",
        "raw_hspf2_base",
        "rounded_hspf2",
        "HSPF2",
        "total_load",
        "total_energy",
        "total_heating_btu",
        "total_energy_wh",
        "h42_source",
        "bin_table",
        "summary",
        "bin_details",
    ]
    assert _canonical_result_sha256(result) == (
        "25109558e7c46408ba02c0831c35be8af96abff2c3362452c9a0d00b8209beaf"
    )


def test_seer2_public_facade_and_characterization_are_locked():
    calculator = AHRICalculator(SEER2_CONFIG_PATH)
    result = calculator.calculate_seer2(SEER2_POINTS)

    assert str(inspect.signature(AHRICalculator)) == "(config_path: str)"
    assert str(inspect.signature(calculator.calculate_seer2)) == (
        "(test_points, system_type='HP', p_w_off=0.0, cd_low=None, *, "
        "product_classification='variable_capacity', options=None)"
    )
    assert isinstance(calculator.config, dict)
    assert get_default_ahri_seer2_config()["standard"] == "AHRI 210/240-2023"
    assert list(result) == [
        "SEER2",
        "EER2_A_Full",
        "EER2_B_Low",
        "total_cooling_Btu",
        "total_energy_Wh",
        "system_type",
        "bin_details",
    ]
    assert _canonical_result_sha256(result) == (
        "709c60a32978c9dfed910c07d14a7d3386944a08f049e9fdf56b2049fa5c569a"
    )


def test_seer2_p_w_off_remains_accepted_and_has_no_effect():
    calculator = AHRICalculator(SEER2_CONFIG_PATH)

    assert calculator.calculate_seer2(
        SEER2_POINTS, p_w_off=0.0
    ) == calculator.calculate_seer2(
        SEER2_POINTS,
        p_w_off=123.45,
    )


def test_seer2_facade_delegates_to_variable_engine_for_hp_and_ac():
    calculator = AHRICalculator(SEER2_CONFIG_PATH)

    for system_type in ("HP", "AC"):
        assert calculator.calculate_seer2(
            SEER2_POINTS, system_type=system_type
        ) == calculator._variable_engine.calculate(
            SEER2_POINTS, system_type=system_type
        )
