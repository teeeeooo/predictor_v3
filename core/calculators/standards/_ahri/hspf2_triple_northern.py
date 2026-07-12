"""AHRI 210/240-2026 triple-capacity northern HSPF2 engine."""

from __future__ import annotations

from collections.abc import Mapping

from .hspf2_multicapacity import (
    RESISTANCE_BTU_PER_WH,
    assemble_result,
    availability,
    building_load,
    effective_cd,
    full_curve,
    low_curve,
    positive_point,
    seasonal_context,
)
from .numeric import linear_interpolate, safe_div
from .product import TRIPLE_CAPACITY_NORTHERN


class HSPF2TripleNorthernEngine:
    """Evaluate the eight Section 11.2.2.6 cases and corrected stage curves."""

    def __init__(self, config_context) -> None:
        self.config_context = config_context

    def calculate(self, test_points: Mapping[str, object], **options: object) -> dict:
        context = seasonal_context(self.config_context, options)
        ranges = self._stage_ranges(options)
        points, sources = self._resolve_points(test_points, options, ranges)
        q_a_full, _ = positive_point(test_points, "AFull", "A2", "A_Full")
        cd_low, cd_full, cd_boost = self._degradation_coefficients(options)
        total_heating = compressor_energy = resistance_energy = 0.0
        details: list[dict] = []
        for index, (temp_f, fraction) in enumerate(
            zip(context.bin_temps, context.fractional_hours), 1
        ):
            if fraction <= 0:
                continue
            load = building_load(temp_f, q_a_full, context)
            permitted = {
                stage: lower <= temp_f <= upper
                for stage, (lower, upper) in ranges.items()
            }
            if permitted["low"]:
                q_low, p_low = low_curve(temp_f, points)
                delta_low = availability(temp_f, q_low, p_low, context)
            else:
                q_low = p_low = None
                delta_low = 0.0
            q_full, p_full = full_curve(temp_f, points, points["H4Boost"])
            q_boost, p_boost = self._boost_curve(temp_f, points)
            deltas = {
                "low": delta_low,
                "full": availability(temp_f, q_full, p_full, context),
                "boost": availability(temp_f, q_boost, p_boost, context),
            }
            case, e_comp, e_resistance, load_fractions, plf = self._evaluate_case(
                load=load,
                fraction=fraction,
                permitted=permitted,
                capacities={"low": q_low, "full": q_full, "boost": q_boost},
                powers={"low": p_low, "full": p_full, "boost": p_boost},
                deltas=deltas,
                cds={"low": cd_low, "full": cd_full, "boost": cd_boost},
            )
            selected_delta = self._selected_availability_delta(
                case,
                load_fractions,
                deltas,
            )
            bin_heating = load * fraction
            total_heating += bin_heating
            compressor_energy += e_comp
            resistance_energy += e_resistance
            details.append(
                {
                    "bin": index,
                    "bin_no": index,
                    "temp_F": temp_f,
                    "fractional_hours": fraction,
                    "building_load": load,
                    "q_low": q_low,
                    "p_low": p_low,
                    "q_full": q_full,
                    "p_full": p_full,
                    "q_boost": q_boost,
                    "p_boost": p_boost,
                    "low_permitted": permitted["low"],
                    "full_permitted": permitted["full"],
                    "boost_permitted": permitted["boost"],
                    "delta_low": deltas["low"],
                    "delta_full": deltas["full"],
                    "delta_boost": deltas["boost"],
                    "compressor_availability": self._availability_label(
                        selected_delta
                    ),
                    "operating_case": f"Case {case}",
                    "case": case,
                    "stage_fractions": load_fractions,
                    "PLF": plf,
                    "q_comp": max(
                        0.0,
                        bin_heating - e_resistance * RESISTANCE_BTU_PER_WH,
                    ),
                    "q_aux": e_resistance * RESISTANCE_BTU_PER_WH,
                    "e_comp": e_comp,
                    "e_aux": e_resistance,
                    "q_j": bin_heating,
                    "E_j": e_comp + e_resistance,
                }
            )
        return assemble_result(
            product=TRIPLE_CAPACITY_NORTHERN,
            formula_path="ahri_210_240_2026_triple_capacity_northern_heating",
            context=context,
            total_heating=total_heating,
            compressor_energy=compressor_energy,
            resistance_energy=resistance_energy,
            bin_details=details,
            metadata={
                "point_sources": sources,
                "resolved_points": points,
                "stage_ranges_f": ranges,
                "h3_low_required": ranges["low"][0] <= 37.0,
                "cd_low_used": cd_low,
                "cd_full_used": cd_full,
                "cd_boost_used": cd_boost,
                "resistance_btu_per_wh": RESISTANCE_BTU_PER_WH,
            },
        )

    @staticmethod
    def _evaluate_case(*, load, fraction, permitted, capacities, powers, deltas, cds):
        ql, qf, qb = capacities["low"], capacities["full"], capacities["boost"]
        pl, pf, pb = powers["low"], powers["full"], powers["boost"]
        dl, df, db = deltas["low"], deltas["full"], deltas["boost"]
        fractions: dict[str, float] = {}
        plf = None
        if permitted["low"] and load <= ql:
            case = 1
            fractions["low"] = safe_div(load, ql)
            plf = max(0.01, 1.0 - cds["low"] * (1.0 - fractions["low"]))
            e_comp = safe_div(pl * fractions["low"] * dl * fraction, plf)
            e_res = safe_div(
                load * (1.0 - dl) * fraction,
                RESISTANCE_BTU_PER_WH,
            )
        elif permitted["full"] and load <= qf:
            if permitted["low"] and load > ql:
                case = 4
                fractions["low"] = safe_div(qf - load, qf - ql)
                fractions["full"] = 1.0 - fractions["low"]
                e_comp = (
                    pl * fractions["low"] + pf * fractions["full"]
                ) * dl * fraction
                e_res = safe_div(
                    load * (1.0 - dl) * fraction,
                    RESISTANCE_BTU_PER_WH,
                )
            else:
                case = 2
                fractions["full"] = safe_div(load, qf)
                plf = max(
                    0.01,
                    1.0 - cds["full"] * (1.0 - fractions["full"]),
                )
                e_comp = safe_div(
                    pf * fractions["full"] * df * fraction,
                    plf,
                )
                e_res = safe_div(
                    load * (1.0 - df) * fraction,
                    RESISTANCE_BTU_PER_WH,
                )
        elif permitted["boost"] and load <= qb:
            if permitted["full"] and load > qf:
                case = 5
                fractions["full"] = safe_div(qb - load, qb - qf)
                fractions["boost"] = 1.0 - fractions["full"]
                e_comp = (
                    pf * fractions["full"] + pb * fractions["boost"]
                ) * db * fraction
                e_res = safe_div(
                    load * (1.0 - db) * fraction,
                    RESISTANCE_BTU_PER_WH,
                )
            else:
                case = 3
                fractions["boost"] = safe_div(load, qb)
                plf = max(
                    0.01,
                    1.0 - cds["boost"] * (1.0 - fractions["boost"]),
                )
                e_comp = safe_div(
                    pb * fractions["boost"] * db * fraction,
                    plf,
                )
                e_res = safe_div(
                    load * (1.0 - db) * fraction,
                    RESISTANCE_BTU_PER_WH,
                )
        elif permitted["boost"]:
            case, fractions = 8, {"boost": 1.0}
            e_comp = pb * db * fraction
            e_res = safe_div(
                max(0.0, load - qb * db) * fraction,
                RESISTANCE_BTU_PER_WH,
            )
        elif permitted["full"]:
            case, fractions = 7, {"full": 1.0}
            e_comp = pf * df * fraction
            e_res = safe_div(
                max(0.0, load - qf * df) * fraction,
                RESISTANCE_BTU_PER_WH,
            )
        elif permitted["low"]:
            case, fractions = 6, {"low": 1.0}
            e_comp = pl * dl * fraction
            e_res = safe_div(
                max(0.0, load - ql * dl) * fraction,
                RESISTANCE_BTU_PER_WH,
            )
        else:
            case, fractions = 8, {"resistance": 1.0}
            e_comp = 0.0
            e_res = safe_div(load * fraction, RESISTANCE_BTU_PER_WH)
        return case, max(0.0, e_comp), max(0.0, e_res), fractions, plf

    @staticmethod
    def _resolve_points(test_points, options, ranges):
        points = {
            "H0Low": positive_point(test_points, "H0Low", "H01"),
            "H1Low": positive_point(test_points, "H1Low", "H11"),
            "H1Full": positive_point(test_points, "H1Full", "H12"),
            "H2Full": positive_point(test_points, "H2Full", "H22"),
            "H3Full": positive_point(test_points, "H3Full", "H32"),
            "H3Boost": positive_point(test_points, "H3Boost", "H33"),
            "H4Boost": positive_point(test_points, "H4Boost", "H43"),
        }
        sources = {key: "tested" for key in points}
        h3_low_required = ranges["low"][0] <= 37.0
        h3_low_input = positive_point(
            test_points,
            "H3Low",
            "H31",
            required=False,
        )
        h3_low_tested = h3_low_input is not None and bool(
            options.get("h3_low_tested", True)
        )
        if h3_low_required:
            if not h3_low_tested:
                raise ValueError(
                    "H3Low is required when Low stage is permitted at or below 37 F"
                )
            points["H3Low"] = h3_low_input
            sources["H3Low"] = "tested"
            q_h3, p_h3 = h3_low_input
            q_h1, p_h1 = points["H1Low"]
            points["H2Low"] = (
                0.90 * (q_h3 + 0.6 * (q_h1 - q_h3)),
                0.985 * (p_h3 + 0.6 * (p_h1 - p_h3)),
            )
            sources["H2Low"] = "eq_11_253_11_254_from_tested_h3low"
        else:
            sources["H3Low"] = "not_applicable_to_permitted_range"
            sources["H2Low"] = "not_applicable_to_permitted_range"

        h2_boost = positive_point(
            test_points,
            "H2Boost",
            "H23",
            required=False,
        )
        if h2_boost is None or not bool(options.get("h2_boost_tested", True)):
            q_h2_full, p_h2_full = points["H2Full"]
            q_h3_full, p_h3_full = points["H3Full"]
            q_h1_full, p_h1_full = points["H1Full"]
            q_ratio = safe_div(
                q_h2_full,
                q_h3_full + 0.6 * (q_h1_full - q_h3_full),
                1.0,
            )
            p_ratio = safe_div(
                p_h2_full,
                p_h3_full + 0.6 * (p_h1_full - p_h3_full),
                1.0,
            )
            q_h3_boost, p_h3_boost = points["H3Boost"]
            q_h4_boost, p_h4_boost = points["H4Boost"]
            h2_boost = (
                q_ratio * (q_h3_boost + 1.5 * (q_h3_boost - q_h4_boost)),
                p_ratio * (p_h3_boost + 1.5 * (p_h3_boost - p_h4_boost)),
            )
            sources["H2Boost"] = "eq_11_259_11_262"
        else:
            sources["H2Boost"] = "tested"
        points["H2Boost"] = h2_boost
        return points, sources

    @staticmethod
    def _boost_curve(temp_f, points):
        if temp_f > 17.0:
            low, high, low_temp, high_temp = (
                points["H3Boost"],
                points["H2Boost"],
                17.0,
                35.0,
            )
        else:
            low, high, low_temp, high_temp = (
                points["H4Boost"],
                points["H3Boost"],
                5.0,
                17.0,
            )
        return (
            max(
                0.0,
                linear_interpolate(
                    temp_f,
                    low_temp,
                    low[0],
                    high_temp,
                    high[0],
                ),
            ),
            max(
                0.0,
                linear_interpolate(
                    temp_f,
                    low_temp,
                    low[1],
                    high_temp,
                    high[1],
                ),
            ),
        )

    @staticmethod
    def _stage_ranges(options):
        raw = options.get("stage_ranges_f")
        if isinstance(raw, Mapping):
            ranges = {
                stage: tuple(float(v) for v in raw[stage])
                for stage in ("low", "full", "boost")
            }
        else:
            ranges = {
                "low": (
                    float(options.get("low_stage_min_f", 40.0)),
                    float(options.get("low_stage_max_f", 65.0)),
                ),
                "full": (
                    float(options.get("full_stage_min_f", 20.0)),
                    float(options.get("full_stage_max_f", 50.0)),
                ),
                "boost": (
                    float(options.get("boost_stage_min_f", -20.0)),
                    float(options.get("boost_stage_max_f", 30.0)),
                ),
            }
        for stage, (lower, upper) in ranges.items():
            if lower > upper:
                raise ValueError(
                    f"Invalid {stage} stage operating range: {lower} > {upper}"
                )
        return ranges

    @staticmethod
    def _degradation_coefficients(options):
        raw_low = options.get("cd_low", options.get("c_d_low"))
        low_defaulted = raw_low is None or float(raw_low) > 0.25
        low = effective_cd(raw_low)
        full = (
            low
            if low_defaulted
            else effective_cd(
                options.get("cd_full", options.get("c_d_full", low))
            )
        )
        boost = effective_cd(
            options.get("cd_boost", options.get("c_d_boost", full))
        )
        return low, full, boost

    @staticmethod
    def _selected_availability_delta(case, fractions, deltas):
        if "resistance" in fractions:
            return 0.0
        stage_by_case = {
            1: "low",
            2: "full",
            3: "boost",
            4: "low",
            5: "boost",
            6: "low",
            7: "full",
            8: "boost",
        }
        return deltas[stage_by_case[case]]

    @staticmethod
    def _availability_label(value):
        if value <= 0:
            return "unavailable"
        if value < 1:
            return "fractional"
        return "available"
