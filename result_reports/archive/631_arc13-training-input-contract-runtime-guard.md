# 631 Arc 13 Training Input Contract Runtime Guard

## Goal

Connect the ML feature catalog contract to runtime training and inference
guards without changing ML algorithms, training parameters, or model artifact
schema.

## Changed Files

- `core/ml/inference.py`
- `core/ml/training.py`
- `tests/test_ml_feature_catalog.py`
- `docs/WORK_PLAN.md`
- `project_brief.md`
- `project_log.md`
- `result_reports/active/631_arc13-training-input-contract-runtime-guard.md`

## Training Guard Point

Training data is loaded in `core.ml.training.train_all_models()` through
`load_and_preprocess()`. The guard is now attached immediately after DataFrame
load/preprocessing and before any `MODEL_REGISTRY` loop, `prepare_pipeline()`,
RFE, Optuna, XGBoost fitting, artifact writing, or training log export.

The train job already surfaces exceptions through its structured result path,
so no Train UI layout or job protocol change was required.

## Training Header Runtime Guard

`core.ml.training.validate_training_input_headers()` validates the loaded
DataFrame columns against the catalog training header contract:

- raw training columns must use `config/ml/features.csv` `ml_name` values;
- unknown headers fail with a clear message;
- missing required headers fail with a clear message;
- derived feature names are not required as raw training headers;
- no alias/header mapping was added.

## Zero-fill Policy Tightening

`core.ml.inference.build_input_df()` now loads validated catalog
`zero_fill_policy` values and only fills missing features marked
`mode_missing_allowed`.

Current allowed missing features:

- `Cooling Capa`
- `Cooling Power`
- `Heating Capa`
- `Heating Power`

All other missing `BASE_FEATURES` names fail fast with a message that includes
the missing feature names and the `config/ml/features.csv` `zero_fill_policy`
boundary.

For normal `predict_row()` execution, the guard is applied to the model
artifact's actual required base features plus raw dependencies needed to
compute selected derived features. Direct `build_input_df()` calls keep the
strict full-`BASE_FEATURES` default.

## Behavior Impact

This slice intentionally changes runtime guard behavior:

- Training data with headers outside catalog `ml_name` values now fails before
  fitting.
- Training data missing required catalog training headers now fails before
  fitting.
- Prediction input no longer silently fills non-allowed missing base features
  with `0.0`.
- Cooling/heating mode-missing capacity/power compatibility remains preserved
  for the four catalog-approved names.

No ML algorithm, Optuna/RFE/XGBoost parameter, model artifact schema, predictor
schema contract, predict UI behavior, train UI layout, mapping schema, or
calculator code changed.

## Read Ledger

- `core/ml/inference.py`: full file, reason: missing feature zero-fill behavior
  owner.
- `core/ml/training.py`: full file, reason: training DataFrame load and
  training entry boundary.
- `core/ml/preprocessing.py`: full file, reason: training DataFrame load and
  feature/target preparation path.
- `apps/train/jobs/train_job.py`: full file, reason: validation error
  surfacing check.
- `apps/train/services/training_service.py`: full file, reason: request
  validation boundary check.
- `config/ml/features.csv`: full small file, reason: zero-fill and training
  header policy.
- `tests/test_ml_feature_catalog.py`: focused file, reason: catalog/training
  guard and inference guard tests.
- `result_reports/active/630_arc13-one-hot-adapter-projection-from-catalog.md`:
  focused file, reason: prior Slice 5 handoff risk.
- `docs/WORK_PLAN.md`, `project_brief.md`, `project_log.md`: targeted Arc 13
  status sections.
- broad read: none.

## change_gate

```yaml
change_gate:
  new_source: none
  hotspot_delta: wiring-only
  code_map_check: regenerated
  ui_literal_exemption: none
  reuse_commonization: checked
  report_exemption: none
  read_ledger: included
```

Existing catalog validation/projection helpers were reused. The runtime
behavior change is a policy guard at existing training and inference
boundaries, not a new training flow or algorithm path.

## Known Risks / Open Questions

- Existing production training datasets must use catalog `ml_name` headers.
- Prediction callers that relied on silent `0.0` fill for non-mode features
  must now provide those features explicitly.
- Packaging/workflow checks around catalog presence remain for Arc 13 Slice 6.

## Next Action

Arc 13 Slice 6 - Catalog Guard / Packaging / Workflow Hardening.

## Verification

- `python3 -B -m compileall -q core/ml tests/test_ml_feature_catalog.py`: OK.
- `python3 -B -m pytest tests/test_ml_feature_catalog.py -q`: OK, 36
  passed.
- `python3 -B -m compileall -q core/ml apps/train apps/predict tests`: OK.
- `python3 -B -m pytest tests -k "feature_catalog"`: OK, 36 passed and
  1418 deselected.
- `python3 -B -m pytest tests -k "training or train or inference or ml"`:
  initially exposed a DEV mock Train execution smoke gap after strict
  inference guard; adjusted `predict_row()` to apply strict zero-fill policy to
  the artifact-required base features and derived dependencies. Final result:
  OK, 81 passed and 1373 deselected.
- `python3 -B -m pytest tests -k "predict_schema or prediction_adapter or prediction_usecase or apps_predict"`:
  OK, 132 passed and 1322 deselected.
- `python3 -B tools/code_checker/build_reference_map.py --check`: initially
  stale after source changes.
- `python3 -B tools/code_checker/build_reference_map.py`: regenerated
  `docs/code_map/CODEBASE_REFERENCE_MAP.md`.
- `python3 -B tools/code_checker/build_reference_map.py --check`: OK, fresh.
- `python3 -B tools/check_code_structure.py`: OK with pre-existing calculator
  soft warnings outside this slice.
- `git diff --check`: OK.
- `git status --short`: task files only before staging.

## Commit / Push

- pending

## Project Memory Delta

- type: decision
  topic: Arc 13 training and inference catalog runtime guard
  content: Training data headers now fail fast against feature catalog
    `ml_name` values before fitting, and inference missing-feature zero fill is
    limited to catalog `mode_missing_allowed` features.
  keywords: arc13, feature-catalog, training-headers, inference, zero-fill
