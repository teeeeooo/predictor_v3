# Arc 15F Training / Model Readiness Integration

## Goal

Verify Data Definition readiness behavior for explicit training data paths and draft restart/retrain preview state without running retrain or touching model artifacts.

## Scope

- Tightened the passive training header readiness check so explicit non-file paths return an unavailable readiness issue instead of attempting to open them.
- Added focused tests for explicit directory paths, retrain-required draft fields, restart-required schema fields, and controller preview state.
- Confirmed existing Data Definition UI save-plan summary/blocker rows surface restart/retrain impact for draft edits.

## Non-goals

- No training execution.
- No model artifact inspection/activation.
- No Predict runtime adapter changes.
- No `features.csv`, config, data, or model writes.

## Verification

- `python3 -B tools/check_code_structure.py`: passed with existing unrelated soft warnings.
- `python3 -B tools/code_checker/build_reference_map.py --check`: checked; reference map remains stale and was not regenerated.
- `python3 -m py_compile $(find core/data_definition apps/train -name '*.py' -print)`: passed.
- `python3 -m pytest tests/test_data_definition_*.py tests/test_train_data_definition_*.py tests/test_data_definition_schema_writer.py`: passed, 56 tests.
- `git diff --check`: passed after report creation.
- `git status --short`: expected slice 5 source/test/report files only before staging.

## Task Results

- `build_readiness_checks()` now treats an explicit directory or other non-file training data path as `unavailable` with a clear non-file message.
- No training data path still returns `not_evaluated` and remains non-blocking.
- Save-plan tests cover retrain-required state for `model_input_enabled`, `ml_name`, and `value_source` changes.
- Save-plan/controller tests cover restart-required state for schema-backed `visible`, `editor`, and `data_type` changes.

## Change Gate

```yaml
change_gate:
  new_source: none
  hotspot_delta: none
  code_map_check: checked
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner
  report_exemption: none
  read_ledger: included
```

- `reuse_commonization`: reused the existing passive readiness owner and save-plan impact model rather than adding training/model execution or artifact probes.

## Read Ledger

- `core/data_definition/readiness.py`: passive training header check owner.
- `core/data_definition/save_contract.py`: restart/retrain impact contract.
- `apps/train/controllers/data_definition_controller.py`: existing UI preview state; read only, not modified.
- `tests/test_data_definition_core_projection.py`, `tests/test_data_definition_save_contract.py`, `tests/test_train_data_definition_*`: existing readiness/save-plan coverage.
- broad read: none.
- repeated read: none.

## Structure Warnings

Existing unrelated calculator/code-map warnings remain. No changed/new source file emitted a structure warning.

## Known Failures / Risks

- Model artifact compatibility remains intentionally `not_evaluated`; this slice does not inspect or activate artifacts.
- UI readiness impact is surfaced through existing save-plan summary and blockers, not a new model-artifact readiness probe.

## Scope Compliance

- No `config/**`, `data/**`, `model/**`, `apps/predict/**`, Feature Catalog, Data Mapping, training execution, retrain, artifact activation, main merge, or main push changes.

## Commit / Push

Slice 5 source, test, and report changes are included in the slice commit. Push is deferred until all requested slices complete.

## Project Memory Delta

No memory seed update required. This slice closes the planned readiness verification without introducing a new project-level decision.
