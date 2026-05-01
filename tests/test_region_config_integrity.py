import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGION_CONFIGS = [
    ROOT / "data/region_configs/korea.json",
    ROOT / "data/region_configs/iso_t1_default_2point.json",
]

ALLOWED_POWER_INTERPOLATION_METHODS = {
    "capacity_linear",
    "ks_intersection",
    "iso_boundary_eer",
}

REQUIRED_TOP_LEVEL_KEYS = {
    "region",
    "standard",
    "t_100_load",
    "reference_point",
    "t_0_load",
    "Cd",
    "building_load_source",
    "points",
    "derived_rules",
    "bin_hours",
}


def load_config(path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_region_configs_have_required_top_level_keys():
    for path in REGION_CONFIGS:
        config = load_config(path)

        missing = REQUIRED_TOP_LEVEL_KEYS - set(config)
        assert not missing, f"{path.name} missing top-level keys: {sorted(missing)}"


def test_region_config_bin_hours_are_valid():
    for path in REGION_CONFIGS:
        config = load_config(path)
        bin_hours = config["bin_hours"]

        assert bin_hours, f"{path.name} bin_hours must not be empty"
        for index, row in enumerate(bin_hours):
            assert "tj" in row, f"{path.name} bin_hours[{index}] missing tj"
            assert "nj" in row, f"{path.name} bin_hours[{index}] missing nj"
            assert isinstance(
                row["nj"], (int, float)
            ), f"{path.name} bin_hours[{index}].nj must be numeric"
            assert row["nj"] >= 0, f"{path.name} bin_hours[{index}].nj must be >= 0"


def test_region_config_points_and_derived_rules_are_consistent():
    for path in REGION_CONFIGS:
        config = load_config(path)
        points = config["points"]
        derived_rules = config["derived_rules"]

        assert isinstance(points, dict), f"{path.name} points must be an object"
        assert isinstance(
            derived_rules, dict
        ), f"{path.name} derived_rules must be an object"

        for point_name, point_kind in points.items():
            assert point_kind in {
                "measure",
                "default",
            }, f"{path.name} points.{point_name} has invalid kind {point_kind!r}"
            if point_kind == "default":
                assert (
                    point_name in derived_rules
                ), f"{path.name} default point {point_name} needs a derived rule"

        for rule_name, rule in derived_rules.items():
            assert (
                rule_name in points
            ), f"{path.name} derived rule {rule_name} is not declared in points"
            source = rule.get("source")
            assert source in points, (
                f"{path.name} derived rule {rule_name} source {source!r} "
                "is not declared in points"
            )
            assert rule.get("capacity_factor", 0) > 0, (
                f"{path.name} derived rule {rule_name} capacity_factor must be > 0"
            )
            assert rule.get("power_factor", 0) > 0, (
                f"{path.name} derived rule {rule_name} power_factor must be > 0"
            )


def test_region_config_power_interpolation_method_is_valid_when_present():
    for path in REGION_CONFIGS:
        config = load_config(path)
        method = config.get("power_interpolation_method")
        if method is not None:
            assert method in ALLOWED_POWER_INTERPOLATION_METHODS, (
                f"{path.name} has invalid power_interpolation_method {method!r}"
            )


def test_iso_t1_default_2point_bin_total_is_1817():
    config = load_config(ROOT / "data/region_configs/iso_t1_default_2point.json")
    total_hours = sum(row["nj"] for row in config["bin_hours"])

    assert total_hours == 1817
