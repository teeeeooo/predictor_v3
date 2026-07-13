"""KS C 9306 CSPF measured and derived point resolution."""

import math


class KSCSPFPointResolverMixin:
    def _validate_ks_cspf_config(self) -> None:
        if "cspf_test_profile" in self.config:
            raise ValueError(
                "KS C 9306 does not support ISO cspf_test_profile configuration."
            )
        points = self.config.get("points")
        if not isinstance(points, dict) or not points:
            raise ValueError("Invalid KS C 9306 CSPF points: non-empty dict required.")
        invalid_types = {
            key: value
            for key, value in points.items()
            if value not in {"measure", "default"}
        }
        if invalid_types:
            raise ValueError(
                f"Invalid KS C 9306 CSPF points schema: {invalid_types!r}"
            )
        derived_rules = self.config.get("derived_rules")
        if not isinstance(derived_rules, dict):
            raise ValueError("Invalid KS C 9306 CSPF derived_rules: dict required.")
        for point, point_type in points.items():
            if point_type != "default":
                continue
            rule = derived_rules.get(point)
            if not isinstance(rule, dict):
                raise ValueError(
                    f"Invalid KS C 9306 CSPF derived_rules for {point!r}."
                )
            missing = {
                "source", "capacity_factor", "power_factor"
            } - rule.keys()
            if missing:
                raise ValueError(
                    f"Invalid KS C 9306 CSPF derived_rules for {point!r}: "
                    f"missing {sorted(missing)}."
                )
            source = rule["source"]
            if source not in points or source == point:
                raise ValueError(
                    f"Invalid KS C 9306 CSPF derived_rules source for {point!r}: "
                    f"{source!r}."
                )
            for factor_field in ("capacity_factor", "power_factor"):
                factor = rule[factor_field]
                if (
                    isinstance(factor, bool)
                    or not isinstance(factor, (int, float))
                    or not math.isfinite(factor)
                    or factor <= 0
                ):
                    raise ValueError(
                        f"Invalid KS C 9306 CSPF {point}.{factor_field}: "
                        "finite positive number required."
                    )
        building_load_source = self.config.get("building_load_source")
        if building_load_source not in {"declared", "measured"}:
            raise ValueError(
                "Unsupported KS C 9306 CSPF building_load_source: "
                f"{building_load_source!r}"
            )
        interpolation = self.config.get("power_interpolation_method")
        if interpolation != "ks_intersection":
            raise ValueError(
                "Unsupported KS C 9306 CSPF power_interpolation_method: "
                f"{interpolation!r}"
            )

    def _resolve_ks_cspf_points(self, measured_inputs: dict) -> dict:
        """KS CSPF용 point resolution.

        ISO ``cspf_test_profile`` schema는 fail-fast한다. KS의
        ``points`` + ``derived_rules``만 measure/default 검증과 연쇄 파생
        규칙을 KS module 안에서 수행한다.
        """
        self._validate_ks_cspf_config()
        points_config = self.config["points"]
        derived_rules = self.config["derived_rules"]

        resolved = {}
        for point_key, point_type in points_config.items():
            if point_type != "measure":
                continue
            if point_key not in measured_inputs:
                raise ValueError(
                    f"필수 측정값 누락: '{point_key}' 포인트 데이터가 없습니다."
                )
            point_data = measured_inputs[point_key]
            if not isinstance(point_data, dict):
                raise ValueError(
                    f"Invalid measured point '{point_key}': expected dict with capacity and power."
                )
            for required_key in ("capacity", "power"):
                if required_key not in point_data:
                    raise ValueError(
                        f"Invalid measured point '{point_key}': "
                        f"missing required field '{required_key}'."
                    )

            validated = dict(point_data)
            for numeric_key in ("capacity", "power"):
                try:
                    numeric_value = float(point_data[numeric_key])
                except (TypeError, ValueError):
                    raise ValueError(
                        f"Invalid measured point '{point_key}': {numeric_key} must be numeric."
                    ) from None
                if numeric_value <= 0:
                    raise ValueError(
                        f"Invalid measured point '{point_key}': {numeric_key} must be positive."
                    )
                validated[numeric_key] = numeric_value
            resolved[point_key] = validated

        round_values = bool(self.config.get("round_test_values", False))
        for _ in range(len(points_config)):
            for point_key, point_type in points_config.items():
                if point_type != "default" or point_key in resolved:
                    continue
                rule = derived_rules.get(point_key)
                if not rule:
                    continue
                source_key = rule.get("source")
                if source_key not in resolved:
                    continue
                source_data = resolved[source_key]
                cap_factor = rule["capacity_factor"]
                pow_factor = rule["power_factor"]
                derived = {
                    "capacity": source_data["capacity"] * cap_factor,
                    "power": source_data["power"] * pow_factor,
                }
                if round_values:
                    derived["capacity"] = self._round_test_value(derived["capacity"])
                    derived["power"] = self._round_test_value(derived["power"])
                resolved[point_key] = derived

        unresolved = [
            k for k, t in points_config.items()
            if t == "default" and k not in resolved
        ]
        if unresolved:
            raise ValueError(
                f"해결되지 않은 default 포인트: {unresolved}. "
                "순환 참조 또는 source 누락을 확인하세요."
            )

        return resolved
