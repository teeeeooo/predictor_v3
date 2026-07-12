"""Legacy/simple ISO heating performance and bin evaluation."""


class HSPFLegacyEngineMixin:
    def _variable_heating_performance(self, tj: float, measured_inputs: dict) -> dict:
        stage_points = self._heating_stage_points(measured_inputs)
        high_minus_7 = self._point_at_temp(stage_points["high"], -7.0, "high")
        high_2 = self._point_at_temp(stage_points["high"], 2.0, "high")
        high_7 = self._point_at_temp(stage_points["high"], 7.0, "high")
        _, cap_high_7, power_high_7 = high_7

        if cap_high_7 == 0 or power_high_7 == 0:
            raise ValueError("7C high-stage capacity and power must be non-zero.")

        if tj >= 2.0:
            high = self._linear_heating_point(tj, high_2, high_7)
        else:
            high = self._linear_heating_point(tj, high_minus_7, high_2)

        _, cap_half_7, power_half_7 = self._point_at_temp(
            stage_points["half"], 7.0, "half"
        )
        _, cap_min_7, power_min_7 = self._point_at_temp(
            stage_points["min"], 7.0, "min"
        )

        capacity_ratio = high["capacity"] / cap_high_7
        power_ratio = high["power"] / power_high_7
        return {
            "high": high,
            "half": {
                "capacity": cap_half_7 * capacity_ratio,
                "power": power_half_7 * power_ratio,
            },
            "min": {
                "capacity": cap_min_7 * capacity_ratio,
                "power": power_min_7 * power_ratio,
            },
        }

    def _variable_heating_bin(
        self,
        tj: float,
        load: float,
        hours: float,
        measured_inputs: dict,
        aux_cop: float = 1.0
    ) -> dict:
        if aux_cop <= 0:
            raise ValueError("aux_cop must be positive.")

        performance = self._variable_heating_performance(tj, measured_inputs)
        cap_high = performance["high"]["capacity"]
        power_high = performance["high"]["power"]
        cap_half = performance["half"]["capacity"]
        power_half = performance["half"]["power"]
        cap_min = performance["min"]["capacity"]
        power_min = performance["min"]["power"]

        auxiliary_heat = 0.0
        heat_pump_capacity = load
        if load > cap_high:
            operating_case = "shortage"
            heat_pump_capacity = cap_high
            heat_pump_power = power_high
            auxiliary_heat = load - cap_high
        elif load > cap_half:
            operating_case = "interpolate_high_half"
            if cap_high == cap_half:
                heat_pump_power = power_high
            else:
                heat_pump_power = (
                    power_half
                    + (load - cap_half)
                    / (cap_high - cap_half)
                    * (power_high - power_half)
                )
        elif load > cap_min:
            operating_case = "interpolate_half_min"
            if cap_half == cap_min:
                heat_pump_power = power_half
            else:
                heat_pump_power = (
                    power_min
                    + (load - cap_min)
                    / (cap_half - cap_min)
                    * (power_half - power_min)
                )
        else:
            operating_case = "cyclic_min"
            if cap_min <= 0:
                heat_pump_power = 0.0
            else:
                CR = load / cap_min
                PLF = max(1e-6, 1.0 - self.Cd * (1.0 - CR))
                heat_pump_power = (power_min * CR) / PLF

        heat_pump_energy = heat_pump_power * hours
        auxiliary_energy = auxiliary_heat * hours / aux_cop
        bin_load = load * hours
        bin_energy = heat_pump_energy + auxiliary_energy
        return {
            "tj": tj,
            "hours": hours,
            "load": load,
            "cap_high": cap_high,
            "power_high": power_high,
            "cap_half": cap_half,
            "power_half": power_half,
            "cap_min": cap_min,
            "power_min": power_min,
            "available_capacity": cap_high,
            "heat_pump_capacity": heat_pump_capacity,
            "compressor_heat": heat_pump_capacity,
            "compressor_energy": heat_pump_energy,
            "heat_pump_energy": heat_pump_energy,
            "auxiliary_heat": auxiliary_heat,
            "auxiliary_energy": auxiliary_energy,
            "bin_load": bin_load,
            "bin_energy": bin_energy,
            "operating_case": operating_case,
        }
