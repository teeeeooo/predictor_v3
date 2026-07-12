"""ISO 16358-1 CSPF profile and point resolution."""


class CSPFPointResolverMixin:
    _CSPF_CLIMATES = frozenset({"T1", "T3"})
    _CSPF_TEST_SELECTIONS = frozenset(
        {"required_only", "with_optional_test"}
    )

    def _has_cspf_test_profile(self) -> bool:
        return "cspf_test_profile" in self.config

    def _validated_cspf_test_profile(self) -> dict:
        profile = self.config.get("cspf_test_profile")
        if not isinstance(profile, dict):
            raise ValueError("cspf_test_profile must be a configuration object.")
        climate = profile.get("climate_profile")
        selection = profile.get("test_selection")
        if climate not in self._CSPF_CLIMATES:
            raise ValueError(
                f"Unsupported ISO CSPF climate_profile: {climate!r}; "
                f"supported={sorted(self._CSPF_CLIMATES)}"
            )
        if selection not in self._CSPF_TEST_SELECTIONS:
            raise ValueError(
                f"Unsupported ISO CSPF test_selection: {selection!r}; "
                f"supported={sorted(self._CSPF_TEST_SELECTIONS)}"
            )
        return profile

    def _get_cspf_profile_cd(self) -> float:
        if "Cd" in self.config:
            return float(self.config["Cd"])
        profile = self._validated_cspf_test_profile()["climate_profile"]
        return 0.27 if profile == "T3" else 0.25

    def _get_active_load_levels(self) -> list:
        profile_cfg = self._validated_cspf_test_profile()
        selection = profile_cfg.get("test_selection")
        if selection == "with_optional_test":
            return ["full", "half", "min"]
        return ["full", "half"]

    def _get_cspf_temperature_segments(self) -> list:
        profile = self._validated_cspf_test_profile()["climate_profile"]
        if profile == "T3":
            return [{"boundary": 35.0, "high": [46, 35], "low": [35, 29]}]
        return [{"boundary": None, "high": [35, 29]}]

    def _resolve_cspf_profile_points(self, measured: dict) -> dict:
        profile_cfg = self._validated_cspf_test_profile()
        climate = profile_cfg.get("climate_profile")
        selection = profile_cfg.get("test_selection")

        resolved = {k: dict(v) if isinstance(v, dict) else v for k, v in measured.items()}

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

    def resolve_points(self, measured_inputs: dict) -> dict:
        if self._has_cspf_test_profile():
            return self._resolve_cspf_profile_points(measured_inputs)

        resolved = {}
        for point_key, point_type in self.points_config.items():
            if point_type != "measure":
                continue
            if point_key not in measured_inputs:
                raise ValueError(f"필수 측정값 누락: '{point_key}' 포인트 데이터가 없습니다.")

            point_data = measured_inputs[point_key]
            if not isinstance(point_data, dict):
                raise ValueError(
                    f"Invalid measured point '{point_key}': expected dict with capacity and power."
                )

            validated_point = dict(point_data)
            for numeric_key in ("capacity", "power"):
                if numeric_key not in point_data:
                    raise ValueError(
                        f"Invalid measured point '{point_key}': "
                        f"missing required field '{numeric_key}'."
                    )
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
                validated_point[numeric_key] = numeric_value
            resolved[point_key] = validated_point

        for _ in range(len(self.points_config)):
            for point_key, point_type in self.points_config.items():
                if point_type != "default" or point_key in resolved:
                    continue
                rule = self.derived_rules.get(point_key)
                if not rule:
                    continue
                source_key = rule.get("source")
                if source_key not in resolved:
                    continue
                source_data = resolved[source_key]
                resolved[point_key] = {
                    "capacity": source_data["capacity"] * rule.get("capacity_factor", 1.0),
                    "power": source_data["power"] * rule.get("power_factor", 1.0),
                }

        unresolved = [
            k for k, t in self.points_config.items()
            if t == "default" and k not in resolved
        ]
        if unresolved:
            raise ValueError(
                f"해결되지 않은 default 포인트: {unresolved}. 순환 참조 또는 source 누락을 확인하세요."
            )

        return resolved
