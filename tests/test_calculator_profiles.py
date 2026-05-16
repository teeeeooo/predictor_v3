from pathlib import Path

import pytest

from core.calculator_profiles import (
    list_calculator_profiles,
    resolve_calculator_profile,
)


def test_resolve_ahri_seer2_by_profile_id_returns_usa_json():
    profile = resolve_calculator_profile(profile_id="ahri_usa_seer2")

    assert profile.profile_id == "ahri_usa_seer2"
    assert profile.calculator_id == "ahri_seer2"
    assert profile.config_path == "data/region_configs/usa.json"


def test_resolve_ahri_hspf2_by_profile_id_returns_usa_hspf2_json():
    profile = resolve_calculator_profile(profile_id="ahri_usa_hspf2")

    assert profile.profile_id == "ahri_usa_hspf2"
    assert profile.calculator_id == "ahri_hspf2"
    assert profile.config_path == "data/region_configs/usa_hspf2.json"


def test_resolve_ahri_seer2_by_selector():
    profile = resolve_calculator_profile(
        standard="AHRI_210_240",
        region="usa",
        metric="SEER2",
        mode="cooling",
    )

    assert profile.profile_id == "ahri_usa_seer2"


def test_resolve_ahri_hspf2_by_selector():
    profile = resolve_calculator_profile(
        standard="AHRI_210_240",
        region="usa",
        metric="HSPF2",
        mode="heating",
    )

    assert profile.profile_id == "ahri_usa_hspf2"


@pytest.mark.parametrize(
    "metric, mode",
    [
        ("SEER2", "heating"),
        ("HSPF2", "cooling"),
    ],
)
def test_invalid_ahri_metric_mode_combinations_fail_fast(metric, mode):
    with pytest.raises(ValueError):
        resolve_calculator_profile(
            standard="AHRI_210_240",
            region="usa",
            metric=metric,
            mode=mode,
        )


def test_ahri_seer2_never_resolves_to_hspf2_config():
    profile = resolve_calculator_profile(
        standard="AHRI_210_240",
        region="usa",
        metric="SEER2",
        mode="cooling",
    )

    assert profile.config_path != "data/region_configs/usa_hspf2.json"


def test_ahri_hspf2_never_resolves_to_seer2_config():
    profile = resolve_calculator_profile(
        standard="AHRI_210_240",
        region="usa",
        metric="HSPF2",
        mode="heating",
    )

    assert profile.config_path != "data/region_configs/usa.json"


def test_resolved_config_paths_exist():
    for profile in list_calculator_profiles():
        assert Path(profile.config_path).exists()


def test_list_calculator_profiles_returns_enabled_profiles_only():
    profiles = list_calculator_profiles()

    assert {profile.profile_id for profile in profiles} == {
        "ahri_usa_seer2",
        "ahri_usa_hspf2",
        "ks_c9306_cspf",
        "ks_c9306_hspf",
    }
    assert all(profile.enabled for profile in profiles)


def test_resolve_ks_c9306_cspf_by_profile_id_returns_korea_json():
    profile = resolve_calculator_profile(profile_id="ks_c9306_cspf")

    assert profile.profile_id == "ks_c9306_cspf"
    assert profile.calculator_id == "ks_c9306"
    assert profile.config_path == "data/region_configs/korea.json"
    assert profile.metric == "CSPF"
    assert profile.mode == "cooling"


def test_resolve_ks_c9306_hspf_by_profile_id_returns_korea_json():
    profile = resolve_calculator_profile(profile_id="ks_c9306_hspf")

    assert profile.profile_id == "ks_c9306_hspf"
    assert profile.calculator_id == "ks_c9306"
    assert profile.config_path == "data/region_configs/korea.json"
    assert profile.metric == "HSPF"
    assert profile.mode == "heating"


def test_resolve_ks_c9306_cspf_by_selector():
    profile = resolve_calculator_profile(
        standard="KS_C_9306",
        region="korea",
        metric="CSPF",
        mode="cooling",
    )

    assert profile.profile_id == "ks_c9306_cspf"


def test_resolve_ks_c9306_hspf_by_selector():
    profile = resolve_calculator_profile(
        standard="KS_C_9306",
        region="korea",
        metric="HSPF",
        mode="heating",
    )

    assert profile.profile_id == "ks_c9306_hspf"
