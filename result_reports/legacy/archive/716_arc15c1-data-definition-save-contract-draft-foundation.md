# Arc 15C-1 Data Definition Save Contract and Draft Foundation

## Goal

Add the Qt-free foundation for future Data Definition editing and saving without implementing UI editing or file writes.

## Modified files

- `core/data_definition/__init__.py`
- `core/data_definition/draft.py`
- `core/data_definition/edit_policy.py`
- `core/data_definition/save_contract.py`
- `tests/test_data_definition_save_contract.py`
- `result_reports/active/716_arc15c1-data-definition-save-contract-draft-foundation.md`

## Save contract summary

- Added an in-memory save plan that reports future write targets and blockers.
- `schema_csv` is represented as the future primary save target for schema-backed draft changes.
- `features_csv` remains blocked as a Data Definition write target while Feature Catalog direct save still exists.
- `derived_policy` remains blocked until a persistence owner is defined.
- `mapping_json` is never a Data Definition save target.
- Restart and retrain impacts are reported as state, not executed actions.

## Draft model summary

- Added immutable draft rows built from current Predict Schema v2 rows plus current derived feature policy rows.
- Draft rows preserve schema fields needed by future Add/Edit/Save work, including mapping requirements, ML names, one-hot group, active state, and notes.
- Draft source ownership is explicit with `schema_row`, `derived_policy`, and `feature_projection` source kinds.
- Draft changes are field-level in-memory diffs against the immutable baseline.

## Editable field policy

- Schema-backed fields such as label, editor, data type, visibility, mapping requirement fields, model input flag, ML name, one-hot group, active state, and notes are allowed by policy.
- `column_key`, `display_order`, and `role` are restricted for future controlled Add Feature commands.
- Mapping values are blocked because Data Mapping Manager owns `mapping.json` values.
- Runtime paths and model activation are blocked because Data Definition core does not own artifact paths.
- Derived policy rows are blocked until derived policy persistence is defined.

## Blocked/deferred writes

- `features_csv_dual_writer_not_resolved`: blocks Data Definition writes to `features.csv` while Feature Catalog direct save remains active.
- `derived_policy_persistence_required`: blocks derived feature add/edit/save until persistence is designed.
- `mapping_value_edit_not_allowed`: blocks Data Definition writes to `mapping.json`.
- `one_hot_runtime_owner_deferred`: records that generic one-hot runtime ownership is deferred to Arc 15E.
- `data_mapping_dynamic_requirement_deferred`: records that Data Mapping dynamic requirement injection is deferred to Arc 15D.
- `retrain_required_for_new_model_input`: records retrain requirement without executing training or artifact activation.
- `restart_required_for_schema_change`: represented by the save plan restart impact state.

## Feature Catalog transition decision

Feature Catalog Manager remains the transition-period compatibility surface. Data Definition save planning does not write `features.csv` until the direct save owner conflict is resolved in a later slice.

## Derived policy persistence status

Current derived feature rows are represented in draft form, but derived policy editing and saving are blocked because Arc 15C-1 does not introduce a persistence file or writer.

## Validation result

- `python3 -B tools/check_code_structure.py`: passed with existing soft warnings.
- `python3 -B tools/code_checker/build_reference_map.py --check`: checked; reference map is stale before this change and was not regenerated in this slice.
- `python3 -m py_compile $(find core/data_definition -name '*.py' -print)`: passed.
- `python3 -m pytest tests/test_data_definition_save_contract.py tests/test_data_definition_core_projection.py tests/test_train_data_definition_readonly_ui.py tests/test_predict_schema_catalog_v2_projection.py`: passed, 35 tests.
- `git diff --check`: passed.
- `git status --short`: expected modified/new allowed files only.
- `git diff --name-only`: expected tracked change shown; new files are untracked before staging.
- `git diff --stat`: expected tracked change stat shown; new files are untracked before staging.

## Manual check

Not required. This slice is core-only and read-only/save-preview only.

## Excluded scope

- No UI edit/save implementation.
- No actual `schema.csv`, `features.csv`, derived policy, or `mapping.json` write.
- No config, data, model, training, runtime adapter, Data Mapping, Feature Catalog, Predict, or Train UI behavior change.
- No model retrain, artifact activation, GUI smoke, full integration smoke, main merge, or main push.

## Structure / Change Gate

- Prompt-supplied boundary was sufficient for Design Gate: new responsibility stays in `core/data_definition/`; UI/service/controller layers are untouched.
- Read ledger: Arc 15 design record; Arc 15A/FU1/B reports; current Data Definition core; current schema/features contracts; Feature Catalog save owner; Data Mapping save owner.
- Existing reference map stale state was checked and recorded; no reference map regeneration was performed because this slice only adds a bounded core foundation and tests.

## Next action

Arc 15C-2 — Data Definition Schema Save Writer
