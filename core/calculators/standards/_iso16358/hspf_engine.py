"""ISO 16358-2 common seasonal orchestration."""

from .hspf_result import assemble_common_hspf_result


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
        if profile != "iso16358_2_hspf":
            raise ValueError(
                f"Unsupported ISO HSPF profile: {profile!r}; "
                "supported=['iso16358_2_hspf']"
            )
        rated_heating_capacity = measured_inputs.get("rated_heating_capacity")
        if rated_heating_capacity is not None:
            rated_heating_capacity = float(rated_heating_capacity)

        return self.calculate_hspf_iso16358_common(
            measured_inputs=measured_inputs,
            rated_heating_capacity=rated_heating_capacity,
            aux_cop=aux_cop,
        )
