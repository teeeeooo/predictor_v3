# Arc 13.5R Read-only Schema v2 Projection Parity

## Goal

Add a read-only Predict Schema Catalog v2 draft and projection prototype, then prove it can reproduce the current 28 core `COLUMNS` order and key metadata without switching runtime ownership.

## Modified Files

| Path | Change |
| --- | --- |
| `config/predict/schema.csv` | Read-only v2 draft schema representing current core columns, hidden one-hot rows, and status/message rows. |
| `core/predictor_schema/catalog_v2.py` | Qt-free draft loader and minimal validator. |
| `core/predictor_schema/catalog_v2_projection.py` | Projection helper from v2 draft rows to current `COLUMNS`-like metadata. |
| `tests/test_predict_schema_catalog_v2.py` | Loader, validation, one-hot, and status-row tests. |
| `tests/test_predict_schema_catalog_v2_projection.py` | Current schema parity tests. |
| `docs/designs/2026-07-03-arc13-5r-readonly-schema-v2-projection-parity.md` | Prototype design record and parity evidence. |
| `docs/designs/README.md` | Design record index update. |
| `docs/WORK_PLAN.md` | Next action moved to Arc 13.5R-4 owner switch readiness. |
| `result_reports/active/679_arc13-5r-readonly-schema-v2-projection-parity.md` | Result report. |

## Key Decisions

- `config/predict/schema.csv` is a read-only prototype artifact, not runtime source of truth.
- `core/predictor_schema/columns.py` remains the runtime owner.
- Status/message rows are represented in v2 but excluded from the 28-row core projection parity helper.
- Hidden one-hot feature rows are represented in v2 and checked against Feature Catalog one-hot groups.
- `cond_area` / `cond_volume` preserve current compatibility metadata while recording `cond_specs` as v2 target meaning.

## Parity Coverage

- Projected core column count is 28.
- Projected key order matches current `COLUMNS`.
- Headers, groups, dropdown metadata, readonly metadata, mapping/source/mapping_key compatibility, `ml_feature`, `ml_target`, width, and bg color match current core metadata.
- `DROPDOWN_COLS` equivalent matches current runtime.
- One-hot selector group mapping matches current adapter behavior.
- Existing Predict schema, case table, mapping dropdown, and prediction adapter focused tests pass.

## Verification

- `python3 -m py_compile core/predictor_schema/catalog_v2.py core/predictor_schema/catalog_v2_projection.py`: OK.
- `python3 -m pytest tests/test_predict_schema_catalog_v2.py tests/test_predict_schema_catalog_v2_projection.py`: OK, 13 passed.
- `python3 -m pytest tests/test_apps_predict_schema_adapter.py tests/test_apps_predict_case_table_schema_adapter.py tests/test_apps_predict_mapping_backed_dropdown.py tests/test_apps_predict_prediction_adapters.py`: OK, 31 passed.
- `git diff --check`: OK.
- `python3 -B tools/check_code_structure.py`: NG, pre-existing unchanged source guard failure in `apps/calculator/ui/calculator_app.py` for raw hex color literal. Verbose output also showed pre-existing LOC/class/code-map warnings outside this task's changed source files.
- `git status --short`: expected source/test/docs/report changes only before commit.

## Excluded Scope

- No Predict runtime owner switch.
- No Predict UI behavior change.
- No Data Mapping Manager UI, mapping converter, runtime cascade engine, live schema reload, Feature Catalog Manager UI, fixture/golden expected, ML training/retraining, or model artifact changes.
- No unrelated refactor.

## Next Action

Arc 13.5R-4 projection owner switch readiness / owner switch after parity acceptance.

## Commit / Push

Final commit/push result will be reported in terminal output.
