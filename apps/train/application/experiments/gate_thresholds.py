"""Configured guardrail and instability evidence helpers."""

from __future__ import annotations

from statistics import mean


def guardrail_evidence(completed, baseline, thresholds):  # noqa: ANN001, ANN202
    if not thresholds:
        return {
            "configured": False,
            "status": "not_configured",
            "violation": False,
            "unresolved": False,
            "entries": [],
        }
    entries = []
    for item in thresholds:
        current = _metric(completed, item["target"], item["metric"])
        prior = _metric(baseline, item["target"], item["metric"])
        degradation = None
        violated = False
        if current is not None and prior is not None:
            degradation = (
                prior - current if item["direction"] == "higher" else current - prior
            )
            violated = degradation > float(item["max_degradation"])
        status = (
            "unresolved"
            if current is None or prior is None
            else "violated" if violated else "passed"
        )
        entries.append({**item, "value": current, "baseline_value": prior,
                        "degradation": degradation, "violation": violated,
                        "status": status})
    return _aggregate(entries)


def stability_evidence(completed, thresholds):  # noqa: ANN001, ANN202
    if not thresholds:
        return {
            "configured": False,
            "status": "not_configured",
            "violation": False,
            "unresolved": False,
            "entries": [],
            "aggregate_std": None,
        }
    entries = []
    for item in thresholds:
        value = _metric(completed, item["target"], f"{item['metric']}_std")
        violated = value is not None and value > float(item["max_std"])
        entries.append({**item, "value": value, "violation": violated,
                        "status": (
                            "unresolved" if value is None
                            else "violated" if violated else "passed"
                        )})
    available = [item["value"] for item in entries if item["value"] is not None]
    return {
        **_aggregate(entries),
        "aggregate_std": mean(available) if available else None,
    }


def _aggregate(entries):  # noqa: ANN001, ANN202
    violation = any(item["violation"] for item in entries)
    unresolved = any(item["status"] == "unresolved" for item in entries)
    return {
        "configured": True,
        "status": (
            "violated" if violation else "unresolved" if unresolved else "passed"
        ),
        "violation": violation,
        "unresolved": unresolved,
        "entries": entries,
    }


def _metric(targets, identity, metric):  # noqa: ANN001, ANN202
    value = targets.get(identity, {}).get("metrics", {}).get(metric)
    return float(value) if isinstance(value, (int, float)) else None
