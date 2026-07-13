"""HSPF2 test-point normalization, validation, and fallback resolution."""

from dataclasses import dataclass
from typing import Mapping, Optional


CapacityPower = tuple[float, float]
VARIABLE_REQUIRED_POINTS = frozenset(
    {"H01", "H11", "H1N", "H2Int", "H32", "A2"}
)
VARIABLE_OPTIONAL_POINTS = frozenset({"H12", "H22", "H42"})
VARIABLE_POINT_KEYS = VARIABLE_REQUIRED_POINTS | VARIABLE_OPTIONAL_POINTS


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

    def normalize_public_test_points(self, test_points: dict) -> dict:
        alias_map = self.test_point_aliases.get("public_to_canonical", {})
        canonical_points = {}
        for key, value in test_points.items():
            if not isinstance(key, str):
                raise ValueError(
                    "Unsupported AHRI HSPF2 variable-capacity test point key: "
                    f"{key!r}"
                )
            alias_key = self.match_key_case_insensitive(key, alias_map.keys())
            canonical_key = alias_map.get(alias_key, key)
            canonical_key = self.match_key_case_insensitive(
                canonical_key, VARIABLE_POINT_KEYS
            )
            if canonical_key not in VARIABLE_POINT_KEYS:
                raise ValueError(
                    f"Unsupported AHRI HSPF2 variable-capacity test point key: {key!r}"
                )
            if canonical_key in canonical_points and canonical_points[canonical_key] != value:
                raise ValueError(
                    f"Conflicting test point values for canonical key {canonical_key}: "
                    f"{canonical_points[canonical_key]} vs {value}"
                )
            canonical_points[canonical_key] = value
        return canonical_points

    def positive_point(self, test_points: dict, key: str) -> CapacityPower:
        capacity, power = self.get_point(test_points, key)
        if capacity <= 0 or power <= 0:
            raise ValueError(f"Invalid canonical test point {key}: capacity={capacity}, power={power}")
        return capacity, power

    @staticmethod
    def _normalize_unit_type(kwargs: dict) -> str:
        aliases = {
            "split": "split",
            "split_system": "split",
            "split-system": "split",
            "single_package": "single_package",
            "single-package": "single_package",
            "package": "single_package",
            "packaged": "single_package",
        }
        supplied = []
        for field in ("unit_type", "system_type"):
            if field not in kwargs:
                continue
            value = kwargs[field]
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"Unsupported AHRI HSPF2 {field}: {value!r}")
            normalized = aliases.get(value.strip().lower())
            if normalized is None:
                raise ValueError(f"Unsupported AHRI HSPF2 {field}: {value!r}")
            supplied.append((field, normalized))
        if len({value for _, value in supplied}) > 1:
            raise ValueError(
                "Conflicting AHRI HSPF2 unit_type and system_type selectors."
            )
        return supplied[0][1] if supplied else "split"

    def _resolve_h12(self, canonical_points, full_points, h1_nom, kwargs):
        if "H12" in canonical_points:
            return self.positive_point(canonical_points, "H12"), "tested"
        if kwargs.get("h1n_same_speed_as_h3", False):
            return h1_nom, "eq_11_183"

        q_h3_full, p_h3_full = full_points["H32"]
        if q_h3_full == 0 or p_h3_full == 0:
            raise ValueError("Invalid H3Full for Eq.11.185/11.186 fallback")
        unit_type = self._normalize_unit_type(kwargs)
        csf = 0.0262 if unit_type == "single_package" else 0.0204
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
        missing = sorted(VARIABLE_REQUIRED_POINTS - canonical_points.keys())
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
