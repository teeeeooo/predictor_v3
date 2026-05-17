# 066 Guard Calculator Schema Boundaries

## Goal

Add automated guard tests so UI/ML/schema concepts do not leak into core calculator modules or region configs.

## Scope

- `tests/test_calculator_schema_boundaries.py`

## Non-goals

- No adapter feature expansion.
- No calculator logic changes.
- No region config value changes.

## Changed Files

- `tests/test_calculator_schema_boundaries.py`
- `result_reports/active/066_guard-calculator-schema-boundaries.md`

## Verification

- `python3 -B -m py_compile tests/test_calculator_schema_boundaries.py`
  - passed
- `python3 -B -m pytest tests/test_calculator_schema_boundaries.py tests/test_calculator_result_adapter.py -q`
  - `7 passed`

## Task Results

- Added AST import guard coverage for `core/calculator_*.py`.
- Banned calculator imports now include UI modules, `core.models`, `MODEL_REGISTRY`, `COLUMNS`, and the numeric/ML stack roots `numpy`, `pandas`, and `sklearn`.
- Added JSON key guard coverage for `data/region_configs/*.json` to reject runtime/ML result keys such as `candidate`, `prediction`, `model_version`, and `raw_result`.
- Added an adapter-term guard so envelope/runtime terms such as `PredictedPointsEnvelope`, `CalculatorInputEnvelope`, `CalculatorResultEnvelope`, `RankingCandidateEnvelope`, `raw_result`, `model_version`, and `prediction` stay out of core calculator files except `core/calculator_result_adapter.py`.

## Known Risks

- The plain word `candidate` is not banned in calculator source because existing calculators use it as an algorithmic local variable. Region configs still ban exact runtime key `candidate`.
- The guard is structural; it does not prove semantic correctness of adapter conversion.

## Commit / Push

- Source commit: `8212045` (`test: guard calculator schema boundaries`).
- Report commit: this commit (`report: record calculator schema boundary guards`).
- Push: deferred until final objective push.
