# 542 Arc 9 Prediction Adapter Recovery

## Goal

Recover PySide6 Predict row-to-ML input conversion and prediction result
mapping against the current core schema and ML owner contracts.

## Changes

- `RowToMlInputAdapter` now derives direct numeric feature mapping from
  `build_input_column_schema()` and `COLUMNS[*].ml_feature`.
- Recovered legacy one-hot intent:
  - `ref_type`: `R410A`, `R32`, `R290`
  - `exp_type`: `EEV`, `Capi`
- Added controlled row validation for missing or non-numeric cooling capacity.
- Added `build_prediction_input_request()` import-smoke helper for the default
  adapter path.
- `PredictionResultAdapter` now derives result target mapping from result
  schema `ml_target` metadata and `core.ml.features.TARGETS`.
- Missing prediction targets become controlled `partial` result rows with a
  concise message instead of crashing.
- Removed runtime import of `PredictionServiceResult` from the result adapter
  to avoid an adapter/service circular import.
- Added focused adapter tests for row-to-ML parity, one-hot encoding, result
  target mapping, partial target handling, and missing model failure.

## Boundary Decision

- Table models do not perform ML feature conversion.
- Prediction service continues to call `core.ml.inference` and
  `core.ml.artifacts` package owner paths directly.
- Adapter conversion remains Qt-free and does not call model `.predict()`.
- Synchronous controller execution remains unchanged; worker/progress/cancel is
  deferred to Arc 10.

## Validation Notes

- `model/model.pkl` is absent in this checkout, so real prediction success is
  not validated. Missing artifact behavior is covered as a controlled service
  error.

## UI/UX Contract Check

- Result lookup remains internal `case_id` based.
- User-facing row identity remains row headers.
- Table parity gaps remain intentionally deferred: TSV copy, TSV paste,
  Delete/Backspace clear, grouped undo, Tab/Enter navigation,
  click/type replace-on-type, dropdown delegate rendering, and validation
  rendering.

## Verification

- `python3 -B -m py_compile apps/predict/**/*.py`
- `python3 -B -c "from apps.predict.adapters.row_to_ml_input_adapter import build_prediction_input_request"`
- `python3 -B -c "from apps.predict.adapters.prediction_result_adapter import apply_prediction_result"`
- `python3 -B -c "from apps.predict.services.prediction_service import PredictionService; from core.ml.artifacts import MODEL_FILE; s=PredictionService(model_file=MODEL_FILE); assert s is not None"`
- `python3 -B -m pytest tests/test_apps_predict_prediction_adapters.py tests/test_apps_predict_table_models.py tests/test_apps_predict_mapping_controller.py`
- `git diff --check`
- `git status --short`

## Excluded Scope

- No ML algorithm, feature list, target list, preprocessing formula, model
  artifact, mapping JSON schema, calculator formula/config/fixture/golden, or
  public result contract changes.
- No worker/progress/cancel implementation.
- No Trainer foundation implementation.
- No legacy PyQt behavior refactor.

## Next Action

Arc 9 Slice 6 - PredictWorkspace integration smoke and Arc 9 closeout.
