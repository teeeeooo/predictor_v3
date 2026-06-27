from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass(frozen=True)
class CalculatorProfile:
    profile_id: str
    standard: str
    region: str
    metric: str
    mode: str
    calculator_id: str
    config_path: str
    enabled: bool = True


_CALCULATOR_PROFILES: Tuple[CalculatorProfile, ...] = (
    CalculatorProfile(
        profile_id="ahri_usa_seer2",
        standard="AHRI_210_240",
        region="usa",
        metric="SEER2",
        mode="cooling",
        calculator_id="ahri_seer2",
        config_path="data/region_configs/usa.json",
        enabled=True,
    ),
    CalculatorProfile(
        profile_id="ahri_usa_hspf2",
        standard="AHRI_210_240",
        region="usa",
        metric="HSPF2",
        mode="heating",
        calculator_id="ahri_hspf2",
        config_path="data/region_configs/usa_hspf2.json",
        enabled=True,
    ),
    CalculatorProfile(
        profile_id="en14825_scop",
        standard="EN_14825",
        region="europe",
        metric="SCOP",
        mode="heating",
        calculator_id="en14825",
        config_path="data/region_configs/en14825.json",
        enabled=True,
    ),
    CalculatorProfile(
        profile_id="en14825_seer",
        standard="EN_14825",
        region="europe",
        metric="SEER",
        mode="cooling",
        calculator_id="en14825",
        config_path="data/region_configs/en14825.json",
        enabled=True,
    ),
    CalculatorProfile(
        profile_id="ks_c9306_cspf",
        standard="KS_C_9306",
        region="korea",
        metric="CSPF",
        mode="cooling",
        calculator_id="ks_c9306",
        config_path="data/region_configs/korea.json",
        enabled=True,
    ),
    CalculatorProfile(
        profile_id="ks_c9306_hspf",
        standard="KS_C_9306",
        region="korea",
        metric="HSPF",
        mode="heating",
        calculator_id="ks_c9306",
        config_path="data/region_configs/korea.json",
        enabled=True,
    ),
    CalculatorProfile(
        profile_id="iso_t1_default_2point_cspf",
        standard="ISO_16358",
        region="generic_t1",
        metric="CSPF",
        mode="cooling",
        calculator_id="iso16358",
        config_path="data/region_configs/iso_t1_default_2point.json",
        enabled=True,
    ),
    CalculatorProfile(
        profile_id="india_iseer_cspf",
        standard="ISO_16358",
        region="india",
        metric="ISEER",
        mode="cooling",
        calculator_id="iso16358",
        config_path="data/region_configs/india_iseer.json",
        enabled=True,
    ),
    CalculatorProfile(
        profile_id="hong_kong_cspf",
        standard="ISO_16358",
        region="hong_kong",
        metric="CSPF",
        mode="cooling",
        calculator_id="iso16358",
        config_path="data/region_configs/hong_kong.json",
        enabled=True,
    ),
    CalculatorProfile(
        profile_id="hong_kong_hspf",
        standard="ISO_16358",
        region="hong_kong",
        metric="HSPF",
        mode="heating",
        calculator_id="iso16358",
        config_path="data/region_configs/hong_kong.json",
        enabled=True,
    ),
    CalculatorProfile(
        profile_id="saso_t3_cspf",
        standard="ISO_16358",
        region="saso",
        metric="CSPF",
        mode="cooling",
        calculator_id="iso16358",
        config_path="data/region_configs/saso.json",
        enabled=True,
    ),
    CalculatorProfile(
        profile_id="asnzs_excel_hspf_compat",
        standard="ASNZS",
        region="au_nz",
        metric="HSPF",
        mode="heating",
        calculator_id="asnzs_excel_hspf",
        config_path="tests/fixtures/asnzs_excel_hspf_compat/workbook_inverter_ac_current.json",
        enabled=False,
    ),
)


def _same(value: str, expected: Optional[str]) -> bool:
    if expected is None:
        return True
    return value.casefold() == expected.casefold()


def list_calculator_profiles(enabled_only: bool = True) -> Tuple[CalculatorProfile, ...]:
    if not enabled_only:
        return _CALCULATOR_PROFILES
    return tuple(profile for profile in _CALCULATOR_PROFILES if profile.enabled)


def resolve_calculator_profile(
    profile_id: Optional[str] = None,
    standard: Optional[str] = None,
    region: Optional[str] = None,
    metric: Optional[str] = None,
    mode: Optional[str] = None,
) -> CalculatorProfile:
    profiles = list_calculator_profiles(enabled_only=True)

    if profile_id is not None:
        matches = [profile for profile in profiles if _same(profile.profile_id, profile_id)]
    else:
        matches = [
            profile
            for profile in profiles
            if _same(profile.standard, standard)
            and _same(profile.region, region)
            and _same(profile.metric, metric)
            and _same(profile.mode, mode)
        ]

    if len(matches) != 1:
        selector = {
            "profile_id": profile_id,
            "standard": standard,
            "region": region,
            "metric": metric,
            "mode": mode,
        }
        raise ValueError(
            "Calculator profile selector must match exactly one enabled profile: "
            f"{selector}, matches={len(matches)}"
        )

    return matches[0]
