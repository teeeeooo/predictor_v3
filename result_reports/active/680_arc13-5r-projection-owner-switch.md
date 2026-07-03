# Arc 13.5R-4 Projection Owner Switch

## Goal

Switch Predict core column assembly to the Predict Schema Catalog v2 projection only if Arc 13.5R-3 parity evidence is sufficient, while preserving current public behavior.

## Scope

- Changed `core.predictor_schema.columns.COLUMNS` to load from `load_projected_columns_v2()`.
- Kept runtime behavior for Predict UI adapters, mapping/autofill, one-hot ML projection, and case-table virtual status/message unchanged.
- Split presentation defaults into a small schema presentation owner.
- Made legacy dropdown/autofill compatibility projection explicit in `catalog_v2_projection.py`.

## Changed Files

| File | Change |
| --- | --- |
| `core/predictor_schema/presentation.py` | Added shared presentation defaults and width override helper. |
| `core/predictor_schema/catalog_v2_projection.py` | Removed duplicated presentation metadata and separated legacy compatibility fields from v2 semantic fields. |
| `core/predictor_schema/columns.py` | Switched `COLUMNS` assembly to v2 projection. |
| `tests/test_predict_schema_catalog_v2_projection.py` | Added owner switch, group, dropdown target, and semantic/legacy mapping separation guards. |
| `docs/designs/2026-07-03-arc13-5r-projection-owner-switch.md` | Added owner switch design record. |
| `docs/designs/README.md` | Added design record index row. |
| `docs/WORK_PLAN.md` | Moved next action to Arc 14A. |

## Readiness Decision

Owner switch performed. The read-only v2 projection already matched the 28 current core columns, and the switch is limited to schema assembly ownership.

## Key Changes

- `config/predict/schema.csv` is now the source for Predict core column projection.
- Feature Catalog remains the ML feature/target/one-hot compatibility source.
- `ui_columns.py` is no longer part of runtime `COLUMNS` assembly, but it was not removed.
- `DROPDOWN_TARGET = {k: k}` behavior is preserved.
- `status` / `message` remain adapter-local virtual columns.

## Compatibility Hard-code Cleanup

- Presentation metadata is no longer duplicated inside `catalog_v2_projection.py`.
- Legacy compatibility helpers clarify that projected `mapping`, `source`, and `mapping_key` are current adapter fields, not the v2 semantic contract.
- `cond_area` and `cond_volume` keep current compatibility metadata while v2 schema rows retain `mapping_entity=cond_specs`.

## Verification

- `python3 -m py_compile core/predictor_schema/catalog_v2.py core/predictor_schema/catalog_v2_projection.py core/predictor_schema/columns.py`: OK
- `python3 -m pytest tests/test_predict_schema_catalog_v2.py tests/test_predict_schema_catalog_v2_projection.py`: OK, 16 passed
- `python3 -m pytest tests/test_apps_predict_schema_adapter.py tests/test_apps_predict_case_table_schema_adapter.py tests/test_apps_predict_mapping_backed_dropdown.py tests/test_apps_predict_prediction_adapters.py`: OK, 31 passed
- `python3 -m pytest tests/test_core_mapping_autofill.py`: OK, 4 passed
- `git diff --check`: OK
- `python3 -B tools/check_code_structure.py`: NG, pre-existing unrelated guard issue in `apps/calculator/ui/calculator_app.py` raw hex literal plus existing LOC/code-map warnings. Changed files are under predictor schema/tests/docs/report and are not the reported error path.

## Known Risks

- Runtime cascade remains hard-coded and is not yet the v2 primitive engine.
- One-hot ML projection still uses `RowToMlInputAdapter._ONE_HOT_INPUT_GROUPS`.
- Schema changes remain restart-required.

## Code Map / Structure

- `code_map_check`: skipped. This slice changed the existing predictor schema owner path and added one small sibling module; no broad code map regeneration was requested.
- `Structure Warnings`: unchanged pre-existing warnings in calculator/standards surfaces plus stale code-map reminder; no changed/new source file emitted a reported structure warning.
- `Warning Triage`: accepted for this slice because the guard error and warnings are outside the modified predictor schema files.

## Excluded Scope

- No Predict UI behavior change.
- No Data Mapping Manager UI.
- No mapping converter.
- No generic runtime cascade engine.
- No IDU Size -> Evap Index filter.
- No one-hot ML adapter owner switch.
- No ML training/retraining/model artifact change.

## Next Action

Arc 14A - Mapping Entity / Master Data Model Foundation.

## Commit / Push

Final commit/push result will be reported in terminal output.
