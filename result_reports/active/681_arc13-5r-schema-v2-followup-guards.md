# Arc 13.5R-4F Schema v2 Follow-up Guards

## Goal

Add narrow follow-up tests after the Predict Schema Catalog v2 owner switch so the schema projection is not protected only by self-referential parity checks.

## Modified Files

| File | Change |
| --- | --- |
| `tests/test_predict_schema_catalog_v2_projection.py` | Added explicit current core column contract and Feature Catalog ML-visible alignment guards. |
| `result_reports/active/681_arc13-5r-schema-v2-followup-guards.md` | Added this compact result report. |

## Added Guards

- Explicit 28-column core contract snapshot: `column_key`, `group`, dropdown flag, `ml_feature`, and `ml_target`.
- Feature Catalog alignment guard for projected input/auto `ml_feature` names against active Feature Catalog predictor input/auto rows.
- Feature Catalog alignment guard for projected result `ml_target` names against active Feature Catalog predictor result rows.
- Existing owner switch and one-hot guards remain in place.

## Verification

- `python3 -m pytest tests/test_predict_schema_catalog_v2.py tests/test_predict_schema_catalog_v2_projection.py`: OK, 18 passed
- `python3 -m pytest tests/test_apps_predict_schema_adapter.py tests/test_apps_predict_case_table_schema_adapter.py`: OK, 12 passed
- `git diff --check`: OK
- `python3 -B tools/check_code_structure.py`: NG, pre-existing unrelated `apps/calculator/ui/calculator_app.py` raw hex literal issue plus existing warnings. This task only changed predictor schema tests and this report.
- `git status --short`: checked before commit/push

## Excluded Scope

- No runtime behavior change.
- No `core/predictor_schema/columns.py` owner change.
- No `config/predict/schema.csv` change.
- No Feature Catalog change.
- No mapping/cascade, one-hot adapter, UI, fixture, or golden change.
- No WORK_PLAN update because the next action remains Arc 14A.

## Next Action

Arc 14A - Mapping Entity / Master Data Model Foundation.

## Commit / Push

Final commit/push result will be reported in terminal output.
