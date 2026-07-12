from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from core.calculators.standards.ahri_hspf2 import AHRIHSPF2Calculator
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


def test_ahri_active_alias_allowlist_and_retired_aliases() -> None:
    calculator = AHRIHSPF2Calculator(str(REGIONS / "usa_hspf2.json"))
    assert calculator.test_point_aliases == {
        "public_to_canonical": {"A_Full": "A2"}
    }
    assert calculator.normalize_public_test_points(
        {"a_full": (24000, 2500)}
    ) == {"A2": (24000, 2500)}
    for retired in ("H1_Full", "H2_Full", "H3_Full", "H21", "AFull"):
        assert calculator.normalize_public_test_points({retired: (1, 1)}) == {
            retired: (1, 1)
        }


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
