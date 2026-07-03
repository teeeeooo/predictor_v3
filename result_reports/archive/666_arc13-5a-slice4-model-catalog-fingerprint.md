# Arc 13.5A Slice 4 - Model Catalog Fingerprint Guard

## Goal

Guard prediction against model artifacts trained with a different Feature Catalog.

## Scope

- Added `core/ml/catalog_fingerprint.py` as the fingerprint owner.
- Attached current Feature Catalog fingerprint metadata to real training artifacts.
- Attached the same metadata to DEV/mock prediction artifacts.
- Added `load_model()` validation for missing or mismatched catalog fingerprint.
- Added PredictionService coverage for mismatch blocking.
- Updated stale Train shell smoke expected tabs to include the existing Feature Catalog tab.

## Non-goals Held

- No ML algorithm, tuning, or feature engineering changes.
- No training quality changes.
- No Predict UI rewrite.

## Verification

- `python3 -m compileall core/ml apps/predict apps/train tools/dev/mock_smoke tests/test_ml_feature_catalog.py tests/test_apps_train_training_service.py tests/test_mock_smoke_generators.py tests/test_apps_predict_prediction_service_status.py` - OK
- `python3 -m pytest tests/test_ml_feature_catalog.py tests/test_apps_train_training_service.py tests/test_mock_smoke_generators.py tests/test_apps_predict_prediction_service_status.py` - OK, 70 passed
- `git diff --check` - OK
- `python3 -B tools/check_code_structure.py --verbose` - NG, pre-existing unrelated raw hex literal:
  - `apps/calculator/ui/calculator_app.py:105`
  - Existing unrelated soft warnings remained outside changed files.
- `python3 -B tools/code_checker/build_reference_map.py --check` - STALE from existing repository state; checked and not regenerated in this feature slice.

## Notes

The first focused test run exposed a stale DEV Train shell smoke expectation: it expected only three tabs, while the current shell already has `Feature Catalog`. The script expectation was updated to the current shell contract and the focused suite then passed.

## Changed Files

- `core/ml/catalog_fingerprint.py`
- `core/ml/inference.py`
- `core/ml/training.py`
- `tools/dev/mock_smoke/generators.py`
- `tools/dev/mock_smoke/run_mock_train_shell_smoke.py`
- `tests/test_ml_feature_catalog.py`
- `tests/test_apps_train_training_service.py`
- `tests/test_mock_smoke_generators.py`
- `tests/test_apps_predict_prediction_service_status.py`

## Structure

```yaml
change_gate:
  new_source: justified
  hotspot_delta: none
  code_map_check: checked
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner
  report_exemption: none
  read_ledger: included
```

New source justification: `core/ml/catalog_fingerprint.py` owns a reusable ML artifact/catalog contract and keeps training/inference/mock paths from duplicating hash logic.

Code map judgment: checked current and temporary maps. The generated map does not add `core/ml/catalog_fingerprint.py` as a separate entry, and a full stale-map refresh is outside this feature slice.

## Risk

Existing model artifacts without the new fingerprint metadata now require retraining, which is intentional for compatibility safety.

## Commit / Push

Committed as one Slice 4 commit. Push remains deferred until all requested remaining slices are complete.

## Next

Arc 13.5A Slice 5 - Common table helper cleanup.
