"""ISO 16358-2 common and compatibility seasonal orchestration."""

from .hspf_result import assemble_common_hspf_result, assemble_legacy_hspf_result


class HSPFSeasonalMixin:
    def calculate_hspf_iso16358_common(
        self,
        measured_inputs: dict,
        rated_heating_capacity: float | None = None,
        aux_cop: float = 1.0
    ) -> dict:
        """
        ISO 16358-2 HSPF common engine.
        """
        hspf_cfg = self.config.get("hspf", {})
        correction_cfg = hspf_cfg.get("correction", {})
        if aux_cop == 1.0:
            aux_cop = float(correction_cfg.get("aux_cop", 1.0))
        if aux_cop <= 0:
            raise ValueError("aux_cop must be positive.")
        cd = float(correction_cfg.get("cd", self.Cd))

        points = self._iso_hspf_normalize_common_points(measured_inputs)
        resolved, active_stages = self._iso_hspf_resolve_common_points(
            points, hspf_cfg
        )
        load_line_info = self._iso_hspf_common_load_line(
            hspf_cfg, rated_heating_capacity, resolved
        )
        frost_boundaries = hspf_cfg.get("frost_boundaries", {})

        hstl, hsec = 0.0, 0.0
        bin_details = []
        bin_hours_key = hspf_cfg.get("bin_hours_key", "hspf_bin_hours")

        for bin_data in self.config.get(bin_hours_key, []):
            detail = self._iso_hspf_evaluate_common_bin(
                bin_data,
                resolved,
                active_stages,
                load_line_info,
                frost_boundaries,
                cd,
                aux_cop,
            )
            if not detail:
                continue

            hstl += detail["bl_h"] * detail["nj"]
            hsec += detail["E_j"]
            bin_details.append(detail)

        return assemble_common_hspf_result(hstl, hsec, bin_details)

    def calculate_hspf(self, measured_inputs: dict, aux_cop: float = 1.0) -> dict:
        measured_inputs = self._prepare_measured_inputs(measured_inputs)
        if aux_cop <= 0:
            raise ValueError("aux_cop must be positive.")

        profile = self.config.get("hspf", {}).get("profile")
        if profile == "iso16358_2_hspf":
            rated_heating_capacity = measured_inputs.get("rated_heating_capacity")
            if rated_heating_capacity is not None:
                rated_heating_capacity = float(rated_heating_capacity)

            return self.calculate_hspf_iso16358_common(
                measured_inputs=measured_inputs,
                rated_heating_capacity=rated_heating_capacity,
                aux_cop=aux_cop,
            )

        hstl = 0.0
        hsec = 0.0
        bin_details = []

        for bin_data in self.bin_hours:
            tj = float(bin_data.get("tj", 0))
            hours = float(bin_data.get("nj", bin_data.get("hours", 0)))
            if hours <= 0:
                continue

            load = float(bin_data.get("load", bin_data.get("heating_load", 0)))
            if load <= 0:
                continue

            if self._has_variable_heating_points(measured_inputs):
                detail = self._variable_heating_bin(
                    tj, load, hours, measured_inputs, aux_cop
                )
            else:
                performance = self.interpolate_heating(tj, measured_inputs)
                available_capacity = max(0.0, performance["capacity"])
                compressor_heat = min(load, available_capacity)
                compressor_energy = max(0.0, performance["power"]) * hours
                auxiliary = self.calc_auxiliary_heat(
                    load, available_capacity, hours, aux_cop
                )
                bin_load = load * hours
                bin_energy = compressor_energy + auxiliary["auxiliary_energy"]
                detail = {
                    "tj": tj,
                    "hours": hours,
                    "load": load,
                    "available_capacity": available_capacity,
                    "compressor_heat": compressor_heat,
                    "compressor_energy": compressor_energy,
                    "heat_pump_energy": compressor_energy,
                    "auxiliary_heat": auxiliary["auxiliary_heat"],
                    "auxiliary_energy": auxiliary["auxiliary_energy"],
                    "bin_load": bin_load,
                    "bin_energy": bin_energy,
                }

            hstl += detail["bin_load"]
            hsec += detail["bin_energy"]
            bin_details.append(detail)

        return assemble_legacy_hspf_result(hstl, hsec, bin_details)
