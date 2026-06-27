# Design Gate Summary

## Goal

Define the calculator result envelope and ML adapter boundary before resuming ML / inverse-search work.

The immediate goal is a stable design contract, not an implementation. The design prevents ML feature schema, region config schema, HW candidate input, and calculator result schema from being reused as substitutes for each other.

## Confirmed Decisions

- `region config` remains static standard/region data only.
- `HW candidate input` remains runtime candidate or user-provided performance data.
- `ML feature schema` remains training/prediction input and target metadata.
- `calculator input` is built by an adapter from predicted or candidate performance points.
- `calculator result` remains owned by the calculator layer and can be wrapped by a normalized envelope outside the core calculator.
- Existing calculator public APIs and diagnostics keys are not changed in this design phase.
- UI and recommendation layers may consume normalized envelopes, but calculators must not import UI table schema or ML registry/schema.

## Core vs Handler Boundary

| Item | Core calculator | Adapter / UI / ML / recommendation | Reason |
| --- | --- | --- | --- |
| Region constants | Reads its own static config | Selects profile/config only | Calculator owns standard interpretation. |
| Predicted performance points | Does not know prediction source | Converts ML/candidate values into calculator input | ML output is evidence, not calculator schema. |
| Calculator public API | Stable for current callers | May wrap return dict after call | Avoid broad migration before adapter tests exist. |
| Result normalization | Returns current metric-specific dict | Creates normalized result envelope | Keeps compatibility while giving ranking a stable contract. |
| Ranking/recommendation | No ranking responsibility | Scores candidates from normalized envelopes | Calculator remains a metric evaluator. |

## Data Shape / API Boundary

### Flow

```text
ML output or HW candidate
-> PredictedPointsEnvelope
-> CalculatorInputEnvelope
-> core calculator call
-> CalculatorResultEnvelope
-> RankingCandidateEnvelope
```

### PredictedPointsEnvelope

```python
{
    "source": "ml_prediction" | "manual_candidate" | "fixture",
    "model_target": "cooling" | "heating" | "multi",
    "points": {
        "<point_id>": {
            "capacity": float,
            "power": float,
            "capacity_unit": "W" | "Btu/h" | "kW",
            "power_unit": "W" | "kW",
        }
    },
    "metadata": {
        "model_version": str | None,
        "candidate_id": str | None,
    },
}
```

### CalculatorInputEnvelope

```python
{
    "calculator_profile_id": str,
    "standard": str,
    "region": str,
    "mode": "cooling" | "heating",
    "metric": "CSPF" | "HSPF" | "SEER2" | "HSPF2" | "SCOP",
    "measured_inputs": {
        "<calculator_point_id>": {
            "capacity": float,
            "power": float,
        }
    },
    "options": dict,
}
```

`source` is intentionally not a top-level key in this envelope. Provenance
belongs on `PredictedPointsEnvelope`. The implementation copies the
upstream `source` value into `options["source"]` so the calculator input
layer carries the same vocabulary without re-asserting ownership of it.

### CalculatorResultEnvelope

```python
{
    "calculator_profile_id": str,
    "calculator_id": str,
    "metric": str,
    "value": float,
    "units": str,
    "raw_result": dict,
    "diagnostics": dict,
    "warnings": list[str],
}
```

### RankingCandidateEnvelope

```python
{
    "candidate_id": str,
    "predicted_points_ref": str,
    "calculator_result_ref": str,
    "score": float,
    "ranking_features": dict,
}
```

## Required Tests

- Adapter unit tests that map ML/manual candidate points into each supported calculator profile input without touching region config.
- Schema guard tests proving `core/calculator_*.py` does not import UI table schema or ML registry modules.
- Golden/smoke tests for existing calculator APIs to prove adapter work does not change current result dicts.
- Ranking smoke tests that consume `CalculatorResultEnvelope` instead of raw calculator-specific dicts.

## Migration / Refactor Path

1. Add an adapter module candidate such as `core/calculators/adapters/result_adapter.py` or `core/calculator_adapter.py` with pure conversion helpers only.
2. Wrap existing calculator outputs into `CalculatorResultEnvelope` without changing calculator public APIs.
3. Add ML/inverse-search caller code that consumes envelopes and keeps raw calculator output available under `raw_result`.
4. After callers migrate, consider whether any calculator return dict cleanup is still needed as a separate, approved schema migration.

## Risks

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Adapter silently changes units | Bad ranking or false regression | Store units per point/result and add conversion tests. |
| Envelope becomes a second public API too early | Premature compatibility burden | Keep it adapter-owned until ML/recommendation callers stabilize. |
| Raw calculator diagnostics are flattened incorrectly | Debugging loss | Preserve `raw_result` and `diagnostics` separately. |
| Region config absorbs candidate data | Config pollution and invalid calculator reuse | Guard with tests and docs: config stays static only. |

## Non-goals

- No ML / inverse-search implementation in this step.
- No calculator return schema migration.
- No region config schema change.
- No UI table schema change.
- No public API rename.

## Implementation Status (as of 2026-05-17 audit_5 task 2)

- `CalculatorResultEnvelope` first slice landed for `ahri_usa_seer2` in
  `core/calculators/adapters/result_adapter.py` (see report 065 / 071).
- `CalculatorInputEnvelope` first slice now matches the design shape above:
  `{calculator_profile_id, standard, region, mode, metric, measured_inputs,
  options}`, with `options` carrying `units` and `source`.
- `source` vocabulary is locked to `manual_candidate`, `ml_prediction`,
  `fixture` (legacy values `manual` / `predicted` are explicitly rejected).
- Unit conversion is intentionally out of scope: capacity must be `Btu/h`
  and power must be `W` for the AHRI SEER2 profile.
- Extra point keys, extra inner keys per point, extra unit keys, and
  options that re-define reserved keys all fail fast.
- A small helper `measured_inputs_as_test_points(envelope)` is exposed for
  callers that still need the legacy tuple form that
  `AHRICalculator.calculate_seer2` accepts; the calculator public API is
  unchanged.
- `PredictedPointsEnvelope` and `RankingCandidateEnvelope` remain
  design-only and are scheduled for follow-up slices.

## Next Codex Implementation Prompt

```text
Implement the calculator adapter first slice from docs/designs/2026-05-17-calculator-result-envelope-ml-adapter.md.
Keep core calculator public APIs unchanged.
Add pure adapter helpers that build CalculatorInputEnvelope and CalculatorResultEnvelope for one narrow profile path first, with unit tests and schema-coupling guard tests.
Do not modify region config semantics, ML feature registry, or UI table schema.
```
