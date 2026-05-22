"""Adapter-owned RankingCandidateEnvelope helpers.

This is the downstream counterpart to ``core.calculator_result_adapter``.
It accepts a validated ``CalculatorResultEnvelope`` and produces a
``RankingCandidateEnvelope`` that a ranking / inverse-search layer can
consume without ever touching raw calculator return dicts directly.

First slice scope (audit_5 task 5):

- Single-metric scoring only — ``score`` defaults to the envelope's
  ``value`` so the simplest ranking layer can sort by metric without
  extra logic.
- ``ranking_features`` is opaque to this adapter; callers own its shape.
- ``raw_result`` from the input envelope is intentionally not exposed in
  the output. Rankers must consume envelopes, not raw dicts.
- Only the result envelope's primary metric / value / units / profile_id
  are surfaced, plus a caller-supplied ``candidate_id``.

The richer design-doc fields (``predicted_points_ref``,
``calculator_result_ref``) are deferred until the ranking layer actually
needs back-references and a registry exists.
"""

from typing import Any, Dict, Mapping, Optional


_REQUIRED_RESULT_ENVELOPE_KEYS = ("calculator_profile_id", "metric", "value", "units")


def _validate_result_envelope(result_envelope: Mapping[str, Any]) -> None:
    if not isinstance(result_envelope, Mapping):
        raise TypeError("result_envelope must be a mapping")
    missing = [key for key in _REQUIRED_RESULT_ENVELOPE_KEYS if key not in result_envelope]
    if missing:
        raise KeyError(
            f"result_envelope is missing required keys: {missing}. "
            f"Did you wrap the raw calculator result with "
            f"wrap_calculator_result_envelope first?"
        )


def _validate_candidate_id(candidate_id: str) -> str:
    if not isinstance(candidate_id, str) or not candidate_id.strip():
        raise ValueError("candidate_id must be a non-empty string")
    return candidate_id


def _validate_ranking_features(ranking_features: Optional[Mapping[str, Any]]) -> Dict[str, Any]:
    if ranking_features is None:
        return {}
    if not isinstance(ranking_features, Mapping):
        raise TypeError("ranking_features must be a mapping when provided")
    return dict(ranking_features)


def build_ranking_candidate_envelope(
    candidate_id: str,
    result_envelope: Mapping[str, Any],
    score: Optional[float] = None,
    ranking_features: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    """Build a RankingCandidateEnvelope from a CalculatorResultEnvelope.

    Args:
        candidate_id: Caller-provided non-empty string identifying the
            candidate that produced the calculator result.
        result_envelope: A validated CalculatorResultEnvelope mapping that
            already contains ``calculator_profile_id``, ``metric``,
            ``value``, and ``units``.
        score: Optional override for the ranking score. Defaults to the
            envelope's ``value`` so a single-metric ranking layer can sort
            without extra logic.
        ranking_features: Optional dict that the ranking layer owns. Copied
            into the output envelope as-is.

    Returns:
        Dict matching the first slice ranking envelope shape:

        ``{candidate_id, calculator_profile_id, metric, value, units,
        score, ranking_features}``

    Raises:
        TypeError: if ``result_envelope`` or ``ranking_features`` are not
            mappings when expected.
        KeyError: if ``result_envelope`` is missing required keys.
        ValueError: if ``candidate_id`` is empty / not a string.
    """
    resolved_candidate_id = _validate_candidate_id(candidate_id)
    _validate_result_envelope(result_envelope)
    resolved_features = _validate_ranking_features(ranking_features)

    metric_value = float(result_envelope["value"])
    resolved_score = float(score) if score is not None else metric_value

    return {
        "candidate_id": resolved_candidate_id,
        "calculator_profile_id": result_envelope["calculator_profile_id"],
        "metric": result_envelope["metric"],
        "value": metric_value,
        "units": result_envelope["units"],
        "score": resolved_score,
        "ranking_features": resolved_features,
    }
