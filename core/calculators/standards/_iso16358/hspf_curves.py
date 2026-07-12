"""ISO 16358-2 common capacity, power, and boundary curves."""


class HSPFCommonCurveMixin:
    def _iso_hspf_capacity_curve(self, tj: float, stage: str, resolved: dict, frost: bool) -> float:
        """
        ISO 16358-2 heating capacity curve evaluation.
        """
        p7 = resolved[f"7_{stage}"]
        pm7 = resolved[f"-7_{stage}"]

        if not frost:
            # non-frost: tj <= -7.0 or tj >= 5.5
            return pm7["capacity"] + (p7["capacity"] - pm7["capacity"]) * (tj + 7.0) / 14.0
        else:
            # frost: -7.0 < tj < 5.5
            p2 = resolved.get(f"2_{stage}_f", resolved[f"2_{stage}"])
            return pm7["capacity"] + (p2["capacity"] - pm7["capacity"]) * (tj + 7.0) / 9.0

    def _iso_hspf_power_curve(self, tj: float, stage: str, resolved: dict, frost: bool) -> float:
        """
        ISO 16358-2 heating power curve evaluation.
        """
        p7 = resolved[f"7_{stage}"]
        pm7 = resolved[f"-7_{stage}"]

        if not frost:
            # non-frost: tj <= -7.0 or tj >= 5.5
            return pm7["power"] + (p7["power"] - pm7["power"]) * (tj + 7.0) / 14.0
        else:
            # frost: -7.0 < tj < 5.5
            p2 = resolved.get(f"2_{stage}_f", resolved[f"2_{stage}"])
            return pm7["power"] + (p2["power"] - pm7["power"]) * (tj + 7.0) / 9.0

    def _iso_hspf_capacity_line(self, stage: str, resolved: dict, frost: bool) -> tuple:
        if frost:
            t1, t2 = -7.0, 2.0
        else:
            t1, t2 = -7.0, 7.0
        c1 = self._iso_hspf_capacity_curve(t1, stage, resolved, frost)
        c2 = self._iso_hspf_capacity_curve(t2, stage, resolved, frost)
        slope = (c2 - c1) / (t2 - t1)
        intercept = c1 - slope * t1
        return slope, intercept

    def _iso_hspf_intersection_temp(
        self,
        stage: str,
        resolved: dict,
        frost: bool,
        load_line: tuple
    ) -> float:
        load_slope, load_intercept = load_line
        capacity_slope, capacity_intercept = self._iso_hspf_capacity_line(
            stage, resolved, frost
        )
        denominator = load_slope - capacity_slope
        if denominator == 0:
            raise ValueError("ISO 16358-2 HSPF load line and capacity line are parallel.")
        return (capacity_intercept - load_intercept) / denominator

    def _iso_hspf_boundary_cop(
        self,
        temp: float,
        stage: str,
        resolved: dict,
        frost: bool
    ) -> float:
        # ISO 16358-2 boundary COP at the load-line / capacity-line intersection
        # temperature `temp` (e.g. tk, tj, tg, th, ta, tf).  Both capacity and
        # power are taken from the same stage curve and frost branch so the
        # ratio represents the actual operating COP at that boundary point.
        capacity = self._iso_hspf_capacity_curve(temp, stage, resolved, frost)
        power = self._iso_hspf_power_curve(temp, stage, resolved, frost)
        if power <= 0:
            raise ValueError("ISO 16358-2 HSPF boundary power must be positive.")
        return capacity / power

    def _iso_hspf_boundary_point(
        self,
        stage: str,
        resolved: dict,
        frost: bool,
        load_line: tuple,
    ) -> dict:
        # Resolve the boundary point where the load line intersects the
        # selected stage capacity line.  Returns temperature plus the capacity
        # / power / load / COP at that intersection, all derived from the same
        # stage curves so callers can use them consistently for Formula
        # 44/45/47/48/49/50 endpoint interpolation.
        temp = self._iso_hspf_intersection_temp(stage, resolved, frost, load_line)
        capacity = self._iso_hspf_capacity_curve(temp, stage, resolved, frost)
        power = self._iso_hspf_power_curve(temp, stage, resolved, frost)
        load_slope, load_intercept = load_line
        load = load_slope * temp + load_intercept
        if power <= 0:
            raise ValueError("ISO 16358-2 HSPF boundary power must be positive.")
        return {
            "temp": temp,
            "stage": stage,
            "frost": frost,
            "capacity": capacity,
            "power": power,
            "load_at_boundary": load,
            "cop": capacity / power,
        }

    def _iso_hspf_min_half_power_by_formula_44_48(
        self,
        tj: float,
        bl_h: float,
        resolved: dict,
        frost: bool,
        load_line: tuple
    ) -> float:
        # ISO 16358-2 Formula 44 (non-frost) / Formula 48 (frost):
        #   COP_mh(tj) = COP_min(tk) + (COP_half(tj') - COP_min(tk))
        #                              * (tj - tk) / (tj' - tk)
        # where tk = load/min-capacity intersection, tj' = load/half-capacity
        # intersection.  The rewrite below uses the half boundary as the base
        # term, which is algebraically identical to the spec form.
        min_temp = self._iso_hspf_intersection_temp("min", resolved, frost, load_line)
        half_temp = self._iso_hspf_intersection_temp("half", resolved, frost, load_line)
        denominator = min_temp - half_temp
        if denominator == 0:
            raise ValueError("ISO 16358-2 HSPF min and half boundary temperatures are equal.")

        cop_min = self._iso_hspf_boundary_cop(min_temp, "min", resolved, frost)
        cop_half = self._iso_hspf_boundary_cop(half_temp, "half", resolved, frost)
        cop_mh = cop_half + (cop_min - cop_half) * (tj - half_temp) / denominator
        if cop_mh <= 0:
            raise ValueError("ISO 16358-2 HSPF min-half branch COP must be positive.")
        return bl_h / cop_mh

    def _iso_hspf_half_full_power_by_formula_45_49(
        self,
        tj: float,
        bl_h: float,
        resolved: dict,
        frost: bool,
        load_line: tuple
    ) -> dict:
        # ISO 16358-2 Formula 45 (non-frost) / Formula 49 (frost):
        #   COP_hf(tj) = COP_full(ta) + (COP_half(tj') - COP_full(ta))
        #                              * (tj - ta) / (tj' - ta)
        # ta = load/full-capacity intersection, tj' = load/half-capacity
        # intersection.  The rewrite using cop_full as the base is identical.
        half_temp = self._iso_hspf_intersection_temp("half", resolved, frost, load_line)
        full_temp = self._iso_hspf_intersection_temp("full", resolved, frost, load_line)
        denominator = half_temp - full_temp
        if denominator == 0:
            raise ValueError("ISO 16358-2 HSPF half and full boundary temperatures are equal.")

        cop_half = self._iso_hspf_boundary_cop(half_temp, "half", resolved, frost)
        cop_full = self._iso_hspf_boundary_cop(full_temp, "full", resolved, frost)
        cop_hf = cop_full + (cop_half - cop_full) * (tj - full_temp) / denominator
        if cop_hf <= 0:
            raise ValueError("ISO 16358-2 HSPF half-full branch COP must be positive.")

        pi_half = self._iso_hspf_capacity_curve(tj, "half", resolved, frost)
        pi_full = self._iso_hspf_capacity_curve(tj, "full", resolved, frost)
        if bl_h < pi_half - 1e-5 or bl_h > pi_full + 1e-5:
            raise ValueError(f"Load {bl_h} is outside the half ({pi_half}) to full ({pi_full}) capacity range.")

        branch_id = "formula49_half_full_frost" if frost else "formula45_half_full"

        return {
            "P_hf": bl_h / cop_hf,
            "branch": branch_id,
            "cop_half": cop_half,
            "cop_full": cop_full,
            "cop_hf": cop_hf,
        }
