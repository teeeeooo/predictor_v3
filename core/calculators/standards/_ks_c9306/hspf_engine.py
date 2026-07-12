"""KS C 9306 HSPF seasonal orchestration."""

from .result import assemble_hspf_result


class KSHSPFSeasonalMixin:
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
        load_line = (
            self._ks_hspf_load_line(hspf_input)
            or self._ks_hspf_config_load_line(measured_inputs)
        )

        for bin_data in bin_hours:
            tj = float(bin_data.get("tj", 0))
            hours = float(bin_data.get("nj", bin_data.get("hours", 0)))
            if hours <= 0:
                continue

            load = self._ks_hspf_bin_load(
                bin_data, tj, hspf_input, measured_inputs, load_line
            )
            if load <= 0:
                continue

            detail = self._ks_hspf_bin(
                tj, load, hours, hspf_input, aux_cop, load_line
            )
            hstl += detail["bin_load"]
            hsec += detail["bin_energy"]
            bin_details.append(detail)

        return assemble_hspf_result(hstl, hsec, bin_details)

    def calculate_hspf(self, measured_inputs: dict, aux_cop: float = 1.0) -> dict:
        return self._calculate_ks_c9306_hspf(measured_inputs, aux_cop=aux_cop)
