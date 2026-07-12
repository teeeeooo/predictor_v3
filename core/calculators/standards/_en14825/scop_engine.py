"""EN 14825 SCOP seasonal bin engine."""

from __future__ import annotations

from .context import EN14825ConfigContext
from .performance import EN14825PerformanceCurve
from .result import assemble_scop_result
from .scop_context import SCOPClimateContext
from .scop_performance import SCOPPerformanceCurve
from .scop_points import SCOPPointResolver


class SCOPSeasonalEngine:
    def __init__(
        self,
        context: EN14825ConfigContext,
        climate: SCOPClimateContext,
        points: SCOPPointResolver,
        performance: EN14825PerformanceCurve,
        scop_performance: SCOPPerformanceCurve,
    ) -> None:
        self._context = context
        self._climate = climate
        self._points = points
        self._performance = performance
        self._scop_performance = scop_performance

    def _calculate_scop_on(
        self,
        scop_points: dict,
        climate_data: dict,
        p_design_h: float,
        cd: float,
    ) -> dict:
        temps = climate_data["heating_bin_temps_c"]
        hours = climate_data["heating_bin_hours"]
        t_design_h = float(climate_data["t_design_h_c"])
        tol_temp = scop_points["points"]["TOL"]["temp_c"]
        numerator = 0.0
        denominator = 0.0
        bin_details = []

        for tj, hj in zip(temps, hours):
            if hj <= 0:
                continue
            ph = self._performance._heating_part_load(
                float(tj), p_design_h, t_design_h
            )
            if ph <= 0:
                continue
            if float(tj) < tol_temp:
                pdh = 0.0
                cop_pl = 0.0
                heat_pump_load = 0.0
                elbu = ph
                operating_case = "below_tol_electric_backup_only"
                capacity_source = "below_tol_heat_pump_off"
                cop_source = "below_tol_heat_pump_off"
                cr = 0.0
                denominator_contribution = hj * elbu
            else:
                pdh, capacity_source = (
                    self._scop_performance._capacity_at_temp_for_scop(
                        float(tj), scop_points
                    )
                )
                cop_pl, cop_source = (
                    self._scop_performance._coppl_at_temp_for_scop(
                        float(tj), scop_points
                    )
                )
                if pdh >= ph:
                    elbu = 0.0
                    heat_pump_load = ph
                    operating_case = "heat_pump_covers_load"
                else:
                    elbu = ph - pdh
                    heat_pump_load = pdh
                    operating_case = "capacity_shortfall_with_backup"
                cr = (
                    self._performance._safe_div(heat_pump_load, pdh)
                    if pdh > 0
                    else 0.0
                )
                denominator_contribution = hj * (
                    self._performance._safe_div(heat_pump_load, cop_pl) + elbu
                )

            if heat_pump_load > 0 and cop_pl <= 0:
                raise ValueError(f"SCOP COPPL must be > 0 at Tj={tj}")
            numerator += hj * ph
            denominator += denominator_contribution
            bin_details.append(
                {
                    "temp_c": tj,
                    "hours": hj,
                    "ph": round(ph, 6),
                    "pdh": round(pdh, 6),
                    "cop_pl": round(cop_pl, 6) if cop_pl > 0 else 0.0,
                    "equivalent_power": round(
                        self._performance._safe_div(pdh, cop_pl), 6
                    )
                    if cop_pl > 0
                    else 0.0,
                    "cop_bin": round(cop_pl, 6) if cop_pl > 0 else 0.0,
                    "cr": round(cr, 6),
                    "degradation_factor": 1.0,
                    "capacity_source": capacity_source,
                    "cop_source": cop_source,
                    "denominator_contribution": round(
                        denominator_contribution, 6
                    ),
                    "heat_pump_load": round(heat_pump_load, 6),
                    "elbu": round(elbu, 6),
                    "operating_case": operating_case,
                    "interpolation": (
                        f"capacity={capacity_source}; cop={cop_source}"
                    ),
                }
            )

        if numerator <= 0:
            raise ValueError(
                "SCOPon calculation error: heating demand numerator must be > 0."
            )
        if denominator <= 0:
            raise ValueError(
                "SCOPon calculation error: energy denominator must be > 0."
            )
        return {
            "scop_on": numerator / denominator,
            "active_heating_kwh": numerator,
            "active_energy_kwh": denominator,
            "bin_details": bin_details,
        }

    def calculate_scop(
        self,
        test_points: dict,
        p_to: float,
        p_sb: float,
        p_ck: float,
        p_off: float,
        p_design_h: float,
        climate: str,
        cd: float = None,
        appliance_type: str = None,
        tbiv_temp_c: float = None,
        tol_temp_c: float = None,
    ) -> dict:
        climate_key = self._climate._normalize_climate(climate)
        climate_data = self._climate._get_scop_climate_data(climate_key)
        defaults = self._context.scop_config.get("defaults", {})
        if cd is None:
            try:
                cd = defaults["degradation_coefficient"]
            except KeyError as exc:
                raise ValueError(
                    "Missing SCOP default config key: degradation_coefficient"
                ) from exc
        if appliance_type is None:
            try:
                appliance_type = defaults["appliance_type"]
            except KeyError as exc:
                raise ValueError(
                    "Missing SCOP default config key: appliance_type"
                ) from exc

        point_resolution = self._points._validate_scop_points(
            test_points,
            climate_key,
            climate_data,
            tbiv_temp_c,
            tol_temp_c,
        )
        scop_points = self._scop_performance._build_scop_points(
            point_resolution, climate_data, p_design_h, cd
        )
        operational_hours = self._climate._get_scop_operational_hours(
            climate_key, appliance_type
        )
        scop_on_data = self._calculate_scop_on(
            scop_points, climate_data, p_design_h, cd
        )
        q_h = p_design_h * operational_hours["h_he"]
        if q_h <= 0:
            raise ValueError(
                f"Reference annual heating demand must be > 0: {q_h}"
            )
        standby_kwh = (
            operational_hours["h_to"] * p_to
            + operational_hours["h_sb"] * p_sb
            + operational_hours["h_ck"] * p_ck
            + operational_hours["h_off"] * p_off
        )
        active_kwh = self._performance._safe_div(
            q_h, scop_on_data["scop_on"]
        )
        total_kwh = active_kwh + standby_kwh
        if total_kwh <= 0:
            raise ValueError(
                "SCOP calculation error: total annual heating energy must be > 0."
            )
        return assemble_scop_result(
            scop=q_h / total_kwh,
            scop_on=scop_on_data["scop_on"],
            q_h=q_h,
            active_kwh=active_kwh,
            standby_kwh=standby_kwh,
            total_kwh=total_kwh,
            climate_key=climate_key,
            appliance_type=appliance_type,
            p_design_h=p_design_h,
            operational_hours=operational_hours,
            source=self._context.scop_config.get("source", {}),
            bin_details=scop_on_data["bin_details"],
        )
