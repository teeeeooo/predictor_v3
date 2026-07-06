# Arc 14B-5G Data Mapping Validation / Reload / Feedback Fixes

## Goal

Fix blocker issues found after Arc 14B-5B~5F: ODU Cond Specs duplicate
validation, dirty reload confirmation, Save/Export failure feedback, and the
Data Mapping service class-count structure warning.

## Modified Files

- `core/mapping/editor_validation.py`
- `apps/train/services/data_mapping_types.py`
- `apps/train/services/data_mapping_service.py`
- `apps/train/controllers/data_mapping_controller.py`
- `apps/train/ui/data_mapping_panel.py`
- `tests/test_core_mapping_editor_validation.py`
- `tests/test_apps_train_data_mapping_controller.py`
- `tests/test_apps_train_data_mapping_ui_models.py`
- `docs/WORK_PLAN.md`
- `docs/code_map/CODEBASE_REFERENCE_MAP.md`
- `result_reports/active/703_arc14b5g-data-mapping-validation-reload-feedback-fixes.md`

## Bug Fixed

- ODU Cond Specs duplicate validation: same ODU across different Fin/Pi/Row
  rows is allowed; only duplicate `ODU + Fin Type + Pi + Row` combinations are
  blocking.
- Dirty reload confirmation: UI now prompts before discarding dirty draft
  changes and skips reload when the user cancels.
- Save failure feedback: controller state now reports `Save failed.` and adds a
  user-facing Save issue row when persistence fails.
- Export failure feedback: controller state now reports `Export failed.` and
  adds a user-facing Export issue row when snapshot export fails.

## Service Split Decision

Performed a small split:

- Moved `DataMappingAction`, `DataMappingSnapshot`, and `MappingDraftProvider`
  into `apps/train/services/data_mapping_types.py`.
- Kept provider implementations and workflow methods in
  `apps/train/services/data_mapping_service.py`.
- Result: the prior `data_mapping_service.py` top-level class soft warning is
  removed without a broad refactor; structure warnings decreased from the
  previous 10-warning state to 9 existing unrelated warnings.

## Validation

- py_compile: OK
  `python3 -m py_compile core/mapping/editor_validation.py apps/train/services/data_mapping_types.py apps/train/services/data_mapping_service.py apps/train/controllers/data_mapping_controller.py apps/train/ui/data_mapping_panel.py apps/train/ui/data_mapping_models.py apps/train/ui/data_mapping_view_models.py`
- editor validation tests: OK
  `python3 -m pytest tests/test_core_mapping_editor_validation.py -q`
- persistence/export tests: OK
  `python3 -m pytest tests/test_core_mapping_editor_persistence.py tests/test_core_mapping_editor_export.py -q`
- train data mapping tests: OK
  `python3 -m pytest tests/test_apps_train_data_mapping_service.py tests/test_apps_train_data_mapping_controller.py tests/test_apps_train_data_mapping_ui_models.py -q`
- Qt programmatic smoke: OK, covered by
  `tests/test_apps_train_data_mapping_ui_models.py`.
- git diff check: OK
  `git diff --check`
- structure guard: OK with 9 existing unrelated warnings
  `python3 -B tools/check_code_structure.py`
- code map: regenerated and fresh
  `python3 -B tools/code_checker/build_reference_map.py`
  `python3 -B tools/code_checker/build_reference_map.py --check`

## Architecture

- UI still does not parse or write raw JSON.
- Core owns draft validation.
- Service owns draft workflow and persistence/export calls.
- Controller converts service results into UI-facing status and Issues state.
- UI owns the reload confirmation dialog and forwards commands.
- No Import, XLSX export, Runtime Cascade Integration, Predict Schema Catalog,
  Feature Catalog, ML, model, calculator, fixture, or golden changes.

## Manual Check Required

No manual GUI check is required for this slice. Dirty reload behavior is covered
by Qt offscreen programmatic tests using a confirmation hook.

## Next Action

Arc 14C - Runtime Cascade Integration.

```yaml
change_gate:
  new_source: small
  hotspot_delta: accepted-for-slice
  code_map_check: regenerated
  ui_literal_exemption: none
  reuse_commonization: local-with-reason
  report_exemption: none
  read_ledger: included
```

Change gate notes:

- `new_source`: small; `data_mapping_types.py` contains DTO/protocol types only.
- `hotspot_delta`: accepted for this slice; service warning was reduced, while
  controller/panel changes are feedback and confirmation wiring.
- `reuse_commonization`: local with reason; reload confirmation is local to this
  panel because the prompt specified one Data Mapping workflow and no shared
  confirm abstraction exists in the Train UI.
- `code_map_check`: regenerated after adding the service type module.

## Commit / Push

Final commit/push result will be reported in terminal output.
