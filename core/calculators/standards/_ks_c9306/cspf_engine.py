"""KS C 9306 CSPF seasonal bin engine."""

from decimal import InvalidOperation

from .result import assemble_cspf_result


class KSCSPFSeasonalMixin:
    def _calculate_ks_c9306_cspf(
        self,
        measured_inputs: dict,
        declared_capacity: float = None,
    ) -> dict:
        """KS C 9306 CSPF standalone 계산 본문.

        기존 `points` + `derived_rules` 분기 흐름을 KS module 안에서 직접
        수행한다. measured input 정수화,
        point resolution, declared_capacity 기반 building load,
        bin loop, 최저단 cycling / 사이단 KS intersection / 최고단 saturated
        regime, 누적 cstl/csec를 모두 KS 코드 경로에서 실행한다.
        """
        measured_inputs = self._prepare_measured_inputs(measured_inputs)
        if declared_capacity is not None and self.config.get("round_test_values", False):
            try:
                declared_capacity = self._round_test_value(declared_capacity)
            except (InvalidOperation, ValueError, TypeError):
                pass

        resolved_points = self._resolve_ks_cspf_points(measured_inputs)

        building_load_source = self.config.get("building_load_source")
        reference_point = self.config.get("reference_point", "35_full")

        if building_load_source == "declared":
            if declared_capacity is None or declared_capacity <= 0:
                raise ValueError(
                    "building_load_source가 'declared'인 지역은 "
                    "declared_capacity(표기 정격 능력)를 입력해야 합니다."
                )
            L_c_ref = declared_capacity
        else:
            if reference_point not in resolved_points:
                raise ValueError(
                    f"Reference point '{reference_point}' not found in resolved points. "
                    f"Check config['reference_point'] or input data."
                )
            L_c_ref = resolved_points[reference_point]["capacity"]

        t_100_load = float(self.config.get("t_100_load"))
        t_0_load = float(self.config.get("t_0_load"))
        delta_t = t_100_load - t_0_load
        if delta_t == 0:
            raise ValueError(
                "t_100_load and t_0_load cannot be equal (division by zero)."
            )

        cd = float(self.config.get("Cd", self.Cd))
        power_interp_method = self.config.get("power_interpolation_method")

        cstl = 0.0
        csec = 0.0
        bin_details = []

        for idx, bin_data in enumerate(self.bin_hours, start=1):
            tj = float(bin_data.get("tj", 0))
            nj = float(bin_data.get("nj", 0))

            if nj <= 0:
                bin_details.append({
                    "bin_no": idx, "tj": tj, "nj": nj, "lc": 0.0,
                    "capacity": 0.0, "power": 0.0, "eer": None,
                    "cstl_bin": 0.0, "csec_bin": 0.0,
                })
                continue

            Lc = L_c_ref * (tj - t_0_load) / delta_t
            if Lc <= 0:
                bin_details.append({
                    "bin_no": idx, "tj": tj, "nj": nj, "lc": Lc,
                    "capacity": 0.0, "power": 0.0, "eer": None,
                    "cstl_bin": 0.0, "csec_bin": 0.0,
                })
                continue

            interp_tj = self._interpolate_ks_cspf(tj, resolved_points)
            if "full" not in interp_tj:
                bin_details.append({
                    "bin_no": idx, "tj": tj, "nj": nj, "lc": Lc,
                    "capacity": 0.0, "power": 0.0, "eer": None,
                    "cstl_bin": 0.0, "csec_bin": 0.0,
                })
                continue

            loads = [
                (data["capacity"], data["power"], load_type)
                for load_type, data in interp_tj.items()
            ]
            loads.sort(key=lambda x: x[0])
            if not loads:
                bin_details.append({
                    "bin_no": idx, "tj": tj, "nj": nj, "lc": Lc,
                    "capacity": 0.0, "power": 0.0, "eer": None,
                    "cstl_bin": 0.0, "csec_bin": 0.0,
                })
                continue

            lowest_cap, lowest_pow, _ = loads[0]
            highest_cap, highest_pow, _ = loads[-1]

            cooling_output = Lc
            if Lc <= lowest_cap:
                if lowest_cap <= 0:
                    P_tj = 0.0
                else:
                    X = Lc / lowest_cap
                    PLF = max(1e-6, 1.0 - cd * (1.0 - X))
                    P_tj = (X * lowest_pow) / PLF if PLF > 0 else 0.0
            elif Lc > highest_cap:
                cooling_output = highest_cap
                P_tj = highest_pow
            else:
                P_tj = 0.0
                for i in range(len(loads) - 1):
                    c1, p1, _ = loads[i]
                    c2, p2, _ = loads[i + 1]
                    if c1 < Lc <= c2:
                        lower_type = loads[i][2]
                        upper_type = loads[i + 1][2]
                        ks_power = None
                        if power_interp_method == "ks_intersection":
                            ks_power = self._ks_cspf_intersection_power(
                                tj,
                                L_c_ref,
                                resolved_points,
                                lower_type,
                                upper_type,
                                t_100_load,
                                t_0_load,
                            )
                        if ks_power is not None:
                            P_tj = ks_power
                        elif c2 == c1:
                            P_tj = p1
                        else:
                            P_tj = p1 + (p2 - p1) * (Lc - c1) / (c2 - c1)
                        break

            cstl += cooling_output * nj
            csec += P_tj * nj

            eer = None
            if P_tj > 0:
                eer = cooling_output / P_tj

            bin_details.append({
                "bin_no": idx,
                "tj": tj,
                "nj": nj,
                "lc": Lc,
                "capacity": cooling_output,
                "power": P_tj,
                "eer": eer,
                "cstl_bin": cooling_output * nj,
                "csec_bin": P_tj * nj,
            })

        return assemble_cspf_result(cstl, csec, bin_details)

    def calculate_cspf(self, measured_inputs: dict, declared_capacity: float = None) -> dict:
        return self._calculate_ks_c9306_cspf(measured_inputs, declared_capacity)
