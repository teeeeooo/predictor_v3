"""AHRI 210/240-2026 dual-stage SEER2 seasonal engine."""

from __future__ import annotations

from collections.abc import Mapping

from .numeric import linear_interpolate, round_nearest_005, safe_div
from .product import DUAL_STAGE

_BIN_TEMPS_F = (67.0, 72.0, 77.0, 82.0, 87.0, 92.0, 97.0, 102.0)
_FRACTIONAL_HOURS = (0.214, 0.231, 0.216, 0.161, 0.104, 0.052, 0.018, 0.004)
_DEFAULT_CD = 0.20


class SEER2DualStageEngine:
    """Evaluate Section 11.2.1.2 without changing the variable-capacity path."""

    _ALIASES = {
        "AFull": ("AFull", "A_Full", "A2"),
        "BFull": ("BFull", "B_Full", "B2"),
        "BLow": ("BLow", "B_Low", "B1"),
        "FLow": ("FLow", "F_Low", "F1"),
    }

    def calculate(
        self,
        test_points: Mapping[str, object],
        *,
        system_type: str = "HP",
        p_w_off: float = 0.0,
        cd_low: float | None = None,
        options: Mapping[str, object] | None = None,
    ) -> dict:
        options = dict(options or {})
        points = {name: self._positive_point(test_points, aliases) for name, aliases in self._ALIASES.items()}
        q_a, p_a = points["AFull"]
        q_b, p_b = points["BFull"]
        q_b_low, p_b_low = points["BLow"]
        q_f_low, p_f_low = points["FLow"]

        cd_low_used = self._effective_cd(options.get("cd_low", cd_low))
        cd_full_used = self._effective_cd(options.get("cd_full"))
        lockout_enabled = bool(options.get("low_stage_lockout_enabled", False))
        lockout_temp_f = options.get("low_stage_lockout_temp_f")
        if lockout_enabled:
            if lockout_temp_f is None:
                raise ValueError("Dual-stage SEER2 low-stage lockout temperature is required")
            lockout_temp_f = float(lockout_temp_f)

        total_cooling = 0.0
        total_energy = 0.0
        details = []
        for index, (temp_f, fraction) in enumerate(zip(_BIN_TEMPS_F, _FRACTIONAL_HOURS), 1):
            building_load = ((temp_f - 65.0) / 30.0) * (q_a / 1.1)
            q_low = linear_interpolate(temp_f, 67.0, q_f_low, 82.0, q_b_low)
            p_low = linear_interpolate(temp_f, 67.0, p_f_low, 82.0, p_b_low)
            q_full = linear_interpolate(temp_f, 82.0, q_b, 95.0, q_a)
            p_full = linear_interpolate(temp_f, 82.0, p_b, 95.0, p_a)
            low_permitted = not (
                lockout_enabled and temp_f >= float(lockout_temp_f)
            )

            clf_low = clf_full = plf = None
            if low_permitted and building_load <= q_low:
                case = 1
                clf_low = safe_div(building_load, q_low)
                plf = 1.0 - cd_low_used * (1.0 - clf_low)
                cooling = clf_low * q_low * fraction
                energy = safe_div(clf_low * p_low * fraction, plf)
            elif low_permitted and building_load < q_full:
                case = 2
                clf_low = safe_div(q_full - building_load, q_full - q_low)
                clf_full = 1.0 - clf_low
                cooling = (clf_low * q_low + clf_full * q_full) * fraction
                energy = (clf_low * p_low + clf_full * p_full) * fraction
            elif building_load < q_full:
                case = 3
                clf_full = safe_div(building_load, q_full)
                plf = 1.0 - cd_full_used * (1.0 - clf_full)
                cooling = clf_full * q_full * fraction
                energy = safe_div(clf_full * p_full * fraction, plf)
            else:
                case = 4
                cooling = q_full * fraction
                energy = p_full * fraction

            total_cooling += max(0.0, cooling)
            total_energy += max(0.0, energy)
            details.append(
                {
                    "bin": index,
                    "bin_no": index,
                    "temp_F": temp_f,
                    "fractional_hours": fraction,
                    "building_load": building_load,
                    "q_low": q_low,
                    "p_low": p_low,
                    "q_full": q_full,
                    "p_full": p_full,
                    "low_permitted": low_permitted,
                    "operating_case": f"Case {case}",
                    "case": case,
                    "CLF_low": clf_low,
                    "CLF_full": clf_full,
                    "PLF": plf,
                    "q_j": cooling,
                    "E_j": energy,
                }
            )

        if total_energy <= 0:
            raise ValueError("Dual-stage SEER2 total energy must be positive")
        raw = total_cooling / total_energy
        published = round_nearest_005(raw)
        return {
            "SEER2": published,
            "raw_seer2": raw,
            "published_seer2": published,
            "presentation_value": published,
            "total_cooling_Btu": total_cooling,
            "total_energy_Wh": total_energy,
            "total_compressor_energy_wh": total_energy,
            "total_resistance_energy_wh": 0.0,
            "system_type": system_type,
            "product_classification": DUAL_STAGE,
            "bin_details": details,
            "summary": {
                "metadata": {
                    "formula_path": "ahri_210_240_2026_dual_stage_cooling",
                    "product_classification": DUAL_STAGE,
                    "cd_low_used": cd_low_used,
                    "cd_full_used": cd_full_used,
                    "low_stage_lockout_enabled": lockout_enabled,
                    "low_stage_lockout_temp_f": lockout_temp_f,
                    "p_w_off": float(p_w_off),
                }
            },
        }

    @staticmethod
    def _effective_cd(value: object) -> float:
        if value is None:
            return _DEFAULT_CD
        parsed = float(value)
        if parsed < 0:
            raise ValueError("Degradation coefficient must be non-negative")
        return min(parsed, _DEFAULT_CD)

    @staticmethod
    def _positive_point(test_points: Mapping[str, object], aliases: tuple[str, ...]) -> tuple[float, float]:
        lowered = {str(key).casefold(): value for key, value in test_points.items()}
        value = None
        for alias in aliases:
            if alias in test_points:
                value = test_points[alias]
                break
            value = lowered.get(alias.casefold())
            if value is not None:
                break
        if not isinstance(value, (tuple, list)) or len(value) != 2:
            raise ValueError(f"Missing dual-stage SEER2 test point: {aliases[0]}")
        capacity, power = float(value[0]), float(value[1])
        if capacity <= 0 or power <= 0:
            raise ValueError(
                f"Invalid dual-stage SEER2 point {aliases[0]}: capacity={capacity}, power={power}"
            )
        return capacity, power
