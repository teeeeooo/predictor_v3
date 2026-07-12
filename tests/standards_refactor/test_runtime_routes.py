from __future__ import annotations

import importlib
import json

from core.calculators.capability import (
    BrazilCspfComplianceRequest,
    En14825ScopRequest,
    En14825SeerRequest,
    Iso16358CspfRequest,
    Iso16358HspfRequest,
    KsC9306CspfRequest,
    KsC9306HspfRequest,
    execute_standard_calculation,
)
from core.calculators.dispatcher import create_calculator_for_profile
from core.calculators.profiles import list_calculator_profiles
from core.calculators.standards.en14825 import EN14825Calculator
from core.calculators.standards.iso16358 import ISO16358Calculator
from core.calculators.standards.ks_c9306 import KSC9306Calculator
from tests.standards_refactor.samples import (
    EN_SEER_POINTS,
    EN_STANDBY,
    ROOT,
    brazil_fixture,
    cspf_fixtures,
    en_scop_points,
    ks_official_hspf_input,
)


NON_AHRI_PROFILE_IDS = (
    "en14825_scop",
    "en14825_seer",
    "ks_c9306_cspf",
    "ks_c9306_hspf",
    "iso_t1_default_2point_cspf",
    "brazil_cspf_compliance",
    "india_iseer_cspf",
    "hong_kong_cspf",
    "hong_kong_hspf",
    "saso_t3_cspf",
)


def _capability_cases() -> list[tuple[str, object, str | None]]:
    fixtures = cspf_fixtures()
    ks_cspf_points = {
        "35_full": {"capacity": 6035.8, "power": 1641.4},
        "35_half": {"capacity": 3420.4, "power": 679.4},
        "29_min": {"capacity": 1759.6, "power": 201.7},
    }
    return [
        (
            "en14825.seer",
            En14825SeerRequest(
                parameters={
                    "test_points": EN_SEER_POINTS,
                    "p_design_c": 3.5,
                    "t_design_c": 35,
                    **EN_STANDBY,
                }
            ),
            "seer",
        ),
        (
            "en14825.scop",
            En14825ScopRequest(
                parameters={
                    "test_points": en_scop_points(-10, -11),
                    "p_design_h": 2.4,
                    "climate": "average",
                    "tbiv_temp_c": -10,
                    "tol_temp_c": -11,
                    **EN_STANDBY,
                }
            ),
            "scop",
        ),
        (
            "ks_c9306.cspf",
            KsC9306CspfRequest("ks_c9306_cspf", ks_cspf_points, 6000),
            "cspf",
        ),
        (
            "ks_c9306.hspf",
            KsC9306HspfRequest("ks_c9306_hspf", ks_official_hspf_input()),
            "hspf",
        ),
        (
            "iso16358.cspf",
            Iso16358CspfRequest(
                "iso_t1_default_2point_cspf",
                fixtures["southeast_asia_iso_basic_cspf_4_665"][
                    "measured_points"
                ],
            ),
            "cspf",
        ),
        (
            "iso16358.cspf",
            Iso16358CspfRequest(
                "india_iseer_cspf",
                fixtures["india_iseer_5_00"]["measured_points"],
            ),
            "cspf",
        ),
        (
            "iso16358.cspf",
            Iso16358CspfRequest(
                "hong_kong_cspf",
                fixtures["hong_kong_cspf_4_83"]["measured_points"],
                3500,
            ),
            "cspf",
        ),
        (
            "iso16358.hspf",
            Iso16358HspfRequest(
                "hong_kong_hspf",
                {
                    "7_full": {"capacity": 6300, "power": 1500},
                    "7_half": {"capacity": 3200, "power": 800},
                },
            ),
            "hspf",
        ),
        (
            "iso16358.cspf",
            Iso16358CspfRequest(
                "saso_t3_cspf",
                fixtures["saso_cspf_4_95"]["measured_points"],
            ),
            "cspf",
        ),
        (
            "brazil.cspf_compliance",
            BrazilCspfComplianceRequest(brazil_fixture()["measured_points"]),
            None,
        ),
    ]


def test_all_active_facades_import_from_non_repo_cwd(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    for module_name in (
        "app_calculator",
        "core.calculators.standards.en14825",
        "core.calculators.standards.iso16358",
        "core.calculators.standards.ks_c9306",
        "core.calculators.standards.ahri_seer2",
        "core.calculators.standards.ahri_hspf2",
    ):
        assert importlib.import_module(module_name) is not None


def test_enabled_profile_resources_construct_from_non_repo_cwd(
    tmp_path, monkeypatch
) -> None:
    monkeypatch.chdir(tmp_path)
    enabled = {profile.profile_id for profile in list_calculator_profiles()}

    assert set(NON_AHRI_PROFILE_IDS) <= enabled
    for profile_id in enabled:
        assert create_calculator_for_profile(profile_id=profile_id) is not None


def test_each_non_ahri_active_capability_calculates_from_non_repo_cwd(
    tmp_path, monkeypatch
) -> None:
    monkeypatch.chdir(tmp_path)
    for capability_id, request, result_key in _capability_cases():
        result = execute_standard_calculation(capability_id, request)
        if result_key is None:
            assert result.final_passed is True
        else:
            assert result[result_key] > 0


def test_explicit_standard_config_path_overrides_remain_supported(tmp_path) -> None:
    cases = (
        ("en14825.json", EN14825Calculator, "config_path"),
        ("hong_kong.json", ISO16358Calculator, None),
        ("korea.json", KSC9306Calculator.from_config_path, "_config_path"),
    )
    for source_name, constructor, path_attribute in cases:
        source = ROOT / "data/region_configs" / source_name
        override = tmp_path / f"override-{source_name}"
        override.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
        calculator = constructor(str(override))
        assert isinstance(calculator.config, dict)
        if path_attribute is not None:
            assert getattr(calculator, path_attribute) == str(override)


def test_asnzs_profile_remains_disabled_and_unreachable() -> None:
    all_profiles = {profile.profile_id: profile for profile in list_calculator_profiles(False)}

    assert all_profiles["asnzs_excel_hspf_compat"].enabled is False
    assert "asnzs_excel_hspf_compat" not in {
        profile.profile_id for profile in list_calculator_profiles()
    }
