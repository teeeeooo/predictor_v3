"""KS C 9306 CSPF measured and derived point resolution."""


class KSCSPFPointResolverMixin:
    def _resolve_cspf_profile_points(self, measured: dict) -> dict:
        """KS CSPF용 cspf_test_profile 기반 derived point 생성.

        기존 KS 경로의 T1 / T3 derived point 규칙을 KS owner 내부에서
        유지한다. ``cspf_test_profile``이 config에 없으면 derived point를
        만들지 않고 입력의 shallow copy만 돌려준다.

        이미 존재하는 key는 overwrite하지 않으며, 입력 dict는 mutate하지
        않는다. point_data dict도 새 dict로 얕게 복사해 후속 KS resolution이
        호출자 dict에 영향을 주지 않도록 한다.
        """
        resolved = {}
        for point_key, point_data in measured.items():
            if isinstance(point_data, dict):
                resolved[point_key] = dict(point_data)
            else:
                resolved[point_key] = point_data

        profile_cfg = self.config.get("cspf_test_profile", {})
        climate = profile_cfg.get("climate_profile")
        selection = profile_cfg.get("test_selection")

        def _set_point(key, cap, pwr):
            if key not in resolved:
                resolved[key] = {"capacity": cap, "power": pwr}

        if climate == "T1":
            _set_point(
                "29_full",
                resolved["35_full"]["capacity"] * 1.077,
                resolved["35_full"]["power"] * 0.914,
            )
            _set_point(
                "29_half",
                resolved["35_half"]["capacity"] * 1.077,
                resolved["35_half"]["power"] * 0.914,
            )
            if selection == "with_optional_test":
                _set_point(
                    "29_min",
                    resolved["35_min"]["capacity"] * 1.077,
                    resolved["35_min"]["power"] * 0.914,
                )
        elif climate == "T3":
            _set_point(
                "46_half",
                resolved["35_half"]["capacity"] * 0.859,
                resolved["35_half"]["power"] * 1.25,
            )
            _set_point(
                "29_full",
                resolved["35_full"]["capacity"] * 1.077,
                resolved["35_full"]["power"] * 0.914,
            )
            _set_point(
                "29_half",
                resolved["35_half"]["capacity"] * 1.077,
                resolved["35_half"]["power"] * 0.914,
            )
            if selection == "with_optional_test":
                _set_point(
                    "46_min",
                    resolved["35_min"]["capacity"] * 0.859,
                    resolved["35_min"]["power"] * 1.25,
                )
                _set_point(
                    "29_min",
                    resolved["35_min"]["capacity"] * 1.077,
                    resolved["35_min"]["power"] * 0.914,
                )

        return resolved

    def _resolve_ks_cspf_points(self, measured_inputs: dict) -> dict:
        """KS CSPF용 point resolution.

        ``cspf_test_profile``이 config에 있으면 T1/T3 derived point만 채우는
        ``_resolve_cspf_profile_points``를 사용한다. 그 외(Korea처럼
        ``points`` + ``derived_rules`` 기반)이면 measure/default 검증과 연쇄
        파생 규칙을 KS module 안에서 직접 수행한다.
        """
        if "cspf_test_profile" in self.config:
            return self._resolve_cspf_profile_points(measured_inputs)

        points_config = self.config.get("points", {})
        derived_rules = self.config.get("derived_rules", {})
        if not points_config:
            resolved = {}
            for key, value in measured_inputs.items():
                resolved[key] = dict(value) if isinstance(value, dict) else value
            return resolved

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
                cap_factor = rule.get("capacity_factor", 1.0)
                pow_factor = rule.get("power_factor", 1.0)
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
