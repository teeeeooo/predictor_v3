"""Stable ISO 16358 HSPF result and diagnostics assembly."""

from __future__ import annotations


def assemble_common_hspf_result(hstl: float, hsec: float, bin_details: list) -> dict:
    if hsec <= 0:
        return {
            "hspf": 0.0,
            "hstl_wh": hstl,
            "hsec_wh": hsec,
            "heat_pump_energy_wh": 0.0,
            "auxiliary_energy_wh": 0.0,
            "bin_details": bin_details,
        }
    hspf_value = hstl / hsec
    heat_pump_energy = sum(item["heat_pump_energy"] for item in bin_details)
    auxiliary_energy = sum(item["auxiliary_energy"] for item in bin_details)
    return {
        "hspf": round(hspf_value, 3),
        "hstl_wh": hstl,
        "hsec_wh": hsec,
        "heat_pump_energy_wh": heat_pump_energy,
        "auxiliary_energy_wh": auxiliary_energy,
        "bin_details": bin_details,
    }
