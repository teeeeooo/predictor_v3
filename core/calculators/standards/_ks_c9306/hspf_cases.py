"""KS C 9306 HSPF operating-case and per-bin energy engine."""


class KSHSPFCaseEngineMixin:
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
                hspf_input, "rated", frost, load_line
            )
            max_temp = self._ks_hspf_intersection_temp(
                hspf_input, "max", frost, load_line
            )
            rated_power = self._ks_hspf_power_curve(
                rated_temp, hspf_input, "rated", frost
            )
            max_power = self._ks_hspf_power_curve(
                max_temp, hspf_input, "max", frost
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
        aux_cop: float = 1.0,
        load_line: tuple = None
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
        load_line = load_line or self._ks_hspf_load_line(hspf_input)
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
                if tj <= -7.0:
                    heat_pump_power = max_stage["power"]
                elif load_line is None:
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
