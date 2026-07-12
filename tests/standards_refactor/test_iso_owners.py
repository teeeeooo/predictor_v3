from __future__ import annotations

import inspect
from pathlib import Path

from core.calculators.standards._iso16358.context import ISO16358ConfigContext
from core.calculators.standards._iso16358.hspf_result import (
    assemble_common_hspf_result,
)
from core.calculators.standards.iso16358 import ISO16358Calculator
from tests.standards_refactor.samples import cspf_fixtures


ROOT = Path(__file__).resolve().parents[2]
HK_CONFIG = ROOT / "data/region_configs/hong_kong.json"


def test_iso_context_loads_once_and_is_shared_by_mode_engines(monkeypatch) -> None:
    opened = []
    original_open = open

    def recording_open(path, *args, **kwargs):
        opened.append(str(path))
        return original_open(path, *args, **kwargs)

    monkeypatch.setattr("builtins.open", recording_open)
    calculator = ISO16358Calculator(str(HK_CONFIG))

    assert opened == [str(HK_CONFIG)]
    assert calculator._cspf_engine._context is calculator._context
    assert calculator._hspf_engine._context is calculator._context


def test_iso_facade_delegates_cspf_and_hspf_to_separate_engines() -> None:
    calculator = ISO16358Calculator(str(HK_CONFIG))
    fixture = cspf_fixtures()["hong_kong_cspf_4_83"]
    cspf_kwargs = {
        "measured_inputs": fixture["measured_points"],
        "declared_capacity": 3500,
    }
    hspf_points = {
        "7_full": {"capacity": 6300, "power": 1500},
        "7_half": {"capacity": 3200, "power": 800},
    }

    assert calculator.calculate_cspf(**cspf_kwargs) == (
        calculator._cspf_engine.calculate_cspf(**cspf_kwargs)
    )
    assert calculator.calculate_hspf(hspf_points) == (
        calculator._hspf_engine.calculate_hspf(hspf_points)
    )
    assert "for " not in inspect.getsource(ISO16358Calculator.calculate_cspf)
    assert "for " not in inspect.getsource(ISO16358Calculator.calculate_hspf)


def test_iso_mutable_cd_compatibility_reaches_private_hspf_owner() -> None:
    calculator = ISO16358Calculator(str(HK_CONFIG))
    calculator.Cd = 0.35

    assert calculator.Cd == 0.35
    assert calculator._context.Cd == 0.35
    assert calculator._hspf_engine.Cd == 0.35


def test_iso_common_result_assembler_preserves_key_order() -> None:
    result = assemble_common_hspf_result(10.0, 2.0, [])

    assert list(result) == [
        "hspf",
        "hstl_wh",
        "hsec_wh",
        "heat_pump_energy_wh",
        "auxiliary_energy_wh",
        "bin_details",
    ]


def test_application_does_not_import_private_iso_owners() -> None:
    for path in (ROOT / "apps/calculator").rglob("*.py"):
        assert "core.calculators.standards._iso16358" not in path.read_text(
            encoding="utf-8"
        )


def test_iso_context_preserves_missing_config_exception(tmp_path) -> None:
    missing = tmp_path / "missing.json"
    try:
        ISO16358ConfigContext(str(missing))
    except FileNotFoundError as exc:
        assert str(exc) == f"설정 파일을 찾을 수 없습니다: {missing}"
    else:
        raise AssertionError("missing ISO config must fail")
