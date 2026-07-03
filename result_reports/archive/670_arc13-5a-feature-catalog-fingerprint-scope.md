# Arc 13.5A Feature Catalog Fingerprint Scope

## Goal

Narrow the Feature Catalog model compatibility fingerprint so only ML model contract changes require retraining.

## Existing Problem

The previous fingerprint hashed every `REQUIRED_HEADERS` field and sorted rows by `order`. Display/admin-only edits such as `label`, `notes`, `order`, or `ui_key` could therefore create a model fingerprint mismatch even when the trained model contract did not change.

## Fingerprint Scope

The new fingerprint version is `feature_catalog.ml_contract.v1`.

Payload includes active rows only and these fields:

- `ml_name`
- `role`
- `one_hot_group`
- `zero_fill_policy`
- `active`

Payload excludes:

- `label`
- `notes`
- `order`
- `ui_key`
- `source`
- `mapping_key`

Rows are sorted by stable ML contract values (`role`, `ml_name`, `one_hot_group`, `zero_fill_policy`) so changing `order` does not affect the model compatibility fingerprint.

`source` and `mapping_key` remain UI/input mapping and schema apply concerns. They are not part of model artifact compatibility in this slice.

## Changed Files

- `core/ml/catalog_fingerprint.py`: replaced full-catalog hashing with active-row ML contract payload hashing and bumped the fingerprint version string.
- `tests/test_ml_feature_catalog.py`: added guards for included/excluded fields, inactive-row exclusion, version naming, and existing missing/mismatch validation.
- `docs/workflows/ml_feature_catalog_workflow.md`: documented model compatibility fingerprint scope and source/mapping exclusion.
- `docs/designs/2026-07-02-arc13-5a-feature-catalog-manager-correction-design.md`: synced Arc 13.5A design notes with the narrowed ML contract fingerprint.

## Training / Inference Compatibility

- `core/ml/training.py` still calls `attach_catalog_fingerprint()` when creating model artifacts.
- `core/ml/inference.py` still calls `validate_model_catalog_fingerprint()` during model load.
- Existing artifacts with old full-catalog fingerprints are expected to mismatch and require retraining.
- Public metadata keys remain unchanged: `feature_catalog_fingerprint` and `feature_catalog_fingerprint_version`.

## Verification

- `python3 -m compileall core apps tests`: OK.
- `python3 -m pytest tests/test_ml_feature_catalog.py tests/test_apps_predict_prediction_service_status.py`: OK, 52 passed.
- `git diff --check`: OK.
- `python3 -B tools/check_code_structure.py`: NG, existing unrelated `apps/calculator/ui/calculator_app.py` raw hex literal guard failure only.
- `python3 -B tools/check_code_structure.py --verbose`: changed files are not structure warning targets; warnings are existing calculator/core/code-map freshness warnings.

## Excluded Scope

- Dropdown UX changes.
- Feature Catalog add/delete/duplicate behavior.
- Schema refresh/live apply implementation.
- UI schema fingerprint runtime wiring.
- Model training logic refactor.
- Calculator raw hex literal cleanup.
- Report lifecycle cleanup.

## Structure / Code Map

- `code_map_check`: skipped.
- Reason: this slice changes an existing ML owner and adds only local fingerprint payload helpers; no new source file, reusable surface/helper boundary, or owner split was introduced. The code map is already stale and regeneration would touch a non-scope documentation artifact.
- Structure warnings: none for changed files.

## Known Risks

- Existing trained artifacts using the old fingerprint version will mismatch and require retraining, which is acceptable for this scope change.
- `source` and `mapping_key` changes can still affect UI/input mapping behavior; that concern is intentionally separate from model artifact compatibility.

## Next Action

- Arc 13.5A final closeout update or active report lifecycle cleanup.

## Commit / Push

- commit: final hash reported in terminal output after push
- push: final status reported in terminal output after push
- local_head: final SHA reported in terminal output after push
- remote_main: final SHA reported in terminal output after push
- match: final match status reported in terminal output after push

## Project Memory Delta

- none
