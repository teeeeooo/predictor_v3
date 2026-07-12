"""ISO 16358-2 per-bin performance snapshot construction."""


class HSPFPerformanceSnapshotMixin:
    def _iso_hspf_has_non_frost_extended_candidate(self, resolved: dict) -> bool:
        return (
            "7_ext" in resolved
            and "-7_ext" in resolved
        )

    def _iso_hspf_has_frost_extended_candidate(self, resolved: dict) -> bool:
        return self._iso_hspf_has_extended_candidate(resolved) or (
            "-7_ext" in resolved and "2_ext_f" in resolved
        )

    def _iso_hspf_common_extended_frost_curve(
        self,
        tj: float,
        resolved: dict
    ) -> dict:
        ext_m7 = self._iso_hspf_extended_minus7_default(resolved)
        ext_2 = resolved.get("2_ext_f", resolved.get("2_ext"))
        return {
            "capacity": ext_m7["capacity"]
            + (ext_2["capacity"] - ext_m7["capacity"]) * (tj + 7.0) / 9.0,
            "power": ext_m7["power"]
            + (ext_2["power"] - ext_m7["power"]) * (tj + 7.0) / 9.0,
        }

    def _iso_hspf_common_stage_snapshot(
        self,
        tj: float,
        resolved: dict,
        active_stages: list,
        frost: bool
    ) -> dict:
        snapshot = {}
        for stage in ("min", "half", "full"):
            if stage not in active_stages:
                continue
            snapshot[stage] = {
                "capacity": self._iso_hspf_capacity_curve(
                    tj, stage, resolved, frost
                ),
                "power": self._iso_hspf_power_curve(tj, stage, resolved, frost),
            }

        if frost and self._iso_hspf_has_frost_extended_candidate(resolved):
            snapshot["ext"] = self._iso_hspf_common_extended_frost_curve(
                tj, resolved
            )
        elif (not frost) and self._iso_hspf_has_non_frost_extended_candidate(resolved):
            snapshot["ext"] = {
                "capacity": self._iso_hspf_capacity_curve(
                    tj, "ext", resolved, False
                ),
                "power": self._iso_hspf_power_curve(tj, "ext", resolved, False),
            }
        return snapshot
