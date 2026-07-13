from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from core.calculators.standards.ahri_hspf2 import AHRIHSPF2Calculator
from core.calculators.standards._ahri.hspf2_points import (
    VARIABLE_OPTIONAL_POINTS,
    VARIABLE_POINT_KEYS,
    VARIABLE_REQUIRED_POINTS,
)
from core.calculators.standards.iso16358 import ISO16358Calculator
from core.calculators.standards.ks_c9306 import KSC9306Calculator


ROOT = Path(__file__).resolve().parents[2]
REGIONS = ROOT / "data" / "region_configs"


def _write_config(tmp_path: Path, source: str, mutate) -> str:
    config = json.loads((REGIONS / source).read_text(encoding="utf-8"))
    mutate(config)
    path = tmp_path / source
    path.write_text(json.dumps(config), encoding="utf-8")
    return str(path)


@pytest.mark.parametrize("profile", [None, "unknown", "ks_c_9306_hspf"])
def test_iso_hspf_rejects_missing_unknown_and_compatibility_profiles(
    tmp_path: Path, profile: str | None
) -> None:
    def mutate(config: dict) -> None:
        if profile is None:
            config.pop("hspf", None)
        else:
            config.setdefault("hspf", {})["profile"] = profile

    calculator = ISO16358Calculator(
        _write_config(tmp_path, "hong_kong.json", mutate)
    )
    with pytest.raises(ValueError, match=repr(profile)):
        calculator.calculate_hspf(
            {
                "7_full": {"capacity": 6300, "power": 1500},
                "7_half": {"capacity": 3200, "power": 800},
            }
        )


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("climate_profile", "T2"),
        ("climate_profile", ""),
        ("climate_profile", None),
        ("test_selection", "optional"),
        ("test_selection", ""),
        ("test_selection", None),
    ],
)
def test_iso_cspf_profile_selectors_are_strict(
    tmp_path: Path, field: str, value: str | None
) -> None:
    def mutate(config: dict) -> None:
        profile = config["cspf_test_profile"]
        if value is None:
            profile.pop(field)
        else:
            profile[field] = value

    calculator = ISO16358Calculator(_write_config(tmp_path, "saso.json", mutate))
    with pytest.raises(ValueError, match=field):
        calculator.calculate_cspf({})


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("building_load_source", "automatic"),
        ("building_load_source", ""),
        ("building_load_source", None),
        ("power_interpolation_method", "linear"),
        ("power_interpolation_method", ""),
        ("power_interpolation_method", None),
    ],
)
def test_iso_flat_config_selectors_reject_explicit_invalid_values(
    tmp_path: Path, field: str, value: str | None
) -> None:
    def mutate(config: dict) -> None:
        config[field] = value

    with pytest.raises(ValueError, match=field):
        ISO16358Calculator(
            _write_config(tmp_path, "iso_t1_default_2point.json", mutate)
        )


def test_iso_flat_config_selector_defaults_remain_supported(tmp_path: Path) -> None:
    def mutate(config: dict) -> None:
        config.pop("building_load_source", None)
        config.pop("power_interpolation_method", None)

    calculator = ISO16358Calculator(
        _write_config(tmp_path, "iso_t1_default_2point.json", mutate)
    )
    assert calculator.building_load_source == "measured"
    assert calculator.power_interpolation_method == "capacity_linear"


def test_iso_facade_selector_reassignment_uses_context_validation() -> None:
    calculator = ISO16358Calculator(
        str(REGIONS / "iso_t1_default_2point.json")
    )
    calculator.building_load_source = "declared"
    calculator.power_interpolation_method = "capacity_linear"
    assert calculator._context.building_load_source == "declared"
    assert calculator._context.power_interpolation_method == "capacity_linear"

    for field, invalid in (
        ("building_load_source", "unknown"),
        ("building_load_source", ""),
        ("building_load_source", None),
        ("building_load_source", 1),
        ("power_interpolation_method", "unknown"),
        ("power_interpolation_method", ""),
        ("power_interpolation_method", None),
        ("power_interpolation_method", 1),
    ):
        with pytest.raises(ValueError, match=field):
            setattr(calculator, field, invalid)


def test_ks_rejects_iso_cspf_profile_schema() -> None:
    config = json.loads((REGIONS / "korea.json").read_text(encoding="utf-8"))
    config["cspf_test_profile"] = {
        "climate_profile": "T1",
        "test_selection": "required_only",
    }
    with pytest.raises(ValueError, match="does not support ISO cspf_test_profile"):
        KSC9306Calculator(config).calculate_cspf({})


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("points", None, "points"),
        ("points", {}, "points"),
        ("points", [], "points"),
        ("derived_rules", [], "derived_rules"),
        ("building_load_source", "automatic", "building_load_source"),
        ("power_interpolation_method", "capacity_linear", "power_interpolation_method"),
    ],
)
def test_ks_cspf_rejects_missing_schema_and_unknown_selectors(
    field: str, value, message: str
) -> None:
    config = json.loads((REGIONS / "korea.json").read_text(encoding="utf-8"))
    if value is None:
        config.pop(field, None)
    else:
        config[field] = value
    with pytest.raises(ValueError, match=message):
        KSC9306Calculator(config).calculate_cspf({})


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("capacity_factor", None),
        ("power_factor", None),
        ("capacity_factor", "typo"),
        ("power_factor", True),
        ("capacity_factor", float("nan")),
        ("power_factor", float("inf")),
        ("capacity_factor", 0),
        ("power_factor", -1),
    ],
)
def test_ks_cspf_rejects_invalid_derived_factors(field: str, value) -> None:
    config = json.loads((REGIONS / "korea.json").read_text(encoding="utf-8"))
    rule = config["derived_rules"]["35_min"]
    if value is None:
        rule.pop(field)
    else:
        rule[field] = value
    with pytest.raises(ValueError, match=field):
        KSC9306Calculator(config).calculate_cspf({})


def test_ks_cspf_rejects_self_reference_and_unresolved_cycle() -> None:
    config = json.loads((REGIONS / "korea.json").read_text(encoding="utf-8"))
    config["derived_rules"]["35_min"]["source"] = "35_min"
    with pytest.raises(ValueError, match="source"):
        KSC9306Calculator(config).calculate_cspf({})

    config = json.loads((REGIONS / "korea.json").read_text(encoding="utf-8"))
    config["derived_rules"]["35_min"]["source"] = "29_full"
    config["derived_rules"]["29_full"]["source"] = "35_min"
    measured = {
        "35_full": {"capacity": 6035.8, "power": 1641.4},
        "35_half": {"capacity": 3420.4, "power": 679.4},
        "29_min": {"capacity": 1759.6, "power": 201.7},
    }
    with pytest.raises(ValueError, match="unresolved|default"):
        KSC9306Calculator(config).calculate_cspf(measured, 6000)


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (lambda config: config.pop("hspf"), "hspf"),
        (lambda config: config["hspf"].update(profile="unknown"), "profile"),
        (lambda config: config["hspf"].pop("required_points"), "required_points"),
        (lambda config: config["hspf"].update(required_points={}), "required_points"),
        (lambda config: config["hspf"].pop("bin_hours_key"), "bin_hours_key"),
        (lambda config: config["hspf"].update(bin_hours_key="missing_bins"), "missing_bins"),
        (
            lambda config: config["hspf"]["load_line"].update(source="unknown"),
            "rated_cooling_capacity",
        ),
    ],
)
def test_ks_hspf_rejects_invalid_profile_and_required_schema(
    mutation, message: str
) -> None:
    config = json.loads((REGIONS / "korea.json").read_text(encoding="utf-8"))
    mutation(config)
    with pytest.raises(ValueError, match=message):
        KSC9306Calculator(config).calculate_hspf({})


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (lambda rows: rows.__setitem__(0, []), r"\[0\].*dict"),
        (lambda rows: rows[0].pop("tj"), r"\[0\].*tj"),
        (lambda rows: rows[0].pop("nj"), r"\[0\].*nj"),
        (lambda rows: rows[0].update(tj=True), r"\[0\].tj"),
        (lambda rows: rows[0].update(tj=float("nan")), r"\[0\].tj"),
        (lambda rows: rows[0].update(nj=True), r"\[0\].nj"),
        (lambda rows: rows[0].update(nj=float("inf")), r"\[0\].nj"),
        (lambda rows: rows[0].update(nj=-1), r"\[0\].nj"),
        (lambda rows: rows[1].update(tj=rows[0]["tj"]), "duplicate tj"),
    ],
)
def test_ks_hspf_rejects_malformed_bin_rows(mutation, message: str) -> None:
    config = json.loads((REGIONS / "korea.json").read_text(encoding="utf-8"))
    rows = config[config["hspf"]["bin_hours_key"]]
    mutation(rows)
    with pytest.raises(ValueError, match=message):
        KSC9306Calculator(config).calculate_hspf({})


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("zero_load_temp", True),
        ("full_load_temp", "zero"),
        ("rated_capacity_factor", float("nan")),
        ("rated_capacity_factor", float("inf")),
        ("rated_capacity_factor", 0),
        ("rated_capacity_factor", -0.1),
    ],
)
def test_ks_hspf_rejects_invalid_config_load_line_numbers(
    field: str, value
) -> None:
    config = json.loads((REGIONS / "korea.json").read_text(encoding="utf-8"))
    config["hspf"]["load_line"][field] = value
    explicit_user_line = {
        "ks_c_9306_hspf": {"load_line": {"slope": -1, "intercept": 10}}
    }
    with pytest.raises(ValueError, match=field):
        KSC9306Calculator(config).calculate_hspf(explicit_user_line)


def test_ks_hspf_rejects_equal_config_load_line_temperatures() -> None:
    config = json.loads((REGIONS / "korea.json").read_text(encoding="utf-8"))
    load_line = config["hspf"]["load_line"]
    load_line["full_load_temp"] = load_line["zero_load_temp"]
    with pytest.raises(ValueError, match="must differ"):
        KSC9306Calculator(config).calculate_hspf(
            {"ks_c_9306_hspf": {"load_line": {"slope": -1, "intercept": 10}}}
        )


def test_ahri_active_alias_allowlist_and_retired_aliases() -> None:
    calculator = AHRIHSPF2Calculator(str(REGIONS / "usa_hspf2.json"))
    assert calculator.test_point_aliases == {
        "public_to_canonical": {"A_Full": "A2"}
    }
    assert calculator.normalize_public_test_points(
        {"a_full": (24000, 2500)}
    ) == {"A2": (24000, 2500)}
    for retired in (
        "H2V", "B2", "C2", "D2", "E2", "H1_Full", "H2_Full",
        "H3_Full", "H21", "AFull", "H12x", "H22x", "unrelated",
    ):
        with pytest.raises(ValueError, match=retired):
            calculator.normalize_public_test_points({retired: (1, 1)})


def test_ahri_variable_allowlist_is_exact_and_distinct_from_full_schema() -> None:
    calculator = AHRIHSPF2Calculator(str(REGIONS / "usa_hspf2.json"))
    assert VARIABLE_REQUIRED_POINTS == {
        "H01", "H11", "H1N", "H2Int", "H32", "A2"
    }
    assert VARIABLE_OPTIONAL_POINTS == {"H12", "H22", "H42"}
    assert VARIABLE_POINT_KEYS == {
        "H01", "H11", "H1N", "H2Int", "H32", "A2",
        "H12", "H22", "H42",
    }
    assert {"H2V", "B2", "C2", "D2", "E2"} <= (
        calculator._point_resolver.schema_keys() - VARIABLE_POINT_KEYS
    )


def _ahri_required_variable_points() -> dict:
    return {
        "H01": (12500, 980),
        "H11": (12000, 1000),
        "H1N": (22000, 2000),
        "H2Int": (13000, 1200),
        "H32": (22000, 2100),
        "A2": (24000, 2500),
    }


@pytest.mark.parametrize(
    "unsupported",
    [
        "H2V", "B2", "C2", "D2", "E2", "H1_Full", "H2_Full",
        "H12x", "H22x", "unrelated", 7,
    ],
)
def test_ahri_variable_calculation_rejects_unsupported_point_before_fallback(
    unsupported,
) -> None:
    calculator = AHRIHSPF2Calculator(str(REGIONS / "usa_hspf2.json"))
    points = _ahri_required_variable_points()
    points[unsupported] = (1, 1)
    with pytest.raises(
        ValueError,
        match="variable-capacity test point key",
    ):
        calculator.calculate_hspf2_v3(
            points,
            defrost_t_test_minutes=90,
            defrost_t_max_minutes=720,
        )


def test_ahri_required_only_points_keep_h12_h22_standard_fallbacks() -> None:
    calculator = AHRIHSPF2Calculator(str(REGIONS / "usa_hspf2.json"))
    result = calculator.calculate_hspf2_v3(
        _ahri_required_variable_points(),
        defrost_t_test_minutes=90,
        defrost_t_max_minutes=720,
    )
    assert result["summary"]["metadata"]["h12_source"] == "eq_11_185"
    assert result["summary"]["metadata"]["h22_source"] == "eq_11_44_11_50"


def test_ahri_all_optional_variable_points_are_accepted() -> None:
    calculator = AHRIHSPF2Calculator(str(REGIONS / "usa_hspf2.json"))
    points = {
        **_ahri_required_variable_points(),
        "H12": (24000, 2200),
        "H22": (23200, 2160),
        "H42": (18000, 1900),
    }
    normalized = calculator.normalize_public_test_points(points)
    assert set(normalized) == VARIABLE_POINT_KEYS


def test_ahri_canonical_point_keys_remain_case_insensitive() -> None:
    calculator = AHRIHSPF2Calculator(str(REGIONS / "usa_hspf2.json"))
    assert calculator.normalize_public_test_points(
        {"h01": (12500, 980), "h2int": (13000, 1200)}
    ) == {"H01": (12500, 980), "H2Int": (13000, 1200)}


@pytest.mark.parametrize("field", ["unit_type", "system_type"])
@pytest.mark.parametrize("value", ["unknown", "", None, 7])
def test_ahri_explicit_invalid_unit_type_fails_fast(field: str, value) -> None:
    calculator = AHRIHSPF2Calculator(str(REGIONS / "usa_hspf2.json"))
    points = {
        "H01": (12500, 980),
        "H11": (12000, 1000),
        "H1N": (22000, 2000),
        "H2Int": (13000, 1200),
        "H32": (22000, 2100),
        "A2": (24000, 2500),
    }
    with pytest.raises(ValueError, match=field):
        calculator._point_resolver.resolve_variable_capacity(
            points, {field: value}
        )


def test_ahri_conflicting_unit_type_aliases_fail_fast() -> None:
    calculator = AHRIHSPF2Calculator(str(REGIONS / "usa_hspf2.json"))
    points = {
        "H01": (12500, 980),
        "H11": (12000, 1000),
        "H1N": (22000, 2000),
        "H2Int": (13000, 1200),
        "H32": (22000, 2100),
        "A2": (24000, 2500),
    }
    with pytest.raises(ValueError, match="Conflicting.*unit_type.*system_type"):
        calculator._point_resolver.resolve_variable_capacity(
            points, {"unit_type": "split", "system_type": "packaged"}
        )


def test_retired_owner_modules_and_facade_surface_are_absent() -> None:
    iso_private = ROOT / "core/calculators/standards/_iso16358"
    ahri_private = ROOT / "core/calculators/standards/_ahri"
    assert not (iso_private / "hspf_legacy_engine.py").exists()
    assert not (iso_private / "hspf_legacy_points.py").exists()
    assert not (ahri_private / "hspf2_legacy.py").exists()

    calculator = AHRIHSPF2Calculator(str(REGIONS / "usa_hspf2.json"))
    assert not hasattr(calculator, "calculate_hspf2_v2")
    assert not hasattr(calculator, "canonical_to_internal_usage")
    for retired in ("bin_temps", "bin_hours", "test_point_temps", "constants"):
        assert not hasattr(calculator, retired)
    assert set(calculator.config).isdisjoint(
        {"bin_data", "test_point_temps", "constants"}
    )
    assert set(calculator._context.__dict__).isdisjoint(
        {"bin_temps", "bin_hours", "test_point_temps", "constants"}
    )
    assert set(calculator.__dict__) >= {
        "_variable_engine",
        "_dual_engine",
        "_triple_engine",
    }

    from core.calculators.standards._iso16358.engines import ISO16358HSPFEngine

    assert [base.__name__ for base in ISO16358HSPFEngine.__bases__] == [
        "ISOEngineContext",
        "ISOInputPreparationMixin",
        "HSPFCommonCurveMixin",
        "HSPFExtendedPerformanceMixin",
        "HSPFCommonPointMixin",
        "HSPFLoadContextMixin",
        "HSPFPerformanceSnapshotMixin",
        "HSPFCaseEngineMixin",
        "HSPFSeasonalMixin",
    ]


def test_application_and_capability_do_not_import_private_standard_owners() -> None:
    roots = [ROOT / "apps", ROOT / "core/calculators/capability"]
    violations = []
    for root in roots:
        for path in root.rglob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                module = ""
                if isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                elif isinstance(node, ast.Import):
                    module = " ".join(alias.name for alias in node.names)
                if ".standards._" in module:
                    violations.append(str(path.relative_to(ROOT)))
    assert violations == []


def test_ks_private_owner_has_no_iso_selector_calculation_branches() -> None:
    private_root = ROOT / "core/calculators/standards/_ks_c9306"
    for path in private_root.glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        compared_literals = {
            node.value
            for node in ast.walk(tree)
            if isinstance(node, ast.Constant) and isinstance(node.value, str)
        }
        assert "T1" not in compared_literals
        assert "T3" not in compared_literals
        assert "with_optional_test" not in compared_literals
