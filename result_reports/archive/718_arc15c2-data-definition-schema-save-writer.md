# Arc 15C-2 Data Definition Schema Save Writer

## Goal

Add a guarded schema.csv writer for Data Definition drafts without touching production config files or adding UI save behavior.

## Modified files

- `core/data_definition/__init__.py`
- `core/data_definition/schema_writer.py`
- `tests/test_data_definition_schema_writer.py`
- `result_reports/active/718_arc15c2-data-definition-schema-save-writer.md`

## Schema writer summary

- Added `save_data_definition_schema_draft()` for writing schema-backed draft rows to an explicit destination path.
- Added `schema_csv_rows_from_draft()` to convert only `source_kind == "schema_row"` rows into the current schema CSV contract.
- Derived policy rows and feature projection rows are excluded from schema CSV output.
- CSV header and field order follow `core.predictor_schema.catalog_v2.REQUIRED_HEADERS`.
- Boolean values are written as lowercase `true` / `false`.
- Rows are written in stable `display_order` order, preserving status/helper rows when they are schema-backed.

## Guard behavior summary

- Writer requires `target == "schema_csv"`.
- Writer builds or accepts a save plan and only writes when `can_save_schema` is true and no error blockers exist.
- Writer rechecks raw row add/delete, restricted direct field edits, and derived policy changes before writing.
- Unchanged drafts return a no-op result and do not create a destination file.
- Non-schema targets are rejected and do not write files.

## Atomic write / backup behavior

- Writer has no production default path and requires an explicit destination.
- Writes use a temporary file in the destination directory and `os.replace`.
- Existing destination files are copied to `destination.parent/backups` with a timestamped filename before replacement.
- Temporary files are cleaned up on write failure.

## Tests summary

- Allowed label edit writes to a tmp schema and reloads through `load_predict_schema_catalog_v2`.
- Production `config/predict/schema.csv` hash remains unchanged in the writer test.
- Unchanged drafts no-op without creating files.
- Restricted field edits, raw row add/delete, and derived policy edits are blocked before write.
- Non-schema targets are rejected.
- Round-trip Data Definition report runs on the tmp schema; label-only schema edits can produce expected feature projection parity mismatch without modifying `features.csv`.

## Validation result

- `python3 -B tools/check_code_structure.py`: passed with existing soft warnings.
- `python3 -B tools/code_checker/build_reference_map.py --check`: checked; reference map remains stale and was not regenerated in this writer slice.
- `python3 -m py_compile $(find core/data_definition -name '*.py' -print)`: passed.
- `python3 -m pytest tests/test_data_definition_schema_writer.py tests/test_data_definition_save_contract.py tests/test_data_definition_core_projection.py tests/test_train_data_definition_readonly_ui.py tests/test_predict_schema_catalog_v2_projection.py`: passed, 50 tests.
- `git diff --check`: passed.
- `git status --short`: expected modified/new allowed files only.
- `git diff --name-only`: expected tracked change shown; new files are untracked before staging.
- `git diff --stat`: expected tracked change stat shown; new files are untracked before staging.

## Manual check

Not required. Tests write only to `tmp_path`; no production config save was performed.

## Excluded scope

- No UI, apps, Data Mapping, Feature Catalog, Predict runtime, training, model, or main-merge changes.
- No production `config/predict/schema.csv`, `config/ml/features.csv`, derived policy persistence, or `mapping.json` write.
- No Add Feature / Remove Feature command, one-hot owner switch, retrain, or artifact activation.

## Next action

Arc 15C-3 — Data Definition Edit UI Draft Workflow
