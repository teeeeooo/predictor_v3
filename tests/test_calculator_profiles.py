from pathlib import Path

import pytest

from core.calculators.profiles import (
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


def test_resolve_en14825_scop_by_profile_id_returns_unified_en14825_json():
    profile = resolve_calculator_profile(profile_id="en14825_scop")

    assert profile.profile_id == "en14825_scop"
    assert profile.standard == "EN_14825"
    assert profile.region == "europe"
    assert profile.metric == "SCOP"
    assert profile.mode == "heating"
    assert profile.calculator_id == "en14825"
    assert profile.config_path == "data/region_configs/en14825.json"


def test_resolve_en14825_seer_by_profile_id_uses_unified_en14825_json():
    profile = resolve_calculator_profile(profile_id="en14825_seer")

    assert profile.profile_id == "en14825_seer"
    assert profile.standard == "EN_14825"
    assert profile.region == "europe"
    assert profile.metric == "SEER"
    assert profile.mode == "cooling"
    assert profile.calculator_id == "en14825"
    assert profile.config_path == "data/region_configs/en14825.json"


def test_resolve_en14825_seer_by_selector():
    profile = resolve_calculator_profile(
        standard="EN_14825",
        region="europe",
        metric="SEER",
        mode="cooling",
    )

    assert profile.profile_id == "en14825_seer"


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
        "en14825_scop",
        "en14825_seer",
        "ks_c9306_cspf",
        "ks_c9306_hspf",
        "iso_t1_default_2point_cspf",
        "india_iseer_cspf",
        "hong_kong_cspf",
        "hong_kong_hspf",
        "saso_t3_cspf",
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


@pytest.mark.parametrize(
    "profile_id, region, metric, config_path",
    [
        (
            "iso_t1_default_2point_cspf",
            "generic_t1",
            "CSPF",
            "data/region_configs/iso_t1_default_2point.json",
        ),
        (
            "india_iseer_cspf",
            "india",
            "ISEER",
            "data/region_configs/india_iseer.json",
        ),
        (
            "hong_kong_cspf",
            "hong_kong",
            "CSPF",
            "data/region_configs/hong_kong.json",
        ),
        (
            "saso_t3_cspf",
            "saso",
            "CSPF",
            "data/region_configs/saso.json",
        ),
    ],
)
def test_resolve_iso16358_cspf_profiles(profile_id, region, metric, config_path):
    profile = resolve_calculator_profile(profile_id=profile_id)

    assert profile.standard == "ISO_16358"
    assert profile.region == region
    assert profile.metric == metric
    assert profile.mode == "cooling"
    assert profile.calculator_id == "iso16358"
    assert profile.config_path == config_path


def test_resolve_hong_kong_hspf_by_profile_id_returns_hong_kong_json():
    profile = resolve_calculator_profile(profile_id="hong_kong_hspf")

    assert profile.profile_id == "hong_kong_hspf"
    assert profile.standard == "ISO_16358"
    assert profile.region == "hong_kong"
    assert profile.metric == "HSPF"
    assert profile.mode == "heating"
    assert profile.calculator_id == "iso16358"
    assert profile.config_path == "data/region_configs/hong_kong.json"


def test_resolve_hong_kong_hspf_by_selector():
    profile = resolve_calculator_profile(
        standard="ISO_16358",
        region="hong_kong",
        metric="HSPF",
        mode="heating",
    )

    assert profile.profile_id == "hong_kong_hspf"


def test_hong_kong_cspf_and_hspf_share_config_but_resolve_independently():
    cspf = resolve_calculator_profile(profile_id="hong_kong_cspf")
    hspf = resolve_calculator_profile(profile_id="hong_kong_hspf")

    assert cspf.config_path == hspf.config_path
    assert cspf.calculator_id == hspf.calculator_id == "iso16358"
    assert (cspf.metric, cspf.mode) == ("CSPF", "cooling")
    assert (hspf.metric, hspf.mode) == ("HSPF", "heating")


def test_asnzs_excel_hspf_compat_profile_is_disabled_until_explicit_exposure():
    profiles = list_calculator_profiles(enabled_only=False)
    profile = next(
        item for item in profiles if item.profile_id == "asnzs_excel_hspf_compat"
    )

    assert profile.calculator_id == "asnzs_excel_hspf"
    assert profile.enabled is False

    with pytest.raises(ValueError, match="match exactly one enabled profile"):
        resolve_calculator_profile(profile_id="asnzs_excel_hspf_compat")
