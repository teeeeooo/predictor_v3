"""KS C 9306 HSPF point validation and fallback resolution."""


class KSHSPFPointResolverMixin:
    def _ks_hspf_input(self, measured_inputs: dict) -> dict:
        if "ks_c_9306_hspf" not in measured_inputs:
            raise ValueError("Missing ks_c_9306_hspf input.")
        hspf_input = measured_inputs["ks_c_9306_hspf"]
        if not isinstance(hspf_input, dict):
            raise ValueError("Invalid KS C 9306 HSPF ks_c_9306_hspf: must be dict.")
        return hspf_input

    def _ks_hspf_config(self) -> dict:
        hspf_config = self.config.get("hspf")
        if not isinstance(hspf_config, dict):
            raise ValueError("Invalid KS C 9306 HSPF hspf: dict required.")
        if hspf_config.get("profile") != "ks_c_9306_hspf":
            raise ValueError(
                "Unsupported KS C 9306 HSPF profile: "
                f"{hspf_config.get('profile')!r}"
            )
        return hspf_config

    def _validate_ks_hspf_config(self) -> dict:
        hspf_config = self._ks_hspf_config()
        required_points = hspf_config.get("required_points")
        if not isinstance(required_points, dict) or not required_points:
            raise ValueError(
                "Invalid KS C 9306 HSPF required_points: non-empty dict required."
            )
        for temp_key, point_names in required_points.items():
            if not isinstance(temp_key, str) or not isinstance(point_names, list) or not point_names:
                raise ValueError(
                    "Invalid KS C 9306 HSPF required_points schema."
                )
            for point_name in point_names:
                if not isinstance(point_name, str):
                    raise ValueError(
                        "Invalid KS C 9306 HSPF required_points schema."
                    )
                self._ks_hspf_profile_point_path(temp_key, point_name)

        bin_hours_key = hspf_config.get("bin_hours_key")
        if not isinstance(bin_hours_key, str) or not bin_hours_key:
            raise ValueError(
                "Invalid KS C 9306 HSPF bin_hours_key: non-empty string required."
            )
        bin_hours = self.config.get(bin_hours_key)
        if not isinstance(bin_hours, list) or not bin_hours:
            raise ValueError(
                f"Invalid KS C 9306 HSPF {bin_hours_key}: non-empty list required."
            )

        for field in ("derived_rules", "correction"):
            value = hspf_config.get(field)
            if value is not None and not isinstance(value, dict):
                raise ValueError(
                    f"Invalid KS C 9306 HSPF {field}: dict required."
                )

        load_line = hspf_config.get("load_line")
        if not isinstance(load_line, dict):
            raise ValueError("Invalid KS C 9306 HSPF load_line: dict required.")
        required_load_line = {
            "source",
            "zero_load_temp",
            "full_load_temp",
            "rated_capacity_factor",
        }
        if "source" not in load_line:
            raise ValueError(
                "Invalid KS C 9306 HSPF load_line: source is required."
            )
        missing = required_load_line - load_line.keys()
        if missing:
            raise ValueError(
                "Invalid KS C 9306 HSPF load_line: zero_load_temp, "
                "full_load_temp, and rated_capacity_factor are required."
            )
        if load_line["source"] != "rated_cooling_capacity":
            raise ValueError(
                "KS C 9306 HSPF requires rated_cooling_capacity, not "
                f"{load_line['source']!r}."
            )
        return hspf_config

    def _ks_hspf_profile_point_path(self, temp_key: str, point_name: str) -> tuple:
        stage_map = {
            "full": "rated",
            "rated": "rated",
            "half": "intermediate",
            "intermediate": "intermediate",
            "min": "min",
            "minimum": "min",
            "max": "max",
            "maximum": "max",
            "extended": "max",
        }
        if point_name == "defrost":
            return "max", "def"
        stage = stage_map.get(point_name)
        if stage is None:
            raise ValueError(f"Unsupported KS C 9306 HSPF profile point: {point_name}.")
        return stage, temp_key

    def _ks_hspf_required_points(self) -> dict:
        return self._ks_hspf_config()["required_points"]

    def _validate_ks_hspf_positive_number(self, value, field_path: str) -> None:
        try:
            numeric_value = float(value)
        except (TypeError, ValueError):
            raise ValueError(
                f"Invalid KS C 9306 HSPF {field_path}: must be positive number."
            ) from None
        if numeric_value <= 0:
            raise ValueError(
                f"Invalid KS C 9306 HSPF {field_path}: must be positive number."
            )

    def _validate_ks_c9306_hspf_input(self, hspf_input: dict) -> None:
        for quantity in ("capacity", "power"):
            quantity_data = hspf_input.get(quantity)
            if quantity_data is None:
                raise ValueError(f"Missing KS C 9306 HSPF {quantity} input.")
            if not isinstance(quantity_data, dict):
                raise ValueError(
                    f"Invalid KS C 9306 HSPF {quantity}: must be dict."
                )

            for temp_key, point_names in self._ks_hspf_required_points().items():
                for point_name in point_names:
                    stage, point = self._ks_hspf_profile_point_path(
                        temp_key, point_name
                    )
                    stage_data = quantity_data.get(stage)
                    if stage_data is None:
                        raise ValueError(
                            f"Missing KS C 9306 HSPF {quantity}.{stage} input."
                        )
                    if not isinstance(stage_data, dict):
                        raise ValueError(
                            f"Invalid KS C 9306 HSPF {quantity}.{stage}: must be dict."
                        )
                    if point not in stage_data:
                        raise ValueError(
                            f"Missing KS C 9306 HSPF {quantity}.{stage}.{point} input."
                        )

            for stage, stage_data in quantity_data.items():
                if stage_data is None:
                    continue
                if not isinstance(stage_data, dict):
                    raise ValueError(
                        f"Invalid KS C 9306 HSPF {quantity}.{stage}: must be dict."
                    )
                for point, value in stage_data.items():
                    self._validate_ks_hspf_positive_number(
                        value,
                        f"{quantity}.{stage}.{point}"
                    )

        correction = hspf_input.get("correction")
        if correction is not None:
            if not isinstance(correction, dict):
                raise ValueError(
                    "Invalid KS C 9306 HSPF correction: must be dict."
                )
            for key in ("capacity_def_over_nof", "power_def_over_nof"):
                if key in correction:
                    self._validate_ks_hspf_positive_number(
                        correction[key],
                        f"correction.{key}"
                    )
            if "cd" in correction:
                try:
                    cd = float(correction["cd"])
                except (TypeError, ValueError):
                    raise ValueError(
                        "Invalid KS C 9306 HSPF correction.cd: must be >= 0 and < 1."
                    ) from None
                if cd < 0 or cd >= 1:
                    raise ValueError(
                        "Invalid KS C 9306 HSPF correction.cd: must be >= 0 and < 1."
                    )

        load_line = hspf_input.get("load_line")
        if load_line is not None:
            if not isinstance(load_line, dict):
                raise ValueError(
                    "Invalid KS C 9306 HSPF load_line: must be dict."
                )
            has_slope = "slope" in load_line
            has_intercept = "intercept" in load_line
            if not has_slope or not has_intercept:
                raise ValueError(
                    "Invalid KS C 9306 HSPF load_line: slope and intercept are required together."
                )
            try:
                slope = float(load_line["slope"])
                float(load_line["intercept"])
            except (TypeError, ValueError):
                raise ValueError(
                    "Invalid KS C 9306 HSPF load_line: slope and intercept must be numeric."
                ) from None
            if slope == 0:
                raise ValueError(
                    "Invalid KS C 9306 HSPF load_line.slope: must be non-zero."
                )

    def _ks_hspf_correction(self, hspf_input: dict, key: str, default: float) -> float:
        correction = hspf_input.get("correction") or {}
        if key in correction:
            return float(correction[key])
        config_correction = self._ks_hspf_config().get("correction", {})
        if isinstance(config_correction, dict) and key in config_correction:
            return float(config_correction[key])
        return float(default)

    def _ks_hspf_minus7_factor(self, quantity: str, stage: str) -> float:
        stage_to_rule = {
            "min": "min_-7",
            "intermediate": "half_-7",
            "rated": "full_-7",
        }
        rule_key = stage_to_rule.get(stage)
        rules = self._ks_hspf_config().get("derived_rules", {})
        if isinstance(rules, dict) and rule_key in rules:
            rule = rules[rule_key]
            factor_key = "capacity_factor" if quantity == "capacity" else "power_factor"
            if factor_key in rule:
                return float(rule[factor_key])
        return 0.601 if quantity == "capacity" else 0.801

    def _ks_hspf_stage_value(
        self,
        hspf_input: dict,
        quantity: str,
        stage: str,
        point: str,
        required: bool = True
    ) -> float:
        quantity_data = hspf_input.get(quantity, {})
        stage_data = quantity_data.get(stage, {})
        if point in stage_data:
            value = float(stage_data[point])
            if self.config.get("round_test_values", False):
                return float(self._round_test_value(value))
            return value

        if point == "-7" and stage in ("min", "rated", "intermediate"):
            if "7" in stage_data:
                factor = self._ks_hspf_minus7_factor(quantity, stage)
                value = float(stage_data["7"])
                if self.config.get("round_test_values", False):
                    value = float(self._round_test_value(value))
                derived = value * factor
                if self.config.get("round_test_values", False):
                    return float(self._round_test_value(derived))
                return derived

        if point == "2" and stage in ("min", "rated", "intermediate"):
            if "7" in stage_data:
                value_minus7 = self._ks_hspf_stage_value(
                    hspf_input, quantity, stage, "-7"
                )
                value_7 = float(stage_data["7"])
                if self.config.get("round_test_values", False):
                    value_7 = float(self._round_test_value(value_7))
                value = self._ks_hspf_linear(
                    2.0, -7.0, value_minus7, 7.0, value_7
                )
                if self.config.get("round_test_values", False):
                    return float(self._round_test_value(value))
                return value

        if required:
            raise ValueError(
                f"Missing KS C 9306 HSPF {quantity}.{stage}.{point} input."
            )
        return None
