from __future__ import annotations

import inspect
from pathlib import Path

from core.calculators.standards._ks_c9306.context import KSC9306ConfigContext
from core.calculators.standards._ks_c9306.result import assemble_cspf_result
from core.calculators.standards.ks_c9306 import KSC9306Calculator
from tests.standards_refactor.samples import ks_official_hspf_input


ROOT = Path(__file__).resolve().parents[2]
KS_CONFIG = ROOT / "data/region_configs/korea.json"


def test_ks_context_loads_once_and_is_shared_by_mode_engines(monkeypatch) -> None:
    opened = []
    original_open = open

    def recording_open(path, *args, **kwargs):
        opened.append(str(path))
        return original_open(path, *args, **kwargs)

    monkeypatch.setattr("builtins.open", recording_open)
    calculator = KSC9306Calculator.from_config_path(str(KS_CONFIG))

    assert opened == [str(KS_CONFIG)]
    assert calculator._cspf_engine._context is calculator._context
    assert calculator._hspf_engine._context is calculator._context


def test_ks_facade_delegates_to_independent_cspf_and_hspf_engines() -> None:
    calculator = KSC9306Calculator.from_config_path(str(KS_CONFIG))
    cspf_points = {
        "35_full": {"capacity": 6035.8, "power": 1641.4},
        "35_half": {"capacity": 3420.4, "power": 679.4},
        "29_min": {"capacity": 1759.6, "power": 201.7},
    }

    assert calculator.calculate_cspf(cspf_points, 6000) == (
        calculator._cspf_engine.calculate_cspf(cspf_points, 6000)
    )
    hspf_input = ks_official_hspf_input()
    assert calculator.calculate_hspf(hspf_input) == (
        calculator._hspf_engine.calculate_hspf(hspf_input)
    )
    assert "for " not in inspect.getsource(KSC9306Calculator.calculate_cspf)
    assert "for " not in inspect.getsource(KSC9306Calculator.calculate_hspf)


def test_ks_mutable_cd_compatibility_reaches_both_private_engines() -> None:
    calculator = KSC9306Calculator.from_config_path(str(KS_CONFIG))
    calculator.Cd = 0.35

    assert calculator.Cd == 0.35
    assert calculator._context.Cd == 0.35
    assert calculator._cspf_engine.Cd == 0.35
    assert calculator._hspf_engine.Cd == 0.35


def test_ks_result_assembler_preserves_cspf_key_order() -> None:
    assert list(assemble_cspf_result(10.0, 2.0, [])) == [
        "cspf",
        "annual_cooling_kwh",
        "annual_power_kwh",
        "bin_details",
    ]


def test_ks_private_owners_do_not_call_iso_public_facade() -> None:
    owner_root = ROOT / "core/calculators/standards/_ks_c9306"
    for path in owner_root.glob("*.py"):
        source = path.read_text(encoding="utf-8")
        assert "ISO16358Calculator" not in source
        assert "standards.iso16358" not in source


def test_application_does_not_import_private_ks_owners() -> None:
    for path in (ROOT / "apps/calculator").rglob("*.py"):
        assert "core.calculators.standards._ks_c9306" not in path.read_text(
            encoding="utf-8"
        )


def test_ks_context_preserves_missing_config_exception(tmp_path) -> None:
    missing = tmp_path / "missing.json"
    try:
        KSC9306ConfigContext.from_config_path(str(missing))
    except FileNotFoundError as exc:
        assert str(exc) == f"설정 파일을 찾을 수 없습니다: {missing}"
    else:
        raise AssertionError("missing KS config must fail")
