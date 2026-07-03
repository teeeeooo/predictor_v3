# Arc 13.5R Current Predict Schema Inventory

## Goal

현재 Predict table schema가 어디서 생성되고 어떤 runtime adapter가 어떤 metadata에 의존하는지 inventory로 문서화해 Predict Schema Catalog v2 field/spec 확정의 입력 자료로 남긴다.

## Modified Files

| Path | Change |
| --- | --- |
| `docs/designs/assets/current_predict_schema_inventory.md` | Current Predict schema owner split, column inventory, v2 draft mapping, cascade/one-hot gaps, recommendations 작성. |
| `docs/WORK_PLAN.md` | Next action을 Arc 13.5R-2 field/spec confirmation으로 compact하게 갱신. |
| `result_reports/active/677_arc13-5r-current-predict-schema-inventory.md` | Compact result report. |

## Audit Scope

- Feature Catalog projection and validation owners.
- Hard-coded `ui_columns.py` dropdown-only input and rule-result columns.
- `core.predictor_schema.columns.COLUMNS`, grouped key lists, and `DROPDOWN_TARGET`.
- Predict schema/case table adapters and workspace/model usage.
- Mapping-backed dropdowns, core autofill/cascade behavior, and ML input adapter one-hot behavior.
- Focused tests as evidence for current contracts.

## Key Findings

- Current core `COLUMNS` has 28 columns; unified case table appends virtual `status` and `message`.
- Predict UI columns are split across Feature Catalog, `ui_columns.py`, and case-table virtual metadata.
- `source` currently overloads trigger column and mapping entity meaning for auto rows.
- `DROPDOWN_TARGET = {k: k}` assumes dropdown key equals mapping section.
- ODU cascade and one-hot input group projection remain hard-coded.
- `cond_area` / `cond_volume` metadata suggests simple ODU lookup, while runtime final value comes from `cond_specs` composite lookup.
- IDU Size -> Evap Index filtering is absent.

## Verification

- `git diff --check`: OK.
- `git status --short`: expected WORK_PLAN modification plus new inventory/report files only.
- `python3 -B tools/check_code_structure.py`: NG, pre-existing unchanged source guard failure in `apps/calculator/ui/calculator_app.py` for a raw hex color literal; this docs-only audit did not modify source files.
- Skipped pytest: docs/inventory audit only; code/test logic was not changed.
- Skipped GUI smoke: no UI implementation change.

## Excluded Scope

- No source, config, fixture, or test code changes.
- No Predict Schema Catalog v2 implementation or `config/predict/schema.csv`.
- No mapping converter, Data Mapping Manager UI, Feature Catalog Manager, or Predict runtime changes.
- No report lifecycle movement.

## Next Action

Arc 13.5R-2 should confirm the Predict Schema Catalog v2 field/spec contract using the inventory, including one-hot selector representation and initial `lookup` / `filter` / `clear` / `composite_lookup` primitive scope.

## Commit / Push

Final commit and push result will be reported in terminal output to avoid a self-referential report update loop.
