"""Candidate metric and complexity evidence projection helpers."""

from __future__ import annotations

from statistics import mean


def primary_metric_summary(
    completed, targets, metric, baseline  # noqa: ANN001
):  # noqa: ANN202
    identities = list(targets) or sorted(completed)
    values = [
        float(completed[item]["metrics"][metric])
        for item in identities
        if item in completed
        and isinstance(completed[item].get("metrics", {}).get(metric), (int, float))
    ]
    baseline_values = [
        float(baseline[item]["metrics"][metric])
        for item in identities
        if item in baseline
        and isinstance(baseline[item].get("metrics", {}).get(metric), (int, float))
    ]
    current = mean(values) if values else None
    prior = (
        mean(baseline_values)
        if len(baseline_values) == len(values) and values else None
    )
    return {
        "metric": metric,
        "value": current,
        "baseline_value": prior,
        "delta": (
            current - prior
            if current is not None and prior is not None else None
        ),
        "comparable": prior is not None,
    }


def mean_feature_count(completed):  # noqa: ANN001, ANN202
    values = [
        item.get("rfecv", {}).get("feature_count_after")
        for item in completed.values()
    ]
    numeric = [float(item) for item in values if isinstance(item, (int, float))]
    return mean(numeric) if numeric else None


def target_metric_changes(completed, baseline):  # noqa: ANN001, ANN202
    changes = {}
    for identity, target in sorted(completed.items()):
        current = target.get("metrics", {})
        prior = baseline.get(identity, {}).get("metrics", {})
        metrics = {}
        for name, value in sorted(current.items()):
            if not isinstance(value, (int, float)):
                continue
            baseline_value = prior.get(name)
            metrics[name] = {
                "value": float(value),
                "baseline_value": (
                    float(baseline_value)
                    if isinstance(baseline_value, (int, float)) else None
                ),
                "delta": (
                    float(value) - float(baseline_value)
                    if isinstance(baseline_value, (int, float)) else None
                ),
            }
        changes[identity] = metrics
    return changes
