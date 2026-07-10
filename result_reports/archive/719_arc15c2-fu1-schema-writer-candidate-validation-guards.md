# Arc 15C-2-FU1 Schema Writer Candidate Validation Guards

## Goal

Tighten the Arc 15C-2 schema writer before Arc 15C-3 by validating the candidate CSV before replacement and expanding writer guard tests.

## Modified files

- `core/data_definition/schema_writer.py`
- `tests/test_data_definition_schema_writer.py`
- `result_reports/active/719_arc15c2-fu1-schema-writer-candidate-validation-guards.md`

## Guard tightening summary

- The writer now writes the candidate schema to a temp file and runs `load_predict_schema_catalog_v2()` plus `validate_predict_schema_catalog_v2()` before backup or `os.replace`.
- Candidate validation failures return `candidate_schema_validation_failed` issues and do not create or replace the destination file.
- Unsupported targets now return `schema_writer_target_not_allowed` in result issues.

## Atomic write / backup behavior

- Candidate validation runs before any backup is created.
- Existing destination files are backed up only after the candidate validates.
- Replace failures clean up the temp file and leave the existing destination unchanged.

## Tests summary

- Added invalid editable field value coverage for `data_type` and `editor`.
- Added coverage that candidate validation failure does not overwrite an existing destination or create a backup.
- Added unsupported target issue assertion.
- Added backup/replace behavior coverage for an existing destination.
- Added replace failure cleanup coverage using monkeypatch.

## Validation result

- `python3 -B tools/check_code_structure.py`: passed with existing soft warnings.
- `python3 -B tools/code_checker/build_reference_map.py --check`: checked; reference map remains stale and was not regenerated in this guard-only follow-up.
- `python3 -m py_compile $(find core/data_definition -name '*.py' -print)`: passed.
- `python3 -m pytest tests/test_data_definition_schema_writer.py tests/test_data_definition_save_contract.py tests/test_data_definition_core_projection.py tests/test_train_data_definition_readonly_ui.py tests/test_predict_schema_catalog_v2_projection.py`: passed, 54 tests.
- `git diff --check`: passed.
- `git status --short`: expected modified/new allowed files only.
- `git diff --name-only`: expected modified tracked files shown.
- `git diff --stat`: expected writer/test diff shown.

## Manual check

Not required. Tests write only to `tmp_path`; production config remains untouched.

## Excluded scope

- No UI, apps, Data Mapping, Feature Catalog, Predict runtime, training, model, mapping, config, main merge, or main push changes.
- No actual production schema/features/mapping write.

## Next action

Arc 15C-3 — Data Definition Edit UI Draft Workflow
