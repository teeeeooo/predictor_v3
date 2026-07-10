# Arc 15D Data Mapping Dynamic Requirement

## Goal

Reflect Data Definition mapping requirements in the Data Mapping Manager without moving mapping value ownership out of Data Mapping.

## Scope

- Added an in-memory projection step that appends Data Definition-required mapping attributes to matching Data Mapping draft groups.
- Added a minimal `cond_specs` to `odu_cond_specs` adapter for the existing runtime/editor group boundary.
- Added Data Mapping service validation for missing required mapping values.
- Updated controller attribute rows so dynamically required fields display as required with notes.
- Added focused core and Train Data Mapping tests for dynamic requirements and missing-value save blocking.

## Non-goals

- No automatic `mapping.json` value generation.
- No production `mapping.json`, config, data, model, Predict runtime, Feature Catalog, schema writer, retrain, or artifact activation changes.
- No runtime owner switch for one-hot behavior.

## Verification

- `python3 -B tools/check_code_structure.py`: passed with existing unrelated soft warnings.
- `python3 -B tools/code_checker/build_reference_map.py --check`: checked; reference map remains stale and was not regenerated.
- `python3 -m py_compile $(find core/mapping core/data_definition apps/train -name '*.py' -print)`: passed.
- `python3 -m pytest tests/test_data_mapping_*.py tests/test_train_data_mapping_*.py tests/test_data_definition_core_projection.py`: passed, 16 tests.
- Compatibility check: `python3 -m pytest tests/test_apps_train_data_mapping_service.py tests/test_apps_train_data_mapping_controller.py tests/test_apps_train_data_mapping_ui_models.py tests/test_core_mapping_editor_projection.py tests/test_core_mapping_editor_validation.py tests/test_core_mapping_editor_persistence.py`: passed, 57 tests.
- `git diff --check`: passed after report creation.
- `git status --short`: expected slice 3 source/test/report files only before staging.

## Task Results

- Default production Data Mapping service now uses the current Data Definition report as a requirement source.
- Explicit custom/test mapping providers remain requirement-free unless a requirement provider is injected; this preserves existing focused fixtures while keeping the production default dynamic.
- Dynamic requirements add missing in-memory columns and mark blanks as `required_mapping_value_missing`, disabling save.
- Save attempts with missing dynamic values return a controlled failure before persistence, so no `mapping.json` mutation occurs.

## Change Gate

```yaml
change_gate:
  new_source: none
  hotspot_delta: accepted-for-slice
  code_map_check: checked
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner
  report_exemption: none
  read_ledger: included
```

- `hotspot_delta`: accepted for this slice because mapping requirement projection belongs beside the existing editor projection/service/controller boundary and stayed below structure warning thresholds.
- `reuse_commonization`: reused existing `MappingEditorDraft` groups, validation issue DTOs, and Data Mapping panel tables rather than introducing a new registry or UI surface.

## Read Ledger

- `core/mapping/editor_projection.py`: editor draft projection and runtime group adapter.
- `apps/train/services/data_mapping_service.py`: snapshot validation and save gating.
- `apps/train/controllers/data_mapping_controller.py`: attribute required-state projection.
- `apps/train/ui/data_mapping_panel.py`: existing table display confirmed; no code changes needed.
- `core/data_definition/projection.py`, `core/data_definition/validation.py`: mapping requirement source semantics.
- `tests/test_apps_train_data_mapping_*`, `tests/test_core_mapping_editor_*`: compatibility behavior.
- broad read: none.
- repeated read: Data Mapping service/controller, reason: compatibility failure triage after default requirements affected synthetic providers.

## Structure Warnings

Existing unrelated calculator/code-map warnings remain. No changed/new source file emitted a structure warning.

## Known Failures / Risks

- Dynamic requirement metadata is carried through the existing group notes field to avoid a broader editor model contract change in this slice.
- Unknown future mapping entities are reported as missing groups; this slice does not create new mapping groups automatically.

## Scope Compliance

- No `config/**`, `data/**`, `model/**`, `apps/predict/**`, Feature Catalog, schema writer, or production mapping write changes.
- Mapping values remain edited and saved only through Data Mapping Manager.

## Commit / Push

Slice 3 source, test, and report changes are included in the slice commit. Push is deferred until all requested slices complete.

## Project Memory Delta

No memory seed update required. The slice completes the planned Arc 15D requirement handoff without adding a new project-level decision.
