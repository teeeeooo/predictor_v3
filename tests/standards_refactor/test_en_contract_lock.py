from __future__ import annotations

import inspect

from core.calculators.standards.en14825 import EN14825Calculator
from tests.standards_refactor.samples import (
    EN_SEER_POINTS,
    EN_STANDBY,
    en_scop_points,
    ordered_result_sha256,
)


def test_en14825_public_facade_contract_is_locked() -> None:
    calculator = EN14825Calculator()

    assert str(inspect.signature(EN14825Calculator)) == "(config_path: str = None)"
    assert str(inspect.signature(calculator.calculate_seer)) == (
        "(test_points: dict, p_to: float, p_sb: float, p_ck: float, "
        "p_off: float, p_design_c: float, t_design_c: float = None, "
        "cd: float = None, *, appliance_type: str = None) -> dict"
    )
    assert str(inspect.signature(calculator.calculate_seer_with_details)) == (
        "(test_points: dict, p_to: float, p_sb: float, p_ck: float, "
        "p_off: float, p_design_c: float, t_design_c: float = None, "
        "cd: float = None, *, appliance_type: str = None) -> dict"
    )
    assert str(inspect.signature(calculator.calculate_scop)) == (
        "(test_points: dict, p_to: float, p_sb: float, p_ck: float, "
        "p_off: float, p_design_h: float, climate: str, cd: float = None, "
        "appliance_type: str = None, tbiv_temp_c: float = None, "
        "tol_temp_c: float = None) -> dict"
    )
    for attribute in ("config_path", "config", "seer_config", "scop_config"):
        assert hasattr(calculator, attribute)


def test_en14825_supported_branch_results_are_deeply_locked() -> None:
    calculator = EN14825Calculator()
    results = {
        "seer_reversible": calculator.calculate_seer_with_details(
            test_points=EN_SEER_POINTS,
            p_design_c=3.5,
            t_design_c=35,
            appliance_type="reversible",
            **EN_STANDBY,
        ),
        "seer_cooling_only": calculator.calculate_seer_with_details(
            test_points=EN_SEER_POINTS,
            p_design_c=3.5,
            t_design_c=35,
            appliance_type="cooling_only",
            **EN_STANDBY,
        ),
        "scop_average": calculator.calculate_scop(
            test_points=en_scop_points(-10, -11),
            p_design_h=2.4,
            climate="average",
            tbiv_temp_c=-10,
            tol_temp_c=-11,
            **EN_STANDBY,
        ),
        "scop_warmer": calculator.calculate_scop(
            test_points=en_scop_points(2, -11),
            p_design_h=1.3,
            climate="warmer",
            tbiv_temp_c=2,
            tol_temp_c=-11,
            **EN_STANDBY,
        ),
        "scop_colder": calculator.calculate_scop(
            test_points=en_scop_points(-15, -22),
            p_design_h=2.942,
            climate="colder",
            tbiv_temp_c=-15,
            tol_temp_c=-22,
            **EN_STANDBY,
        ),
    }

    assert ordered_result_sha256(results) == (
        "c2386f8bad333d147ddb0ae1e0d9ec090d34c11742fe0bcc6b77c306a7a6a879"
    )
