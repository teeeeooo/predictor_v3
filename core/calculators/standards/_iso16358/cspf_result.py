"""ISO 16358-1 CSPF result assembly."""


class CSPFResultMixin:
    def _build_cspf_result(self, cstl: float, csec: float, bin_details: list) -> dict:
        if csec <= 0:
            return {
                "cspf": 0.0,
                "annual_cooling_kwh": 0.0,
                "annual_power_kwh": 0.0,
                "bin_details": bin_details,
            }
        return {
            "cspf": round(cstl / csec, 3),
            "annual_cooling_kwh": round(cstl / 1000.0, 3),
            "annual_power_kwh": round(csec / 1000.0, 3),
            "bin_details": bin_details,
        }
