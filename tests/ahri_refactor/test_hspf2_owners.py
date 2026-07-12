import pytest

from core.calculators.standards.ahri_hspf2 import AHRIHSPF2Calculator
from core.calculators.standards._ahri.hspf2_context import HSPF2ConfigContext
from core.calculators.standards._ahri.hspf2_points import HSPF2PointResolver

from .test_contract_lock import HSPF2_CONFIG_PATH, HSPF2_V3_KWARGS, HSPF2_V3_POINTS


def _owners():
    context = HSPF2ConfigContext(HSPF2_CONFIG_PATH)
    resolver = HSPF2PointResolver(context.test_point_schema, context.test_point_aliases)
    return context, resolver


def test_hspf2_context_preserves_loaded_state_and_region_iv_values():
    context, _ = _owners()
    seasonal = context.seasonal_context(HSPF2_V3_KWARGS)

    assert context.defaults["t_off"] == -40.0
    assert context.defaults["t_on"] == -40.0
    assert context.defaults["fdef_override"] == 1.0
    assert seasonal.bin_table is context.canonical_hspf2_bin_tables["heating"]["region_iv"]
    assert seasonal.heating_load_hours == 1701
    assert seasonal.bin_hours == [
        fraction * seasonal.heating_load_hours
        for fraction in seasonal.fractional_bin_hours
    ]


def test_hspf2_point_owner_preserves_aliases_and_fallback_sources():
    _, resolver = _owners()
    canonical = resolver.legacy_to_canonical(
        {**HSPF2_V3_POINTS, "A_Full": HSPF2_V3_POINTS["A_Full"]}
    )
    canonical.pop("H12")
    canonical.pop("H22")
    resolved = resolver.resolve_variable_capacity(canonical, HSPF2_V3_KWARGS)

    assert canonical["A2"] == HSPF2_V3_POINTS["A_Full"]
    assert resolved.h12_source == "eq_11_185"
    assert resolved.h22_source == "eq_11_44_11_50"
    assert resolved.h22_high_anchor_source == "h1full_calc"
    assert resolved.h42_source == "provided"


def test_hspf2_point_owner_preserves_case_insensitive_conflict_detection():
    _, resolver = _owners()

    with pytest.raises(ValueError, match="Conflicting test point values for canonical key H12"):
        resolver.legacy_to_canonical({"H12": (24000, 2200), "h1_full": (23000, 2100)})


def test_hspf2_facade_delegates_v3_to_variable_capacity_engine():
    calculator = AHRIHSPF2Calculator(HSPF2_CONFIG_PATH)

    direct = calculator._variable_engine.calculate(HSPF2_V3_POINTS, **HSPF2_V3_KWARGS)
    through_facade = calculator.calculate_hspf2_v3(HSPF2_V3_POINTS, **HSPF2_V3_KWARGS)

    assert through_facade == direct


def test_hspf2_facade_delegates_v2_to_legacy_engine():
    calculator = AHRIHSPF2Calculator(HSPF2_CONFIG_PATH)
    points = {
        "H1_Full": (24000, 2200),
        "H2_Full": (22000, 2100),
        "H3_Full": (18000, 1900),
    }

    assert calculator.calculate_hspf2_v2(points) == calculator._legacy_engine.calculate(points)
