"""EN 14825 SEER seasonal bin engine."""

from __future__ import annotations

from .context import EN14825ConfigContext
from .performance import EN14825PerformanceCurve
from .result import assemble_seer_result
from .seer_points import SEERPointResolver


class SEERSeasonalEngine:
    def __init__(
        self,
        context: EN14825ConfigContext,
        points: SEERPointResolver,
        performance: EN14825PerformanceCurve,
    ) -> None:
        self._context = context
        self._points = points
        self._performance = performance

    def _calculate_seer_on(
        self,
        test_points: dict,
        p_design_c: float,
        t_design_c: float,
        cd: float,
        *,
        bin_details: list[dict] | None = None,
    ) -> float:
        numerator = 0.0
        denominator = 0.0
        eer_points = self._points._build_cooling_eerpl_points(
            test_points, p_design_c, t_design_c, cd
        )
        bin_temps, bin_hours = self._context._get_seer_bin_data()

        for tj, hj in zip(bin_temps, bin_hours):
            if hj == 0:
                continue
            pc = self._performance._cooling_load_at_temp(
                float(tj), p_design_c, t_design_c
            )
            eer_pl, source = self._performance._interpolate_from_points(
                float(tj), eer_points
            )
            if pc <= 0:
                continue
            if eer_pl <= 0:
                raise ValueError(f"Calculated EERpl is <= 0 at Tj={tj}")

            numerator_contribution = hj * pc
            energy_contribution = hj * (pc / eer_pl)
            numerator += numerator_contribution
            denominator += energy_contribution
            if bin_details is not None:
                bin_details.append(
                    {
                        "temp_c": float(tj),
                        "hours": float(hj),
                        "pc": pc,
                        "eer_pl": eer_pl,
                        "numerator_contribution": numerator_contribution,
                        "energy_contribution": energy_contribution,
                        "interpolation": source,
                    }
                )

        if denominator == 0:
            raise ValueError(
                "SEERon 계산 오류: 분모가 0입니다. test_points 값을 확인하세요."
            )
        return numerator / denominator

    def _get_seer_operational_hours(self, appliance_type: str) -> dict:
        operational_hours = self._context.seer_config.get(
            "operational_hours", {}
        )
        if appliance_type not in operational_hours:
            raise ValueError(
                f"Unknown SEER appliance_type: {appliance_type}. "
                f"Expected one of {sorted(operational_hours.keys())}"
            )
        return operational_hours[appliance_type]

    def calculate_seer(
        self,
        test_points: dict,
        p_to: float,
        p_sb: float,
        p_ck: float,
        p_off: float,
        p_design_c: float,
        t_design_c: float = None,
        cd: float = None,
        *,
        appliance_type: str = None,
    ) -> dict:
        self._points._validate_test_points(test_points)
        if t_design_c is None:
            t_design_c = self._context._get_seer_design_value("t_design_c")
        if cd is None:
            cd = self._context._get_seer_default_value(
                "degradation_coefficient"
            )
        if appliance_type is None:
            try:
                appliance_type = self._context.seer_config["defaults"][
                    "appliance_type"
                ]
            except KeyError as exc:
                raise ValueError(
                    "Missing SEER default config key: appliance_type"
                ) from exc
        operational_hours = self._get_seer_operational_hours(appliance_type)

        qc_kwh = p_design_c * operational_hours["h_ce"]
        seer_on = self._calculate_seer_on(
            test_points, p_design_c, t_design_c, cd
        )
        standby_kwh = (
            operational_hours["h_to"] * p_to
            + operational_hours["h_sb"] * p_sb
            + operational_hours["h_ck"] * p_ck
            + operational_hours["h_off"] * p_off
        )
        active_kwh = qc_kwh / seer_on
        total_kwh = active_kwh + standby_kwh
        seer = qc_kwh / total_kwh
        return assemble_seer_result(seer, seer_on, qc_kwh)

    def calculate_seer_with_details(
        self,
        test_points: dict,
        p_to: float,
        p_sb: float,
        p_ck: float,
        p_off: float,
        p_design_c: float,
        t_design_c: float = None,
        cd: float = None,
        *,
        appliance_type: str = None,
    ) -> dict:
        result = self.calculate_seer(
            test_points=test_points,
            p_to=p_to,
            p_sb=p_sb,
            p_ck=p_ck,
            p_off=p_off,
            p_design_c=p_design_c,
            t_design_c=t_design_c,
            cd=cd,
            appliance_type=appliance_type,
        )
        effective_t_design_c = (
            self._context._get_seer_design_value("t_design_c")
            if t_design_c is None
            else t_design_c
        )
        effective_cd = (
            self._context._get_seer_default_value("degradation_coefficient")
            if cd is None
            else cd
        )
        bin_details: list[dict] = []
        self._calculate_seer_on(
            test_points,
            p_design_c,
            effective_t_design_c,
            effective_cd,
            bin_details=bin_details,
        )
        return {**result, "bin_details": bin_details}
