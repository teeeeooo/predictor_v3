"""KS C 9306 HSPF load, capacity, power, and intersection curves."""


class KSHSPFPerformanceMixin:
    def _ks_hspf_linear(self, tj: float, t1: float, v1: float, t2: float, v2: float) -> float:
        if t2 == t1:
            raise ValueError("Interpolation temperatures cannot be equal.")
        return v1 + (v2 - v1) * (tj - t1) / (t2 - t1)

    def _ks_hspf_is_frost_region(self, tj: float) -> bool:
        return -7.0 < tj < 5.5

    def _ks_hspf_frost_def_over_nof_ratio(
        self,
        hspf_input: dict,
        quantity: str
    ) -> float:
        if quantity == "capacity":
            correction_key = "capacity_def_over_nof"
            default = 1.0 / 1.12
        elif quantity == "power":
            correction_key = "power_def_over_nof"
            default = 1.0 / 1.06
        else:
            raise ValueError(f"Unsupported KS HSPF frost ratio quantity: {quantity}")

        base_ratio = self._ks_hspf_correction(hspf_input, correction_key, default)
        if not self.config.get("round_test_values", False):
            return base_ratio

        def_value = self._ks_hspf_stage_value(hspf_input, quantity, "max", "def")
        nofrost_value = float(self._round_test_value(def_value / base_ratio))
        if nofrost_value <= 0:
            raise ValueError(
                f"Invalid KS C 9306 HSPF {quantity} frost no-frost value."
            )
        return def_value / nofrost_value

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
            ratio = self._ks_hspf_frost_def_over_nof_ratio(
                hspf_input, "capacity"
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
            ratio = self._ks_hspf_frost_def_over_nof_ratio(hspf_input, "power")
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
        measured_inputs: dict,
        load_line: tuple = None
    ) -> float:
        if "load" in bin_data:
            return float(bin_data["load"])
        if "heating_load" in bin_data:
            return float(bin_data["heating_load"])

        load_line = (
            load_line
            or self._ks_hspf_load_line(hspf_input)
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
