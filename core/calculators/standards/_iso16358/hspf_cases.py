"""ISO 16358-2 branch selection and per-bin energy evaluation."""


class HSPFCaseEngineMixin:
    def _iso_hspf_select_common_branch(
        self,
        bl_h: float,
        snapshot: dict,
        active_stages: list,
        frost: bool
    ) -> str:
        lowest_stage = "min" if "min" in active_stages else "half"
        if bl_h <= snapshot[lowest_stage]["capacity"]:
            return "cycling"
        if "min" in active_stages and bl_h <= snapshot["half"]["capacity"]:
            return "min_half_formula48" if frost else "min_half_formula44"
        if bl_h <= snapshot["full"]["capacity"]:
            return "half_full_formula49" if frost else "half_full_formula45"
        if "ext" in snapshot and bl_h <= snapshot["ext"]["capacity"]:
            return "full_extended_formula50" if frost else "full_extended_formula47"
        return "saturated"

    def _iso_hspf_stage_pair_power_by_x(
        self,
        bl_h: float,
        low_stage: dict,
        high_stage: dict
    ) -> dict:
        low_capacity = low_stage["capacity"]
        high_capacity = high_stage["capacity"]
        denominator = high_capacity - low_capacity
        if denominator == 0:
            raise ValueError(
                "ISO 16358-2 HSPF stage capacities must differ for interpolation."
            )

        x = (bl_h - low_capacity) / denominator
        power = low_stage["power"] + x * (high_stage["power"] - low_stage["power"])
        return {"X": x, "P_j": power}

    def _iso_hspf_calculate_common_branch_power(
        self,
        branch: str,
        tj: float,
        bl_h: float,
        snapshot: dict,
        active_stages: list,
        cd: float,
        resolved: dict,
        frost: bool,
        load_line: tuple
    ) -> dict:
        if branch == "cycling":
            lowest_stage = "min" if "min" in active_stages else "half"
            capacity = snapshot[lowest_stage]["capacity"]
            power = snapshot[lowest_stage]["power"]
            x = bl_h / capacity
            plf = 1.0 - cd * (1.0 - x)
            if plf <= 0:
                raise ValueError("ISO 16358-2 HSPF cycling PLF must be positive.")
            p_j = x * power / plf
            return {
                "case": "cycling",
                "P_j": p_j,
                "pi_j": bl_h,
                "heat_pump_energy_rate": p_j,
                "auxiliary_heat_rate": 0.0,
                "trace": {
                    "X": x,
                    "PLF": plf,
                    "cycling_stage": lowest_stage,
                },
            }

        if branch in ("min_half_formula44", "min_half_formula48"):
            p_j = self._iso_hspf_min_half_power_by_formula_44_48(
                tj, bl_h, resolved, frost, load_line
            )
            return {
                "case": "min_half_interpolation_frost"
                if branch == "min_half_formula48"
                else "min_half_interpolation",
                "P_j": p_j,
                "pi_j": bl_h,
                "heat_pump_energy_rate": p_j,
                "auxiliary_heat_rate": 0.0,
                "trace": {
                    "branch": branch,
                },
            }

        if branch in ("half_full_formula45", "half_full_formula49"):
            formula_result = self._iso_hspf_half_full_power_by_formula_45_49(
                tj, bl_h, resolved, frost, load_line
            )
            p_j = formula_result["P_hf"]
            trace = {
                key: value for key, value in formula_result.items()
                if key != "P_hf"
            }
            return {
                "case": "formula49_half_full_frost"
                if branch == "half_full_formula49"
                else "formula45_half_full",
                "P_j": p_j,
                "pi_j": bl_h,
                "heat_pump_energy_rate": p_j,
                "auxiliary_heat_rate": 0.0,
                "trace": trace,
            }

        if branch == "full_extended_formula47":
            formula_result = self._iso_hspf_formula47_full_extended_non_frost_power(
                tj, bl_h, resolved, load_line
            )
            p_j = formula_result["P_fe"]
            trace = {
                key: value for key, value in formula_result.items()
                if key != "P_fe"
            }
            return {
                "case": "formula47_full_extended",
                "P_j": p_j,
                "pi_j": bl_h,
                "heat_pump_energy_rate": p_j,
                "auxiliary_heat_rate": 0.0,
                "trace": trace,
            }

        if branch == "full_extended_formula50":
            formula_result = self._iso_hspf_formula50_full_extended_frost_power(
                tj, bl_h, resolved, load_line
            )
            p_j = formula_result["P_fe"]
            trace = {
                "branch": "formula50_full_extended_frost",
                "P_fe": p_j,
                "pi_ext_f": snapshot["ext"]["capacity"],
                "p_ext_f": snapshot["ext"]["power"],
                "backup_heat": 0.0,
            }
            trace.update({
                key: value for key, value in formula_result.items()
                if key != "P_fe"
            })
            return {
                "case": "formula50_full_extended_frost",
                "P_j": p_j,
                "pi_j": bl_h,
                "heat_pump_energy_rate": p_j,
                "auxiliary_heat_rate": 0.0,
                "trace": trace,
            }

        available_stage = "ext" if "ext" in snapshot else "full"
        available_capacity = snapshot[available_stage]["capacity"]
        available_power = snapshot[available_stage]["power"]
        return {
            "case": "saturated",
            "P_j": available_power,
            "pi_j": available_capacity,
            "heat_pump_energy_rate": available_power,
            "auxiliary_heat_rate": max(0.0, bl_h - available_capacity),
            "trace": {
                "saturated_stage": available_stage,
                "backup_heat": max(0.0, bl_h - available_capacity),
            },
        }

    def _iso_hspf_evaluate_common_bin(
        self,
        bin_data: dict,
        resolved: dict,
        active_stages: list,
        load_line_info: dict,
        frost_boundaries: dict,
        cd: float,
        aux_cop: float
    ) -> dict:
        tj = float(bin_data.get("tj", 0))
        nj = float(bin_data.get("nj", 0))
        if nj <= 0:
            return {}

        zero_load_temp = load_line_info["zero_load_temp"]
        full_load_temp = load_line_info["full_load_temp"]
        bl_h = load_line_info["l_h_ref"] * (zero_load_temp - tj) / (
            zero_load_temp - full_load_temp
        )
        if bl_h <= 0:
            return {}

        frost_lower = float(frost_boundaries.get("lower", -7.0))
        frost_upper = float(frost_boundaries.get("upper", 5.5))
        frost = frost_lower < tj < frost_upper
        snapshot = self._iso_hspf_common_stage_snapshot(
            tj, resolved, active_stages, frost
        )
        branch = self._iso_hspf_select_common_branch(
            bl_h, snapshot, active_stages, frost
        )
        branch_result = self._iso_hspf_calculate_common_branch_power(
            branch,
            tj,
            bl_h,
            snapshot,
            active_stages,
            cd,
            resolved,
            frost,
            load_line_info["line"],
        )

        heat_pump_energy = branch_result["heat_pump_energy_rate"] * nj
        auxiliary_energy = branch_result["auxiliary_heat_rate"] * nj / aux_cop
        detail = {
            "tj": tj,
            "nj": nj,
            "bl_h": bl_h,
            "frost": frost,
            "pi_j": branch_result["pi_j"],
            "P_j": branch_result["P_j"],
            "case": branch_result["case"],
            "heat_pump_energy": heat_pump_energy,
            "auxiliary_energy": auxiliary_energy,
            "E_j": heat_pump_energy + auxiliary_energy,
        }
        detail.update(branch_result["trace"])
        detail["frost"] = frost
        return detail
