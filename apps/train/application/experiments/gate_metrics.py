"""Candidate metric and complexity evidence projection helpers."""

from __future__ import annotations

import math
from statistics import mean


def numeric_evidence(value):  # noqa: ANN001, ANN202
    if type(value) not in {int, float}:
        return {"status": "missing", "value": None}
    try:
        numeric = float(value)
    except OverflowError:
        return {"status": "non_finite", "value": None}
    if not math.isfinite(numeric):
        return {"status": "non_finite", "value": None}
    return {"status": "available", "value": numeric}


def finite_number(value):  # noqa: ANN001, ANN202
    return numeric_evidence(value)["value"]


def sanitize_non_finite(value):  # noqa: ANN001, ANN202
    if isinstance(value, dict):
        return {
            key: sanitize_non_finite(item)
            for key, item in value.items()
        }
    if isinstance(value, (list, tuple)):
        return [sanitize_non_finite(item) for item in value]
    if type(value) is float and not math.isfinite(value):
        return None
    return value


def primary_metric_summary(
    completed, targets, metric, baseline  # noqa: ANN001
):  # noqa: ANN202
    identities = list(targets) or sorted(completed)
    current_evidence = _target_evidence(completed, identities, metric)
    baseline_evidence = _target_evidence(baseline, identities, metric)
    current = _complete_mean(current_evidence)
    prior = _complete_mean(baseline_evidence)
    delta = _finite_difference(current, prior)
    comparable = current is not None and prior is not None and delta is not None
    return {
        "metric": metric,
        "value": current,
        "baseline_value": prior,
        "delta": delta if comparable else None,
        "comparable": comparable,
        "status": "available" if current is not None else "unavailable",
        "current_evidence": current_evidence,
        "baseline_evidence": baseline_evidence,
        "unavailable_context": _unavailable_context(
            current_evidence, source="candidate"
        ),
        "comparison_context": _comparison_context(
            current, prior, delta, baseline_evidence
        ),
    }


def mean_feature_count(completed):  # noqa: ANN001, ANN202
    evidence = [
        numeric_evidence(item.get("rfecv", {}).get("feature_count_after"))
        for item in completed.values()
    ]
    return _complete_mean(evidence)


def target_metric_changes(completed, baseline):  # noqa: ANN001, ANN202
    changes = {}
    for identity, target in sorted(completed.items()):
        current = target.get("metrics", {})
        prior = baseline.get(identity, {}).get("metrics", {})
        metrics = {}
        for name, value in sorted(current.items()):
            if type(value) not in {int, float}:
                continue
            baseline_value = prior.get(name)
            current_evidence = numeric_evidence(value)
            baseline_evidence = numeric_evidence(baseline_value)
            delta = _finite_difference(
                current_evidence["value"], baseline_evidence["value"]
            )
            metrics[name] = {
                "value": current_evidence["value"],
                "value_status": current_evidence["status"],
                "baseline_value": baseline_evidence["value"],
                "baseline_status": baseline_evidence["status"],
                "delta": delta,
                "comparison_status": (
                    "available"
                    if delta is not None else "unavailable"
                ),
            }
        changes[identity] = metrics
    return changes


def _target_evidence(targets, identities, metric):  # noqa: ANN001, ANN202
    return [
        {
            "target": identity,
            "metric": metric,
            **numeric_evidence(
                targets.get(identity, {}).get("metrics", {}).get(metric)
            ),
        }
        for identity in identities
    ]


def _complete_mean(evidence):  # noqa: ANN001, ANN202
    if not evidence or any(item["status"] != "available" for item in evidence):
        return None
    return finite_number(mean(item["value"] for item in evidence))


def _finite_difference(current, prior):  # noqa: ANN001, ANN202
    if current is None or prior is None:
        return None
    return finite_number(current - prior)


def _unavailable_context(evidence, *, source):  # noqa: ANN001, ANN202
    return [
        {
            "source": source,
            "target": item["target"],
            "metric": item["metric"],
            "reason": item["status"],
        }
        for item in evidence
        if item["status"] != "available"
    ]


def _comparison_context(current, prior, delta, evidence):  # noqa: ANN001, ANN202
    context = _unavailable_context(evidence, source="baseline")
    if current is not None and prior is not None and delta is None:
        context.append({
            "source": "comparison",
            "reason": "non_finite_delta",
        })
    return context
