"""Stable EN 14825 public result and diagnostics assembly."""

from __future__ import annotations


def assemble_seer_result(seer: float, seer_on: float, qc_kwh: float) -> dict:
    return {
        "seer": round(seer, 3),
        "seer_on": round(seer_on, 3),
        "qc_kwh": round(qc_kwh, 2),
    }


def assemble_scop_result(
    *,
    scop: float,
    scop_on: float,
    q_h: float,
    active_kwh: float,
    standby_kwh: float,
    total_kwh: float,
    climate_key: str,
    appliance_type: str,
    p_design_h: float,
    operational_hours: dict,
    source: dict,
    bin_details: list,
) -> dict:
    rounded_scop = round(scop, 3)
    return {
        "scop": rounded_scop,
        "SCOP": rounded_scop,
        "scop_on": round(scop_on, 3),
        "qh_kwh": round(q_h, 3),
        "active_kwh": round(active_kwh, 3),
        "standby_kwh": round(standby_kwh, 3),
        "total_kwh": round(total_kwh, 3),
        "climate": climate_key,
        "appliance_type": appliance_type,
        "p_design_h": p_design_h,
        "operational_hours": operational_hours,
        "source": source,
        "bin_details": bin_details,
        "unimplemented_notes": [
            "The current API treats user-entered A/B/C/D/TOL/Tbiv capacity and power as already resolved part-load declared points for EN 14825 Clause 7.4.",
            "If raw capacity-control step data is required, Clause 7.4.2.2 variable-capacity closest-step and +/-10% logic needs an expanded input schema.",
            "SCOPnet from Equation (10) is not returned because the requested output is SCOP.",
        ],
    }
