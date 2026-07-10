# Arc 15C-1-FU1 Data Definition Save Contract Guard Tightening

## Goal

Tighten Arc 15C-1 save planning guards so fields blocked by edit policy and raw row add/delete changes cannot be treated as saveable schema edits.

## Modified files

- `core/data_definition/edit_policy.py`
- `core/data_definition/save_contract.py`
- `tests/test_data_definition_save_contract.py`
- `result_reports/active/717_arc15c1-fu1-data-definition-save-contract-guard-tightening.md`

## Guard tightening summary

- Save planning now consults the editable field policy before allowing schema save preview.
- Restricted direct edits are reported as explicit error blockers targeting `schema_csv`.
- Raw draft row add/delete changes are blocked and require future controlled Add/Remove Feature commands.
- Existing allowed schema-backed edits, such as label changes, still produce a planned schema target.

## Restricted field blocker summary

- `column_key`, `display_order`, and `role` direct edits are blocked through `restricted_field_edit_not_allowed`.
- Blocker messages include the changed field name and row identity.
- Restricted field blockers prevent `can_save_schema` from becoming true.

## Raw row add/delete blocker summary

- Draft `__row__` add/delete changes are blocked through `raw_row_add_delete_not_allowed`.
- The blocker message points to future controlled Add/Remove Feature commands.
- Raw add/delete changes do not enable schema save.

## Validation result

- `python3 -B tools/check_code_structure.py`: passed with existing soft warnings.
- `python3 -B tools/code_checker/build_reference_map.py --check`: checked; reference map remains stale and was not regenerated in this guard-only slice.
- `python3 -m py_compile $(find core/data_definition -name '*.py' -print)`: passed.
- `python3 -m pytest tests/test_data_definition_save_contract.py tests/test_data_definition_core_projection.py tests/test_train_data_definition_readonly_ui.py tests/test_predict_schema_catalog_v2_projection.py`: passed, 41 tests.
- `git diff --check`: passed.
- `git status --short`: expected modified/new allowed files only.
- `git diff --name-only`: expected modified tracked files shown.
- `git diff --stat`: expected guard/test diff shown.

## Manual check

Not required. This is a core save-contract guard change with focused tests.

## Excluded scope

- No UI changes.
- No actual `schema.csv`, `features.csv`, derived policy, or `mapping.json` writes.
- No config, data, model, Data Mapping, Feature Catalog, Predict runtime, training, retrain, artifact activation, main merge, or main push changes.

## Next action

Arc 15C-2 — Data Definition Schema Save Writer
