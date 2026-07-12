from __future__ import annotations

import inspect

from core.calculators.standards.iso16358 import ISO16358Calculator
from tests.standards_refactor.samples import ROOT, cspf_fixtures, ordered_result_sha256


def _config(name: str) -> str:
    return str(ROOT / "data/region_configs" / name)


def test_iso16358_public_facade_contract_is_locked() -> None:
    calculator = ISO16358Calculator(_config("hong_kong.json"))

    assert str(inspect.signature(ISO16358Calculator)) == "(config_path: str)"
    assert str(inspect.signature(calculator.calculate_cspf)) == (
        "(measured_inputs: dict, declared_capacity: float = None) -> dict"
    )
    assert str(inspect.signature(calculator.calculate_hspf)) == (
        "(measured_inputs: dict, aux_cop: float = 1.0) -> dict"
    )
    assert str(inspect.signature(calculator.calculate_hspf_iso16358_common)) == (
        "(measured_inputs: dict, rated_heating_capacity: float | None = None, "
        "aux_cop: float = 1.0) -> dict"
    )
    for attribute in (
        "config",
        "t_100_load",
        "t_0_load",
        "Cd",
        "building_load_source",
        "reference_point",
        "power_interpolation_method",
        "iso_boundary_temperature_rounding",
        "round_test_values",
        "rounding_method",
        "points_config",
        "derived_rules",
        "bin_hours",
    ):
        assert hasattr(calculator, attribute)


def test_iso16358_active_profile_results_are_deeply_locked() -> None:
    fixtures = cspf_fixtures()
    cases = {
        "iso_t1_default_2point_cspf": (
            "iso_t1_default_2point.json",
            "southeast_asia_iso_basic_cspf_4_665",
            None,
        ),
        "india_iseer_cspf": ("india_iseer.json", "india_iseer_5_00", None),
        "hong_kong_cspf": ("hong_kong.json", "hong_kong_cspf_4_83", 3500),
        "saso_t3_cspf": ("saso.json", "saso_cspf_4_95", None),
    }
    results = {}
    for profile_id, (config_name, fixture_id, declared_capacity) in cases.items():
        kwargs = (
            {}
            if declared_capacity is None
            else {"declared_capacity": declared_capacity}
        )
        results[profile_id] = ISO16358Calculator(_config(config_name)).calculate_cspf(
            fixtures[fixture_id]["measured_points"],
            **kwargs,
        )

    results["hong_kong_hspf"] = ISO16358Calculator(
        _config("hong_kong.json")
    ).calculate_hspf(
        {
            "7_full": {"capacity": 6300, "power": 1500},
            "7_half": {"capacity": 3200, "power": 800},
        }
    )

    assert ordered_result_sha256(results) == (
        "3958d6b10c9982252558dc0e0ff5db850f620c2516fba53aa51c6df80fbd40c6"
    )
