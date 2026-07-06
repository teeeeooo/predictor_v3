# Arc 15C-4 Data Definition Save UI Integration

## Goal

Connect the Data Definition UI save flow to the guarded schema writer while keeping production config out of tests and keeping `features.csv` unwritten.

## Scope

- Added explicit schema-path ownership to `DataDefinitionService`.
- Added `save_schema_draft()` service orchestration that passes the current save plan into `save_data_definition_schema_draft()`.
- Added controller save state, save result rows, backup path display, and post-success draft reload.
- Added a Save button and Save Result table to the Data Definition panel.
- Added tmp-path save UI tests for success, no-op, blocked candidate validation, and panel result display.

## Non-goals

- No production config test writes.
- No `features.csv` write.
- No derived policy persistence.
- No Data Mapping, Feature Catalog, Predict runtime, training, model, retrain, or artifact activation changes.

## Verification

- `python3 -B tools/check_code_structure.py`: passed with existing unrelated soft warnings; changed/new source files stayed below structure warning thresholds.
- `python3 -B tools/code_checker/build_reference_map.py --check`: checked; reference map remains stale and was not regenerated.
- `python3 -m py_compile $(find core/data_definition apps/train -name '*.py' -print)`: passed.
- `python3 -m pytest tests/test_train_data_definition_save_ui.py tests/test_train_data_definition_readonly_ui.py tests/test_data_definition_schema_writer.py tests/test_data_definition_save_contract.py`: passed, 36 tests.
- `git diff --check`: passed after report creation.
- `git status --short`: expected slice 2 source/test/report files only before staging.

## Task Results

- Save execution stays behind the existing guarded core writer.
- Save attempts pass the active save plan into the writer so blocker/no-op/success/error behavior is produced by the save contract and writer guards.
- Successful schema writes reload the draft from the saved explicit schema path, clearing changed state.
- Blocked candidate validation leaves the edited draft in memory and does not replace or back up the schema file.
- UI state displays save status, message, row count, explicit path, backup path, and writer issue codes.

## Change Gate

```yaml
change_gate:
  new_source: none
  hotspot_delta: wiring-only
  code_map_check: checked
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner
  report_exemption: none
  read_ledger: included
```

- `hotspot_delta`: wiring-only additions to the existing Data Definition service/controller/panel owners.
- `reuse_commonization`: reused the Arc 15C-2 guarded writer and the slice 1 preview/result table surfaces rather than adding another persistence path.

## Read Ledger

- `apps/train/services/data_definition_service.py`: save path owner and guarded writer orchestration.
- `apps/train/controllers/data_definition_controller.py`: save action state and result projection.
- `apps/train/ui/data_definition_panel.py`: Save button and result table wiring.
- `core/data_definition/schema_writer.py`: guarded writer result contract.
- `core/data_definition/save_contract.py`: save plan blocker/no-op policy.
- `tests/test_data_definition_schema_writer.py`, `tests/test_data_definition_save_contract.py`, `tests/test_train_data_definition_edit_ui.py`: focused existing guard patterns.
- broad read: none.
- repeated read: none.

## Structure Warnings

Existing unrelated calculator/code-map warnings remain. No changed/new source file emitted a structure warning.

## Known Failures / Risks

- A successful schema-only save can make the read-only projection report show compatibility parity issues until the Feature Catalog owner transition is handled; this is expected because this slice still does not write `features.csv`.
- UI save is intentionally guarded but available; tests use only explicit `tmp_path` schema files.

## Scope Compliance

- No changes under `config/**`, `data/**`, `model/**`, `core/ml/**`, `core/mapping/**`, or `apps/predict/**`.
- No production config write, Feature Catalog behavior change, Data Mapping behavior change, retrain, artifact activation, main merge, or main push.

## Commit / Push

Slice 2 source, test, and report changes are included in the slice commit. Push is deferred until all requested slices complete.

## Project Memory Delta

No memory seed update required. The slice implements the previously active Arc 15C save UI step without adding a new unresolved project-level decision.
