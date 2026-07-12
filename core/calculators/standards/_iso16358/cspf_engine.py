"""ISO 16358-1 CSPF seasonal bin engine."""


class CSPFSeasonalMixin:
    def _calculate_cspf_profile(self, measured: dict, load_reference: float) -> dict:
        resolved = self._resolve_cspf_profile_points(measured)
        cd = self._get_cspf_profile_cd()
        delta_t = self.t_100_load - self.t_0_load
        if delta_t == 0:
            raise ValueError("t_100_load and t_0_load cannot be equal.")

        cstl = 0.0
        csec = 0.0
        bin_details = []
        for idx, bin_data in enumerate(self.bin_hours, start=1):
            tj = float(bin_data.get("tj", 0))
            nj = float(bin_data.get("nj", 0))
            detail = self._calculate_cspf_bin(idx, tj, nj, load_reference, delta_t, resolved, cd)
            cstl += detail["cstl_bin"]
            csec += detail["csec_bin"]
            bin_details.append(detail)

        return self._build_cspf_result(cstl, csec, bin_details)

    def _calculate_cspf_bin(
        self,
        idx: int,
        tj: float,
        nj: float,
        load_reference: float,
        delta_t: float,
        resolved_points: dict,
        cd: float,
    ) -> dict:
        if nj <= 0:
            return self._empty_cspf_bin(idx, tj, nj, 0.0)

        load = load_reference * (tj - self.t_0_load) / delta_t
        if load <= 0:
            return self._empty_cspf_bin(idx, tj, nj, load)

        interpolated = self.interpolate(tj, resolved_points)
        loads = [
            (data["capacity"], data["power"], load_type)
            for load_type, data in interpolated.items()
        ]
        loads.sort(key=lambda item: item[0])
        if not loads:
            return self._empty_cspf_bin(idx, tj, nj, load)

        lowest_cap, lowest_pow, _ = loads[0]
        highest_cap, highest_pow, _ = loads[-1]
        cooling_output = load

        if load <= lowest_cap:
            if lowest_cap <= 0:
                power = 0.0
            else:
                cycling_ratio = load / lowest_cap
                part_load_factor = max(1e-6, 1.0 - cd * (1.0 - cycling_ratio))
                power = (cycling_ratio * lowest_pow) / part_load_factor
        elif load > highest_cap:
            cooling_output = highest_cap
            power = highest_pow
        else:
            power = None
            for i in range(len(loads) - 1):
                c1, p1, lower_type = loads[i]
                c2, p2, upper_type = loads[i + 1]
                if c1 < load <= c2:
                    if self.power_interpolation_method == "iso_boundary_eer":
                        power = self._iso_boundary_eer_power(
                            tj, load, resolved_points, lower_type, upper_type
                        )
                    if power is not None:
                        break
                    if c2 == c1:
                        power = p1
                    else:
                        power = p1 + (p2 - p1) * (load - c1) / (c2 - c1)
                    break
            if power is None:
                power = highest_pow

        eer = cooling_output / power if power > 0 else None
        return {
            "bin_no": idx,
            "tj": tj,
            "nj": nj,
            "lc": load,
            "capacity": cooling_output,
            "power": power,
            "eer": eer,
            "cstl_bin": cooling_output * nj,
            "csec_bin": power * nj,
        }

    def _empty_cspf_bin(self, idx: int, tj: float, nj: float, load: float) -> dict:
        return {
            "bin_no": idx,
            "tj": tj,
            "nj": nj,
            "lc": load,
            "capacity": 0.0,
            "power": 0.0,
            "eer": None,
            "cstl_bin": 0.0,
            "csec_bin": 0.0,
        }

    def calculate_cspf(
        self,
        measured_inputs: dict,
        declared_capacity: float = None,
    ) -> dict:
        if self._has_cspf_test_profile():
            resolved = self._resolve_cspf_profile_points(measured_inputs)
            load_reference = resolved[self.reference_point]["capacity"]
            return self._calculate_cspf_profile(measured_inputs, load_reference)

        resolved_points = self.resolve_points(measured_inputs)
        if self.building_load_source == "declared":
            if declared_capacity is None or declared_capacity <= 0:
                raise ValueError(
                    "building_load_source가 'declared'인 지역은 "
                    "declared_capacity(표기 정격 능력)를 입력해야 합니다."
                )
            load_reference = declared_capacity
        else:
            if self.reference_point not in resolved_points:
                raise ValueError(
                    f"Reference point '{self.reference_point}' not found in resolved points. "
                    f"Check config['reference_point'] or input data."
                )
            load_reference = resolved_points[self.reference_point]["capacity"]

        delta_t = self.t_100_load - self.t_0_load
        if delta_t == 0:
            raise ValueError("t_100_load and t_0_load cannot be equal.")

        cstl = 0.0
        csec = 0.0
        bin_details = []
        for idx, bin_data in enumerate(self.bin_hours, start=1):
            tj = float(bin_data.get("tj", 0))
            nj = float(bin_data.get("nj", 0))
            detail = self._calculate_cspf_bin(
                idx, tj, nj, load_reference, delta_t, resolved_points, self.Cd
            )
            cstl += detail["cstl_bin"]
            csec += detail["csec_bin"]
            bin_details.append(detail)

        return self._build_cspf_result(cstl, csec, bin_details)
