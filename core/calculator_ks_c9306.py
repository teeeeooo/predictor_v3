# core/calculator_ks_c9306.py

import json
import os


class KSC9306Calculator:
    """KS C 9306 전용 special calculator.

    ISO 16358 common path와 분리된 KS C 9306 CSPF/HSPF 전용 special
    calculator이다. 현재는 KS C 9306 HSPF 계산 (`calculate_hspf`) 및 ISO16358
    common path가 delegation으로 호출하는 KS 전용 helper를 보유한다.

    Behavior-preserving extraction: 이 클래스는 기존
    ``ISO16358Calculator``의 ``_ks_hspf_*`` / ``_calculate_ks_c9306_hspf``
    로직을 그대로 옮긴 결과이며 계산식은 변경하지 않는다.
    """

    def __init__(self, config: dict, bin_hours=None, default_cd: float = 0.25):
        self.config = config
        self.bin_hours = bin_hours if bin_hours is not None else config.get("bin_hours", [])
        self.Cd = default_cd

    @classmethod
    def from_config_path(cls, config_path: str) -> "KSC9306Calculator":
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"설정 파일을 찾을 수 없습니다: {config_path}")
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        config.pop("_comment", None)
        return cls(
            config,
            bin_hours=config.get("bin_hours", []),
            default_cd=config.get("Cd", 0.25),
        )

    @classmethod
    def from_iso_calculator(cls, iso_calculator) -> "KSC9306Calculator":
        instance = cls.__new__(cls)
        instance.config = iso_calculator.config
        instance.bin_hours = iso_calculator.bin_hours
        instance.Cd = iso_calculator.Cd
        return instance

    # ------------------------------------------------------------------
    # KS C 9306 CSPF helpers
    # ------------------------------------------------------------------

    def _ks_cspf_performance_line(self, resolved_points: dict, load_type: str) -> tuple:
        points = []
        for point_key, data in resolved_points.items():
            parts = point_key.split("_")
            if len(parts) != 2 or parts[1] != load_type:
                continue
            points.append((float(parts[0]), data["capacity"], data["power"]))

        points.sort(key=lambda x: x[0])
        if len(points) < 2:
            return None

        t1, c1, p1 = points[0]
        t2, c2, p2 = points[-1]
        if t2 == t1:
            return None

        capacity_slope = (c2 - c1) / (t2 - t1)
        capacity_intercept = c1 - capacity_slope * t1
        power_slope = (p2 - p1) / (t2 - t1)
        power_intercept = p1 - power_slope * t1
        return capacity_slope, capacity_intercept, power_slope, power_intercept

    def _ks_cspf_intersection_power(
        self,
        tj: float,
        L_c_ref: float,
        resolved_points: dict,
        lower_type: str,
        upper_type: str,
        t_100_load: float,
        t_0_load: float,
    ) -> float:
        lower_line = self._ks_cspf_performance_line(resolved_points, lower_type)
        upper_line = self._ks_cspf_performance_line(resolved_points, upper_type)
        if lower_line is None or upper_line is None:
            return None

        load_slope = L_c_ref / (t_100_load - t_0_load)
        load_intercept = -load_slope * t_0_load

        def intersection_temperature(line):
            capacity_slope, capacity_intercept, _, _ = line
            denominator = load_slope - capacity_slope
            if denominator == 0:
                return None
            return (capacity_intercept - load_intercept) / denominator

        def power_at(line, temp):
            _, _, power_slope, power_intercept = line
            return power_slope * temp + power_intercept

        t_lower = intersection_temperature(lower_line)
        t_upper = intersection_temperature(upper_line)
        if t_lower is None or t_upper is None or t_upper == t_lower:
            return None

        p_lower = power_at(lower_line, t_lower)
        p_upper = power_at(upper_line, t_upper)
        return p_upper - ((p_upper - p_lower) / (t_upper - t_lower)) * (t_upper - tj)

    # ------------------------------------------------------------------
    # KS C 9306 HSPF
    # ------------------------------------------------------------------

    def _has_ks_c9306_hspf_input(self, measured_inputs: dict) -> bool:
        hspf_config = self.config.get("hspf", {})
        if not isinstance(hspf_config, dict):
            return False
        return hspf_config.get("profile") == "ks_c_9306_hspf"

    def _ks_hspf_input(self, measured_inputs: dict) -> dict:
        if "ks_c_9306_hspf" not in measured_inputs:
            raise ValueError("Missing ks_c_9306_hspf input.")
        hspf_input = measured_inputs["ks_c_9306_hspf"]
        if not isinstance(hspf_input, dict):
            raise ValueError("Invalid KS C 9306 HSPF ks_c_9306_hspf: must be dict.")
        return hspf_input

    def _ks_hspf_config(self) -> dict:
        hspf_config = self.config.get("hspf", {})
        if not isinstance(hspf_config, dict):
            return {}
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
        hspf_config = self._ks_hspf_config()
        required_points = hspf_config.get("required_points", {})
        if isinstance(required_points, dict) and required_points:
            return required_points
        return {}

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
            return float(stage_data[point])

        if point == "-7" and stage in ("min", "rated", "intermediate"):
            if "7" in stage_data:
                factor = self._ks_hspf_minus7_factor(quantity, stage)
                return float(stage_data["7"]) * factor

        if point == "2" and stage in ("min", "rated", "intermediate"):
            if "7" in stage_data:
                value_minus7 = self._ks_hspf_stage_value(
                    hspf_input, quantity, stage, "-7"
                )
                value_7 = float(stage_data["7"])
                return self._ks_hspf_linear(
                    2.0, -7.0, value_minus7, 7.0, value_7
                )

        if required:
            raise ValueError(
                f"Missing KS C 9306 HSPF {quantity}.{stage}.{point} input."
            )
        return None

    def _ks_hspf_linear(self, tj: float, t1: float, v1: float, t2: float, v2: float) -> float:
        if t2 == t1:
            raise ValueError("Interpolation temperatures cannot be equal.")
        return v1 + (v2 - v1) * (tj - t1) / (t2 - t1)

    def _ks_hspf_is_frost_region(self, tj: float) -> bool:
        return -7.0 < tj < 5.5

    def _ks_hspf_capacity_curve(
        self,
        tj: float,
        hspf_input: dict,
        stage: str,
        frost: bool = None
    ) -> float:
        if frost is None:
            frost = self._ks_hspf_is_frost_region(tj)

        if stage == "max":
            cap_minus7 = self._ks_hspf_stage_value(hspf_input, "capacity", "max", "-7")
            cap_def = self._ks_hspf_stage_value(hspf_input, "capacity", "max", "def")
            return self._ks_hspf_linear(tj, -7.0, cap_minus7, 2.0, cap_def)

        cap_minus7 = self._ks_hspf_stage_value(hspf_input, "capacity", stage, "-7")
        if frost:
            cap_2 = self._ks_hspf_stage_value(hspf_input, "capacity", stage, "2")
            ratio = self._ks_hspf_correction(
                hspf_input, "capacity_def_over_nof", 1.0 / 1.12
            )
            cap_2 = cap_2 * ratio
            return self._ks_hspf_linear(tj, -7.0, cap_minus7, 2.0, cap_2)

        cap_7 = self._ks_hspf_stage_value(hspf_input, "capacity", stage, "7")
        return self._ks_hspf_linear(tj, -7.0, cap_minus7, 7.0, cap_7)

    def _ks_hspf_power_curve(
        self,
        tj: float,
        hspf_input: dict,
        stage: str,
        frost: bool = None
    ) -> float:
        if frost is None:
            frost = self._ks_hspf_is_frost_region(tj)

        if stage == "max":
            power_minus7 = self._ks_hspf_stage_value(hspf_input, "power", "max", "-7")
            power_def = self._ks_hspf_stage_value(hspf_input, "power", "max", "def")
            return self._ks_hspf_linear(tj, -7.0, power_minus7, 2.0, power_def)

        power_minus7 = self._ks_hspf_stage_value(hspf_input, "power", stage, "-7")
        if frost:
            power_2 = self._ks_hspf_stage_value(hspf_input, "power", stage, "2")
            ratio = self._ks_hspf_correction(
                hspf_input, "power_def_over_nof", 1.0 / 1.06
            )
            power_2 = power_2 * ratio
            return self._ks_hspf_linear(tj, -7.0, power_minus7, 2.0, power_2)

        power_7 = self._ks_hspf_stage_value(hspf_input, "power", stage, "7")
        return self._ks_hspf_linear(tj, -7.0, power_minus7, 7.0, power_7)

    def _ks_hspf_stage_curves(self, tj: float, hspf_input: dict) -> dict:
        return {
            "min": {
                "capacity": self._ks_hspf_capacity_curve(tj, hspf_input, "min"),
                "power": self._ks_hspf_power_curve(tj, hspf_input, "min"),
            },
            "intermediate": {
                "capacity": self._ks_hspf_capacity_curve(tj, hspf_input, "intermediate"),
                "power": self._ks_hspf_power_curve(tj, hspf_input, "intermediate"),
            },
            "rated": {
                "capacity": self._ks_hspf_capacity_curve(tj, hspf_input, "rated"),
                "power": self._ks_hspf_power_curve(tj, hspf_input, "rated"),
            },
            "max": {
                "capacity": self._ks_hspf_capacity_curve(tj, hspf_input, "max"),
                "power": self._ks_hspf_power_curve(tj, hspf_input, "max"),
            },
        }

    def _ks_hspf_interpolate_power_for_load(
        self,
        load: float,
        lower_capacity: float,
        lower_power: float,
        upper_capacity: float,
        upper_power: float
    ) -> float:
        if upper_capacity == lower_capacity:
            return upper_power
        return (
            lower_power
            + (load - lower_capacity)
            / (upper_capacity - lower_capacity)
            * (upper_power - lower_power)
        )

    def _ks_hspf_load_line(self, hspf_input: dict) -> tuple:
        load_line = hspf_input.get("load_line")
        if not isinstance(load_line, dict):
            return None
        if "slope" not in load_line or "intercept" not in load_line:
            return None
        return float(load_line["slope"]), float(load_line["intercept"])

    def _ks_hspf_config_load_line(self, measured_inputs: dict) -> tuple:
        load_line = self._ks_hspf_config().get("load_line")
        if not isinstance(load_line, dict):
            return None
        if "source" not in load_line:
            raise ValueError("Invalid KS C 9306 HSPF load_line: source is required.")
        required_fields = ("zero_load_temp", "full_load_temp", "rated_capacity_factor")
        if any(field not in load_line for field in required_fields):
            raise ValueError(
                "Invalid KS C 9306 HSPF load_line: zero_load_temp, "
                "full_load_temp, and rated_capacity_factor are required."
            )

        # KS C 9306 HSPF load line: BL_h(0°C) = rated_cooling_capacity * 0.82
        source = load_line["source"]
        if source != "rated_cooling_capacity":
            raise ValueError(
                f"KS C 9306 HSPF requires rated_cooling_capacity, not '{source}'."
            )

        reference_capacity = measured_inputs.get(source)
        if reference_capacity is None:
            raise ValueError("KS C 9306 HSPF requires rated_cooling_capacity for heating building load.")

        self._validate_ks_hspf_positive_number(reference_capacity, "rated_cooling_capacity")

        zero_load_temp = float(load_line["zero_load_temp"])
        full_load_temp = float(load_line["full_load_temp"])
        if zero_load_temp == full_load_temp:
            raise ValueError("KS C 9306 HSPF load line temperatures cannot be equal.")

        # BL_h(tj) = (rated_cooling_capacity * 0.82) * (zero_load_temp - tj) / (zero_load_temp - 0)
        full_load_at_0 = float(reference_capacity) * float(load_line["rated_capacity_factor"])
        slope = full_load_at_0 / (full_load_temp - zero_load_temp)
        intercept = -slope * zero_load_temp
        return slope, intercept

    def _ks_hspf_bin_load(
        self,
        bin_data: dict,
        tj: float,
        hspf_input: dict,
        measured_inputs: dict
    ) -> float:
        if "load" in bin_data:
            return float(bin_data["load"])
        if "heating_load" in bin_data:
            return float(bin_data["heating_load"])

        load_line = (
            self._ks_hspf_load_line(hspf_input)
            or self._ks_hspf_config_load_line(measured_inputs)
        )
        if load_line is None:
            raise ValueError(
                "Missing KS C 9306 HSPF bin load and load line configuration."
            )
        slope, intercept = load_line
        return max(0.0, slope * tj + intercept)

    def _ks_hspf_capacity_line(
        self,
        hspf_input: dict,
        stage: str,
        frost: bool
    ) -> tuple:
        if stage == "max":
            t1 = -7.0
            t2 = 2.0
        elif frost:
            t1 = -7.0
            t2 = 2.0
        else:
            t1 = -7.0
            t2 = 7.0

        c1 = self._ks_hspf_capacity_curve(t1, hspf_input, stage, frost)
        c2 = self._ks_hspf_capacity_curve(t2, hspf_input, stage, frost)
        slope = (c2 - c1) / (t2 - t1)
        intercept = c1 - slope * t1
        return slope, intercept

    def _ks_hspf_intersection_temp(
        self,
        hspf_input: dict,
        stage: str,
        frost: bool,
        load_line: tuple
    ) -> float:
        load_slope, load_intercept = load_line
        capacity_slope, capacity_intercept = self._ks_hspf_capacity_line(
            hspf_input, stage, frost
        )
        denominator = load_slope - capacity_slope
        if denominator == 0:
            raise ValueError("Load line and capacity line are parallel.")
        return (capacity_intercept - load_intercept) / denominator

    def _ks_hspf_power_by_intersection(
        self,
        tj: float,
        hspf_input: dict,
        case_name: str,
        load_line: tuple
    ) -> float:
        frost = self._ks_hspf_is_frost_region(tj)

        if case_name == "minimum_intermediate":
            min_temp = self._ks_hspf_intersection_temp(
                hspf_input, "min", frost, load_line
            )
            intermediate_temp = self._ks_hspf_intersection_temp(
                hspf_input, "intermediate", frost, load_line
            )
            min_power = self._ks_hspf_power_curve(
                min_temp, hspf_input, "min", frost
            )
            intermediate_power = self._ks_hspf_power_curve(
                intermediate_temp, hspf_input, "intermediate", frost
            )
            return self._ks_hspf_linear(
                tj, intermediate_temp, intermediate_power, min_temp, min_power
            )

        if case_name == "intermediate_rated":
            rated_temp = self._ks_hspf_intersection_temp(
                hspf_input, "rated", frost, load_line
            )
            intermediate_temp = self._ks_hspf_intersection_temp(
                hspf_input, "intermediate", frost, load_line
            )
            rated_power = self._ks_hspf_power_curve(
                rated_temp, hspf_input, "rated", frost
            )
            intermediate_power = self._ks_hspf_power_curve(
                intermediate_temp, hspf_input, "intermediate", frost
            )
            return self._ks_hspf_linear(
                tj, rated_temp, rated_power, intermediate_temp, intermediate_power
            )

        if case_name == "rated_maximum":
            rated_temp = self._ks_hspf_intersection_temp(
                hspf_input, "rated", True, load_line
            )
            max_temp = self._ks_hspf_intersection_temp(
                hspf_input, "max", True, load_line
            )
            rated_power = self._ks_hspf_power_curve(
                rated_temp, hspf_input, "rated", True
            )
            max_power = self._ks_hspf_power_curve(
                max_temp, hspf_input, "max", True
            )
            return self._ks_hspf_linear(
                tj, max_temp, max_power, rated_temp, rated_power
            )

        raise ValueError(f"Unsupported KS HSPF intersection case: {case_name}")

    def _ks_hspf_bin(
        self,
        tj: float,
        load: float,
        hours: float,
        hspf_input: dict,
        aux_cop: float = 1.0
    ) -> dict:
        if aux_cop <= 0:
            raise ValueError("aux_cop must be positive.")

        max_stage = {
            "capacity": self._ks_hspf_capacity_curve(tj, hspf_input, "max"),
            "power": self._ks_hspf_power_curve(tj, hspf_input, "max"),
        }

        auxiliary_heat = 0.0
        heat_pump_capacity = load
        capacity_load_ratio = 1.0
        part_load_factor = 1.0
        available_capacity = max_stage["capacity"]
        load_line = self._ks_hspf_load_line(hspf_input)
        min_stage = {"capacity": None, "power": None}
        intermediate_stage = {"capacity": None, "power": None}
        rated_stage = {"capacity": None, "power": None}

        if tj <= 2.0 and load > max_stage["capacity"]:
            operating_case = "maximum_shortage"
            heat_pump_capacity = max_stage["capacity"]
            heat_pump_power = max_stage["power"]
            auxiliary_heat = load - max_stage["capacity"]
        else:
            rated_stage = {
                "capacity": self._ks_hspf_capacity_curve(tj, hspf_input, "rated"),
                "power": self._ks_hspf_power_curve(tj, hspf_input, "rated"),
            }
            available_capacity = max(max_stage["capacity"], rated_stage["capacity"])
            if load > available_capacity:
                operating_case = "maximum_shortage"
                heat_pump_capacity = available_capacity
                if max_stage["capacity"] >= rated_stage["capacity"]:
                    heat_pump_power = max_stage["power"]
                else:
                    heat_pump_power = rated_stage["power"]
                auxiliary_heat = load - available_capacity
            elif load > rated_stage["capacity"]:
                operating_case = "rated_maximum"
                if load_line is None:
                    heat_pump_power = self._ks_hspf_interpolate_power_for_load(
                        load,
                        rated_stage["capacity"],
                        rated_stage["power"],
                        max_stage["capacity"],
                        max_stage["power"],
                    )
                else:
                    heat_pump_power = self._ks_hspf_power_by_intersection(
                        tj, hspf_input, operating_case, load_line
                    )
            else:
                intermediate_stage = {
                    "capacity": self._ks_hspf_capacity_curve(
                        tj, hspf_input, "intermediate"
                    ),
                    "power": self._ks_hspf_power_curve(
                        tj, hspf_input, "intermediate"
                    ),
                }
                if load > intermediate_stage["capacity"]:
                    operating_case = "intermediate_rated"
                    if load_line is None:
                        heat_pump_power = self._ks_hspf_interpolate_power_for_load(
                            load,
                            intermediate_stage["capacity"],
                            intermediate_stage["power"],
                            rated_stage["capacity"],
                            rated_stage["power"],
                        )
                    else:
                        heat_pump_power = self._ks_hspf_power_by_intersection(
                            tj, hspf_input, operating_case, load_line
                        )
                else:
                    min_stage = {
                        "capacity": self._ks_hspf_capacity_curve(tj, hspf_input, "min"),
                        "power": self._ks_hspf_power_curve(tj, hspf_input, "min"),
                    }
                    if load > min_stage["capacity"]:
                        operating_case = "minimum_intermediate"
                        if load_line is None:
                            heat_pump_power = self._ks_hspf_interpolate_power_for_load(
                                load,
                                min_stage["capacity"],
                                min_stage["power"],
                                intermediate_stage["capacity"],
                                intermediate_stage["power"],
                            )
                        else:
                            heat_pump_power = self._ks_hspf_power_by_intersection(
                                tj, hspf_input, operating_case, load_line
                            )
                    else:
                        operating_case = "cyclic_minimum"
                        if min_stage["capacity"] <= 0:
                            heat_pump_power = 0.0
                            capacity_load_ratio = 0.0
                        else:
                            capacity_load_ratio = load / min_stage["capacity"]
                            cd = self._ks_hspf_correction(hspf_input, "cd", self.Cd)
                            part_load_factor = max(
                                1e-6,
                                1.0 - cd * (1.0 - capacity_load_ratio)
                            )
                            heat_pump_power = (
                                min_stage["power"]
                                * capacity_load_ratio
                                / part_load_factor
                            )

        heat_pump_energy = heat_pump_power * hours
        auxiliary_energy = auxiliary_heat * hours / aux_cop
        bin_load = load * hours
        bin_energy = heat_pump_energy + auxiliary_energy
        return {
            "tj": tj,
            "hours": hours,
            "load": load,
            "cap_min": min_stage["capacity"],
            "power_min": min_stage["power"],
            "cap_intermediate": intermediate_stage["capacity"],
            "power_intermediate": intermediate_stage["power"],
            "cap_rated": rated_stage["capacity"],
            "power_rated": rated_stage["power"],
            "cap_max": max_stage["capacity"],
            "power_max": max_stage["power"],
            "available_capacity": available_capacity,
            "heat_pump_capacity": heat_pump_capacity,
            "compressor_heat": heat_pump_capacity,
            "compressor_energy": heat_pump_energy,
            "heat_pump_energy": heat_pump_energy,
            "auxiliary_heat": auxiliary_heat,
            "auxiliary_energy": auxiliary_energy,
            "capacity_load_ratio": capacity_load_ratio,
            "part_load_factor": part_load_factor,
            "load_line_used": load_line is not None,
            "bin_load": bin_load,
            "bin_energy": bin_energy,
            "operating_case": operating_case,
        }

    def _calculate_ks_c9306_hspf(
        self,
        measured_inputs: dict,
        aux_cop: float = 1.0
    ) -> dict:
        hspf_input = self._ks_hspf_input(measured_inputs)
        self._validate_ks_c9306_hspf_input(hspf_input)
        hstl = 0.0
        hsec = 0.0
        bin_details = []
        hspf_config = self._ks_hspf_config()
        bin_hours_key = hspf_config.get("bin_hours_key")
        bin_hours = self.config.get(bin_hours_key, self.bin_hours) if bin_hours_key else self.bin_hours

        for bin_data in bin_hours:
            tj = float(bin_data.get("tj", 0))
            hours = float(bin_data.get("nj", bin_data.get("hours", 0)))
            if hours <= 0:
                continue

            load = self._ks_hspf_bin_load(
                bin_data, tj, hspf_input, measured_inputs
            )
            if load <= 0:
                continue

            detail = self._ks_hspf_bin(tj, load, hours, hspf_input, aux_cop)
            hstl += detail["bin_load"]
            hsec += detail["bin_energy"]
            bin_details.append(detail)

        if hsec <= 0:
            return {"hspf": 0.0, "HSPF": 0.0, "HSTL": hstl, "HSEC": hsec, "bin_details": bin_details}

        hspf = hstl / hsec
        heat_pump_energy = sum(
            item.get("heat_pump_energy", item.get("compressor_energy", 0.0))
            for item in bin_details
        )
        auxiliary_energy = sum(
            item.get("auxiliary_energy", 0.0) for item in bin_details
        )
        return {
            "hspf": hspf,
            "HSPF": hspf,
            "hstl": hstl,
            "HSTL": hstl,
            "hsec": hsec,
            "HSEC": hsec,
            "heat_pump_energy": heat_pump_energy,
            "auxiliary_energy": auxiliary_energy,
            "bin_details": bin_details
        }

    def calculate_hspf(self, measured_inputs: dict, aux_cop: float = 1.0) -> dict:
        return self._calculate_ks_c9306_hspf(measured_inputs, aux_cop=aux_cop)
