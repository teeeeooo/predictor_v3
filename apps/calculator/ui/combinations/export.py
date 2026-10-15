"""Concise result CSV projection; detailed provenance remains in the detail view."""
from dataclasses import asdict
import json
from .presentation import point_title

# User-facing result measures only: exclude input settings, duplicate aliases,
# rounded/raw copies of the ranked metric, and interpolation diagnostics.
EXTRA_RESULTS = {
    "iso": ("annual_cooling_kwh", "annual_power_kwh"),
    "hong_kong_cspf": ("annual_cooling_kwh", "annual_power_kwh"),
    "hong_kong_hspf": ("hstl_wh", "hsec_wh", "heat_pump_energy_wh", "auxiliary_energy_wh"),
    "saso": ("annual_cooling_kwh", "annual_power_kwh"),
    "korea_cspf": ("annual_cooling_kwh", "annual_power_kwh"),
    "korea_hspf": ("hstl", "hsec", "heat_pump_energy", "auxiliary_energy"),
    "brazil": ("two_point_cspf", "rule_1", "rule_2", "final"),
    "en_seer": ("seer_on", "qc_kwh"),
    "en_scop": ("scop_on", "qh_kwh", "active_kwh", "standby_kwh", "total_kwh"),
    "m_seer": ("seasonal_cooling_numerator", "seasonal_energy_denominator"),
    "m_hspf": ("seasonal_heating_load_numerator", "seasonal_compressor_energy_denominator",
               "seasonal_resistance_energy_denominator"),
    "seer2": ("EER2_A_Full", "EER2_B_Low", "total_cooling_Btu", "total_energy_Wh",
              "total_compressor_energy_wh", "total_resistance_energy_wh"),
    "hspf2": ("total_heating_btu", "total_energy_wh", "total_compressor_energy_wh", "total_resistance_energy_wh"),
}


def context_json(snapshot):
    return json.dumps({"context": asdict(snapshot.context), "points": [asdict(p) for p in snapshot.points]},
                      ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def measurement_headers(point):
    label = point_title(point)
    return (f"{label} 성능 [{point.capacity_unit}]", f"{label} 전력 [W]")


def export_filename(run, *, stale):
    suffix = ("_partial" if run.partial else "") + ("_stale" if stale else "")
    basis = run.snapshot.context.basis
    if basis != "public":
        suffix += "_" + basis
    return f"calculator_combinations{suffix}.csv"


def export_rows(run):
    snapshot = run.snapshot
    present = {key for row in run.results if row.score for key, _ in row.score.summary}
    extras = tuple(key for key in EXTRA_RESULTS[snapshot.context.kind] if key in present)
    errors = any(row.score is None for row in run.results)
    headers = ("순위", "값", "지표", *(header for point in snapshot.independent_points
               for header in measurement_headers(point)), *extras, *(("오류",) if errors else ()))
    rows = []
    for rank, row in run.ranked():
        score = row.score
        values = [rank, score.value if score else None, score.metric if score else run.adapter.metric(snapshot.context)]
        for pool, index in zip(snapshot.pools, row.selections):
            measurement = pool[index]
            values.extend((measurement.capacity, measurement.power))
        summary = dict(score.summary) if score else {}
        values.extend(summary.get(key) for key in extras)
        if errors:
            values.append(f"{row.error_code}: {row.error_message}" if not score else "")
        rows.append(tuple("" if value is None else str(value) for value in values))
    return headers, tuple(rows)
