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


def test_ks_rejects_iso_cspf_profile_schema() -> None:
    config = json.loads((REGIONS / "korea.json").read_text(encoding="utf-8"))
    config["cspf_test_profile"] = {
        "climate_profile": "T1",
        "test_selection": "required_only",
    }
    with pytest.raises(ValueError, match="does not support ISO cspf_test_profile"):
        KSC9306Calculator(config).calculate_cspf({})


def test_retired_owner_modules_and_facade_surface_are_absent() -> None:
    iso_private = ROOT / "core/calculators/standards/_iso16358"
    ahri_private = ROOT / "core/calculators/standards/_ahri"
    assert not (iso_private / "hspf_legacy_engine.py").exists()
    assert not (iso_private / "hspf_legacy_points.py").exists()
    assert not (ahri_private / "hspf2_legacy.py").exists()

    calculator = AHRIHSPF2Calculator(str(REGIONS / "usa_hspf2.json"))
    assert not hasattr(calculator, "calculate_hspf2_v2")
    assert not hasattr(calculator, "canonical_to_internal_usage")

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
