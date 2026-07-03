# Arc 13.5A Fingerprint Active Field Dedup

## Goal

Remove the redundant `active` field from each Feature Catalog model compatibility fingerprint payload row.

## Change

- `active` is no longer part of `ML_CONTRACT_FINGERPRINT_FIELDS`.
- Active state still affects the fingerprint through row inclusion/exclusion:
  active rows are included, inactive rows are excluded.
- Fingerprint version was bumped to `feature_catalog.ml_contract.v2` because the serialized payload changed.

## Changed Files

- `core/ml/catalog_fingerprint.py`
- `tests/test_ml_feature_catalog.py`
- `docs/workflows/ml_feature_catalog_workflow.md`
- `docs/designs/2026-07-02-arc13-5a-feature-catalog-manager-correction-design.md`

## Verification

- `python3 -m compileall core apps tests`: OK.
- `python3 -m pytest tests/test_ml_feature_catalog.py tests/test_apps_predict_prediction_service_status.py`: OK, 52 passed.
- `git diff --check`: OK.
- `python3 -B tools/check_code_structure.py`: NG, existing unrelated `apps/calculator/ui/calculator_app.py` raw hex literal guard failure only.

## Excluded Scope

- No dropdown UX changes.
- No schema refresh/live apply wiring.
- No model training/inference policy changes beyond fingerprint payload/version.
- No calculator raw hex cleanup.

## Commit / Push

- commit: final hash reported in terminal output after push
- push: final status reported in terminal output after push
- local_head: final SHA reported in terminal output after push
- remote_main: final SHA reported in terminal output after push
- match: final match status reported in terminal output after push

## Project Memory Delta

- none
