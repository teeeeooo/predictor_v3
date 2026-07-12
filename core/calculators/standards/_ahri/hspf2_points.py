"""HSPF2 test-point normalization, validation, and fallback resolution."""

from dataclasses import dataclass
from typing import Mapping, Optional


CapacityPower = tuple[float, float]


@dataclass(frozen=True)
class ResolvedHSPF2Points:
    canonical_points: Mapping[str, CapacityPower]
    full_points: Mapping[str, CapacityPower]
    low_points: Mapping[str, CapacityPower]
    h1_nom: CapacityPower
    h2_int: CapacityPower
    h4_point: Optional[CapacityPower]
    q_a_full: float
    h12_source: str
    h22_source: str
    h42_source: str
    h22_tested: bool
    h22_for_slope_source: str
    h22_high_anchor_source: Optional[str]
    h22_high_anchor_capacity: Optional[float]
    h22_high_anchor_power: Optional[float]


class HSPF2PointResolver:
    """Resolve public point dictionaries into coherent engine anchors."""

    def __init__(self, test_point_schema: dict, test_point_aliases: dict):
        self.test_point_schema = test_point_schema
        self.test_point_aliases = test_point_aliases

    @staticmethod
    def get_point(test_points: dict, key: str) -> tuple:
        if key in test_points:
            return test_points[key]
        key_lower = key.lower()
        for candidate_key, value in test_points.items():
            if candidate_key.lower() == key_lower:
                return value
        raise ValueError(f"Missing test point: {key}")

    def schema_keys(self) -> set:
        keys = set()
        for mode_points in self.test_point_schema.values():
            if isinstance(mode_points, dict):
                keys.update(mode_points.keys())
        return keys

    @staticmethod
    def match_key_case_insensitive(key: str, candidates) -> str:
        if key in candidates:
            return key
        key_lower = key.lower()
        for candidate in candidates:
            if candidate.lower() == key_lower:
                return candidate
        return key

    def get_test_point_schema(self, mode: str = None) -> dict:
        if mode is None:
            return self.test_point_schema
        return self.test_point_schema.get(mode, {})

    def legacy_to_canonical(self, test_points: dict) -> dict:
        legacy_map = self.test_point_aliases.get("legacy_to_canonical", {})
        schema_keys = self.schema_keys()
        canonical_points = {}
        for key, value in test_points.items():
            legacy_key = self.match_key_case_insensitive(key, legacy_map.keys())
            canonical_key = legacy_map.get(legacy_key, key)
            canonical_key = self.match_key_case_insensitive(canonical_key, schema_keys)
            if canonical_key in canonical_points and canonical_points[canonical_key] != value:
                raise ValueError(
                    f"Conflicting test point values for canonical key {canonical_key}: "
                    f"{canonical_points[canonical_key]} vs {value}"
                )
            canonical_points[canonical_key] = value
        return canonical_points

    def canonical_to_internal_usage(self, test_points: dict) -> dict:
        canonical_points = self.legacy_to_canonical(test_points)
        internal_map = self.test_point_aliases.get("canonical_to_internal_hspf2_v2", {})
        internal_points = {}
        for key, value in canonical_points.items():
            canonical_key = self.match_key_case_insensitive(key, internal_map.keys())
            internal_key = internal_map.get(canonical_key, key)
            if internal_key in internal_points and internal_points[internal_key] != value:
                raise ValueError(
                    f"Conflicting test point values for internal key {internal_key}: "
                    f"{internal_points[internal_key]} vs {value}"
                )
            internal_points[internal_key] = value
        return internal_points

    def positive_point(self, test_points: dict, key: str) -> CapacityPower:
        capacity, power = self.get_point(test_points, key)
        if capacity <= 0 or power <= 0:
            raise ValueError(f"Invalid canonical test point {key}: capacity={capacity}, power={power}")
        return capacity, power

    def validate_legacy_full_load_points(self, test_points: dict) -> dict:
        points = {
            "H1_Full": self.get_point(test_points, "H1_Full"),
            "H2_Full": self.get_point(test_points, "H2_Full"),
            "H3_Full": self.get_point(test_points, "H3_Full"),
        }
        for key, (capacity, power) in points.items():
            if capacity <= 0 or power <= 0:
                raise ValueError(f"Invalid test point {key}: capacity={capacity}, power={power}")
        return points

    def _resolve_h12(self, canonical_points, full_points, h1_nom, kwargs):
        if "H12" in canonical_points:
            return self.positive_point(canonical_points, "H12"), "tested"
        if kwargs.get("h1n_same_speed_as_h3", False):
            return h1_nom, "eq_11_183"

        q_h3_full, p_h3_full = full_points["H32"]
        if q_h3_full == 0 or p_h3_full == 0:
            raise ValueError("Invalid H3Full for Eq.11.185/11.186 fallback")
        unit_type = kwargs.get("unit_type", kwargs.get("system_type", "split"))
        csf = 0.0262 if str(unit_type).lower() in (
            "single_package",
            "single-package",
            "package",
            "packaged",
        ) else 0.0204
        return (q_h3_full * (1 + 30 * csf), p_h3_full * (1 + 30 * 0.00455)), "eq_11_185"

    def _resolve_h22(self, canonical_points, full_points):
        if "H22" in canonical_points:
            return self.positive_point(canonical_points, "H22"), "tested", True, "tested", None, None, None

        q_h3_full, p_h3_full = full_points["H32"]
        q_h1_full_calc, p_h1_full_calc = full_points["H12"]
        return (
            (
                0.90 * (q_h3_full + 0.6 * (q_h1_full_calc - q_h3_full)),
                0.985 * (p_h3_full + 0.6 * (p_h1_full_calc - p_h3_full)),
            ),
            "eq_11_44_11_50",
            False,
            "eq_11_44_11_50",
            "h1full_calc",
            q_h1_full_calc,
            p_h1_full_calc,
        )

    def resolve_variable_capacity(self, canonical_points: dict, kwargs: dict) -> ResolvedHSPF2Points:
        required_points = ("H01", "H11", "H1N", "H2Int", "H32", "A2")
        missing = [key for key in required_points if key not in canonical_points]
        if missing:
            raise ValueError(
                "HSPF2 v3 AHRI path requires canonical AHRI test points: " + ", ".join(missing)
            )

        full_points = {"H32": self.positive_point(canonical_points, "H32")}
        h4_point = self.positive_point(canonical_points, "H42") if "H42" in canonical_points else None
        h42_source = "provided" if h4_point is not None else "not_provided"
        low_points = {
            "H01": self.positive_point(canonical_points, "H01"),
            "H11": self.positive_point(canonical_points, "H11"),
        }
        h1_nom = self.positive_point(canonical_points, "H1N")
        full_points["H12"], h12_source = self._resolve_h12(
            canonical_points, full_points, h1_nom, kwargs
        )
        (
            full_points["H22"],
            h22_source,
            h22_tested,
            h22_for_slope_source,
            h22_high_anchor_source,
            h22_high_anchor_capacity,
            h22_high_anchor_power,
        ) = self._resolve_h22(canonical_points, full_points)
        q_a_full, _ = self.positive_point(canonical_points, "A2")
        return ResolvedHSPF2Points(
            canonical_points=canonical_points,
            full_points=full_points,
            low_points=low_points,
            h1_nom=h1_nom,
            h2_int=self.positive_point(canonical_points, "H2Int"),
            h4_point=h4_point,
            q_a_full=q_a_full,
            h12_source=h12_source,
            h22_source=h22_source,
            h42_source=h42_source,
            h22_tested=h22_tested,
            h22_for_slope_source=h22_for_slope_source,
            h22_high_anchor_source=h22_high_anchor_source,
            h22_high_anchor_capacity=h22_high_anchor_capacity,
            h22_high_anchor_power=h22_high_anchor_power,
        )
