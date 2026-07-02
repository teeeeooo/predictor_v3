# Arc 13.5A Slice 0 - Feature Catalog Identity Simplification

## Summary

Implemented Slice 0 only: the Feature Catalog schema no longer carries `feature_id`, and `ml_name` is the catalog row identity used by validation and train application DTO paths.

## Scope

- Removed `feature_id` from `config/ml/features.csv`.
- Removed `feature_id` from core Feature Catalog required headers, dataclass, and CSV loader.
- Removed active-row `feature_id` uniqueness validation.
- Updated validation row message prefixes to use `ml_name` and `order`.
- Removed `feature_id` from Train Feature Catalog locked headers and save DTO conversion.
- Updated focused Feature Catalog tests and directly affected Train shell panel column expectation.
- Added a short Slice 0 status note to the correction design document.

## Non-Goals Held

- No Feature Manager add/delete/duplicate behavior.
- No dropdown/help/user-friendly header work.
- No schema refresh or live table refresh implementation.
- No model artifact catalog hash implementation.
- No unrelated refactor.
- No report lifecycle movement.

## Verification

- `python3 -m compileall core apps tests` - OK
- `python3 -m pytest tests/test_ml_feature_catalog.py tests/test_apps_train_feature_catalog.py` - OK, 51 passed
- `git diff --check` - OK
- `python3 -B tools/check_code_structure.py` - NG, pre-existing unrelated raw hex literal:
  - `apps/calculator/ui/calculator_app.py:105`
  - The same `#202020` literal is present in `HEAD`, so this is not introduced by Slice 0.

## Changed Files

- `config/ml/features.csv`
- `core/ml/feature_catalog.py`
- `core/ml/feature_catalog_validation.py`
- `apps/train/application/feature_catalog/models.py`
- `apps/train/application/feature_catalog/service.py`
- `tests/test_ml_feature_catalog.py`
- `tests/test_apps_train_feature_catalog.py`
- `tests/test_apps_train_shell.py`
- `docs/designs/2026-07-02-arc13-5a-feature-catalog-manager-correction-design.md`

## Read Ledger

- `docs/designs/2026-07-02-arc13-5a-feature-catalog-manager-correction-design.md` - full file, Slice 0 implementation scope and later-slice non-goals.
- `AGENT_TASK_ROUTER.md` - relevant schema/core contract, coding, ML/Predictor, and result report workflow sections.
- `docs/agent_workflows/RESULT_REPORT_WORKFLOW.md` - report and push handling.
- `docs/agent_workflows/ML_PREDICTOR_WORKFLOW.md` - ML change verification context.
- `docs/architecture/PROJECT_CLEAN_ARCHITECTURE_BOUNDARY.md` - boundary context for application/core separation.
- `core/ml/feature_catalog.py`
- `core/ml/feature_catalog_validation.py`
- `apps/train/application/feature_catalog/models.py`
- `apps/train/application/feature_catalog/service.py`
- `tests/test_ml_feature_catalog.py`
- `tests/test_apps_train_feature_catalog.py`
- `tests/test_apps_train_shell.py`

## Change Gate

```yaml
change_gate:
  new_source: none
  hotspot_delta: none
  code_map_check: checked
  ui_literal_exemption: none
  reuse_commonization: local-with-reason
  report_exemption: none
  read_ledger: included
```

Code map judgment: `core/ml/feature_catalog_validation.py` is already listed in `docs/code_map/CODEBASE_REFERENCE_MAP.md`, and Slice 0 did not add a new public module or boundary.

Reuse/commonization judgment: the new row-prefix helper is validation-local formatting for this catalog validator, with no sibling owner found in the bounded feature catalog search.

## Risks

- Existing downstream artifacts trained with the prior catalog shape may still have out-of-band expectations, but Slice 0 intentionally did not implement artifact hash or migration logic.
- Structure guard remains blocked by an unrelated pre-existing calculator UI literal.

## Next

Arc 13.5A Slice 1 UX foundation.
