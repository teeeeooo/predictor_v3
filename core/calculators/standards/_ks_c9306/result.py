"""Stable KS C 9306 CSPF/HSPF result assembly."""

from __future__ import annotations


def assemble_cspf_result(cstl: float, csec: float, bin_details: list) -> dict:
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


def assemble_hspf_result(hstl: float, hsec: float, bin_details: list) -> dict:
    if hsec <= 0:
        return {
            "hspf": 0.0,
            "HSPF": 0.0,
            "rounded_hspf": 0.0,
            "HSTL": hstl,
            "HSEC": hsec,
            "bin_details": bin_details,
        }
    hspf_value = hstl / hsec
    heat_pump_energy = sum(
        item.get("heat_pump_energy", item.get("compressor_energy", 0.0))
        for item in bin_details
    )
    auxiliary_energy = sum(
        item.get("auxiliary_energy", 0.0) for item in bin_details
    )
    return {
        "hspf": hspf_value,
        "HSPF": hspf_value,
        "rounded_hspf": round(hspf_value, 3),
        "hstl": hstl,
        "HSTL": hstl,
        "hsec": hsec,
        "HSEC": hsec,
        "heat_pump_energy": heat_pump_energy,
        "auxiliary_energy": auxiliary_energy,
        "bin_details": bin_details,
    }
