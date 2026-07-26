"""Configured guardrail and instability evidence helpers."""

from __future__ import annotations

from statistics import mean

from .gate_metrics import finite_number, numeric_evidence


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
        current_evidence = _metric_evidence(
            completed, item["target"], item["metric"]
        )
        baseline_evidence = _metric_evidence(
            baseline, item["target"], item["metric"]
        )
        current = current_evidence["value"]
        prior = baseline_evidence["value"]
        degradation = None
        violated = False
        unresolved_context = _unresolved_context(
            item, current_evidence, baseline_evidence
        )
        if current is not None and prior is not None:
            degradation = finite_number(
                prior - current if item["direction"] == "higher" else current - prior
            )
            if degradation is None:
                unresolved_context.append({
                    "source": "comparison",
                    "target": item["target"],
                    "metric": item["metric"],
                    "reason": "non_finite_degradation",
                })
            else:
                violated = degradation > float(item["max_degradation"])
        status = (
            "unresolved"
            if unresolved_context
            else "violated" if violated else "passed"
        )
        entries.append({**item, "value": current, "baseline_value": prior,
                        "degradation": degradation, "violation": violated,
                        "status": status,
                        "value_status": current_evidence["status"],
                        "baseline_status": baseline_evidence["status"],
                        "unresolved_context": unresolved_context})
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
        evidence = _metric_evidence(
            completed, item["target"], f"{item['metric']}_std"
        )
        value = evidence["value"]
        violated = value is not None and value > float(item["max_std"])
        unresolved_context = (
            []
            if evidence["status"] == "available"
            else [{
                "source": "candidate",
                "target": item["target"],
                "metric": f"{item['metric']}_std",
                "reason": evidence["status"],
            }]
        )
        entries.append({**item, "value": value, "violation": violated,
                        "status": (
                            "unresolved" if value is None
                            else "violated" if violated else "passed"
                        ),
                        "value_status": evidence["status"],
                        "unresolved_context": unresolved_context})
    available = [item["value"] for item in entries if item["value"] is not None]
    return {
        **_aggregate(entries),
        "aggregate_std": (
            finite_number(mean(available)) if available else None
        ),
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
        "unresolved_context": [
            context
            for item in entries
            for context in item.get("unresolved_context", ())
        ],
    }


def _metric_evidence(targets, identity, metric):  # noqa: ANN001, ANN202
    value = targets.get(identity, {}).get("metrics", {}).get(metric)
    return numeric_evidence(value)


def _unresolved_context(item, current, baseline):  # noqa: ANN001, ANN202
    context = []
    for source, evidence in (("candidate", current), ("baseline", baseline)):
        if evidence["status"] != "available":
            context.append({
                "source": source,
                "target": item["target"],
                "metric": item["metric"],
                "reason": evidence["status"],
            })
    return context
