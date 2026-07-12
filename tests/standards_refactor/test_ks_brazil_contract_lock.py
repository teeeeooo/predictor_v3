from __future__ import annotations

import dataclasses
import inspect

from core.calculators.capability import (
    BrazilCspfComplianceRequest,
    execute_standard_calculation,
)
from core.calculators.standards.ks_c9306 import KSC9306Calculator
from tests.standards_refactor.samples import (
    ROOT,
    brazil_fixture,
    ks_official_hspf_input,
    ordered_result_sha256,
)


KS_CONFIG = str(ROOT / "data/region_configs/korea.json")


def test_ks_c9306_public_facade_contract_is_locked() -> None:
    calculator = KSC9306Calculator.from_config_path(KS_CONFIG)

    assert str(inspect.signature(KSC9306Calculator)) == (
        "(config: dict, bin_hours=None, default_cd: float = 0.25)"
    )
    assert str(inspect.signature(KSC9306Calculator.from_config_path)) == (
        "(config_path: str) -> 'KSC9306Calculator'"
    )
    assert str(inspect.signature(calculator.calculate_cspf)) == (
        "(measured_inputs: dict, declared_capacity: float = None) -> dict"
    )
    assert str(inspect.signature(calculator.calculate_hspf)) == (
        "(measured_inputs: dict, aux_cop: float = 1.0) -> dict"
    )
    for attribute in ("config", "bin_hours", "Cd", "_config_path"):
        assert hasattr(calculator, attribute)


def test_ks_c9306_cspf_and_hspf_results_are_deeply_locked() -> None:
    calculator = KSC9306Calculator.from_config_path(KS_CONFIG)
    results = {
        "cspf": calculator.calculate_cspf(
            {
                "35_full": {"capacity": 6035.8, "power": 1641.4},
                "35_half": {"capacity": 3420.4, "power": 679.4},
                "29_min": {"capacity": 1759.6, "power": 201.7},
            },
            declared_capacity=6000,
        ),
        "hspf": KSC9306Calculator.from_config_path(KS_CONFIG).calculate_hspf(
            ks_official_hspf_input()
        ),
    }

    assert ordered_result_sha256(results) == (
        "07b0a2dd991ef1e333b9c251345da663c9f1bb7476aa909034c7ddf5f3d5ff37"
    )


def test_brazil_active_composite_capability_is_deeply_locked() -> None:
    fixture = brazil_fixture()
    result = execute_standard_calculation(
        "brazil.cspf_compliance",
        BrazilCspfComplianceRequest(fixture["measured_points"]),
    )

    assert ordered_result_sha256(dataclasses.asdict(result)) == (
        "0e1afb671d0ce4ec282095ceea6d03479b2c3e15b1acc050be59250152cfb31a"
    )
