from __future__ import annotations

import inspect
from pathlib import Path

from core.calculators.standards._en14825.context import EN14825ConfigContext
from core.calculators.standards._en14825.result import assemble_seer_result
from core.calculators.standards.en14825 import EN14825Calculator
from tests.standards_refactor.samples import EN_SEER_POINTS, EN_STANDBY


ROOT = Path(__file__).resolve().parents[2]


def test_en_context_loads_unified_config_once_for_both_engines(monkeypatch) -> None:
    config_path = ROOT / "data/region_configs/en14825.json"
    opened = []
    original_open = open

    def recording_open(path, *args, **kwargs):
        opened.append(str(path))
        return original_open(path, *args, **kwargs)

    monkeypatch.setattr("builtins.open", recording_open)
    calculator = EN14825Calculator(str(config_path))

    assert opened == [str(config_path)]
    assert calculator._seer_engine._context is calculator._context
    assert calculator._scop_engine._context is calculator._context


def test_en_facade_delegates_seasonal_calculation_to_private_engines() -> None:
    calculator = EN14825Calculator()
    kwargs = {
        "test_points": EN_SEER_POINTS,
        "p_design_c": 3.5,
        "t_design_c": 35,
        **EN_STANDBY,
    }

    assert calculator.calculate_seer(**kwargs) == calculator._seer_engine.calculate_seer(
        **kwargs
    )
    facade_source = inspect.getsource(EN14825Calculator.calculate_seer)
    assert "for " not in facade_source
    assert "bin_details" not in facade_source


def test_en_scop_contract_compatibility_resolves_through_point_owner() -> None:
    calculator = EN14825Calculator()
    climate_data = calculator._get_scop_climate_data("warmer")

    through_facade = calculator._resolve_scop_point_contract(
        "warmer", climate_data, 2, -11
    )
    through_owner = calculator._scop_points._resolve_scop_point_contract(
        "warmer", climate_data, 2, -11
    )

    assert through_facade == through_owner
    assert through_facade["mapped_points"] == {"Tbiv": "B"}


def test_en_result_assembler_preserves_public_key_order() -> None:
    assert list(assemble_seer_result(1.2345, 2.3456, 300.126)) == [
        "seer",
        "seer_on",
        "qc_kwh",
    ]


def test_application_does_not_import_private_en_owners() -> None:
    for path in (ROOT / "apps/calculator").rglob("*.py"):
        assert "core.calculators.standards._en14825" not in path.read_text(
            encoding="utf-8"
        )


def test_context_owner_preserves_missing_config_exception(tmp_path) -> None:
    missing = tmp_path / "missing.json"
    try:
        EN14825ConfigContext(str(missing))
    except FileNotFoundError as exc:
        assert str(exc) == f"EN14825 config file not found: {missing}"
    else:
        raise AssertionError("missing EN config must fail")
