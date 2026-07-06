# Arc 15C-3 Data Definition Edit UI Draft Workflow

## Goal

Add an in-memory Data Definition draft editing workflow in Train/Admin without connecting the schema writer save action.

## Scope

- Added service/controller draft loading, cell edit mutation, reset, and save-plan preview.
- Added a Data Definition draft table model with cell editability, restricted-cell tooltips, and changed-cell highlighting.
- Added UI panels for draft rows, draft changes, save-plan targets, and blockers while preserving the existing read-only report tables.
- Added focused UI/service/controller/model tests for draft edit, reset, restricted fields, and preview state.

## Non-goals

- No schema write/save button.
- No config, data, model, Predict runtime, Data Mapping, Feature Catalog, retrain, or artifact activation changes.
- No `features.csv` write and no derived policy persistence implementation.

## Verification

- `python3 -B tools/check_code_structure.py`: passed with existing unrelated soft warnings; no changed/new source file emitted a structure warning.
- `python3 -B tools/code_checker/build_reference_map.py --check`: checked; reference map remains stale and was not regenerated in this slice.
- `python3 -m py_compile $(find core/data_definition apps/train -name '*.py' -print)`: passed.
- `python3 -m pytest tests/test_train_data_definition_readonly_ui.py tests/test_train_data_definition_edit_ui.py tests/test_data_definition_save_contract.py tests/test_data_definition_schema_writer.py`: passed, 35 tests.
- `git diff --check`: passed after report creation.
- `git status --short`: expected slice 1 source/test/report files only before staging.

## Task Results

- `DataDefinitionService` now owns in-memory draft loading and field edits through core draft/edit-policy helpers.
- `DataDefinitionController` now exposes draft rows, editability state, changed fields, save targets, and blocker preview rows.
- `DataDefinitionPanel` now shows the editable draft table plus reset/reload behavior and previews, while existing summary/projection/mapping/readiness/issue tables stay read-only.
- `DataDefinitionDraftTableModel` keeps UI mechanics thin: it displays controller state, checks cell flags, and delegates mutation back to the panel/controller.

## Table Parity / Reference Evidence

- Checked existing PySide table implementations: Data Mapping small table models, Predict input/case table models, and Feature Catalog editable table/view.
- Reused the existing `QAbstractTableModel` pattern and common style tokens.
- Did not import the Feature Catalog table view because it is surface-owned and would create a cross-surface dependency from Data Definition to Feature Catalog.
- Adapter gap: full spreadsheet parity for copy/paste/undo/navigation is not complete in this slice; focused automated coverage guards field editability, mutation, reset, and preview behavior. A common train table interaction owner should be considered before broad reuse.

## Change Gate

```yaml
change_gate:
  new_source: small
  hotspot_delta: accepted-for-slice
  code_map_check: checked
  ui_literal_exemption: none
  reuse_commonization: local-with-reason
  report_exemption: none
  read_ledger: included
```

- `new_source`: `apps/train/ui/data_definition_models.py` is a small feature-local UI model.
- `hotspot_delta`: accepted for this slice because `data_definition_panel.py` only gained wiring for the new model and preview tables; broader table interaction commonization is deferred.
- `reuse_commonization`: local-with-reason; existing Feature Catalog interaction view is not reused across surface ownership boundaries.

## Read Ledger

- `AGENT_TASK_ROUTER.md`: relevant report, coding, UI, and validation route sections.
- `docs/agent_workflows/RESULT_REPORT_WORKFLOW.md`: report numbering, content, validation, commit/push rules.
- `docs/agent_workflows/UI_SURFACE_WORKFLOW.md`: table surface gate and validation owner.
- `docs/ui_ux/03_SPREADSHEET_TABLE_UX_CONTRACT.md`: table contract and parity checklist.
- `docs/ui_ux/adapters/PYQT_TABLE_IMPLEMENTATION.md`: model/view/delegate table pattern.
- `docs/designs/2026-07-06-arc15-unified-data-definition-manager-foundation.md`: Arc 15 owner boundary and slice plan.
- `result_reports/active/716_arc15c1-data-definition-save-contract-draft-foundation.md`, `717`, `718`, `719`: draft/save-plan/writer guard decisions.
- `core/data_definition/draft.py`, `edit_policy.py`, `save_contract.py`, `schema_writer.py`, `validation.py`: draft and save preview public contracts.
- `apps/train/services/data_definition_service.py`, `apps/train/controllers/data_definition_controller.py`, `apps/train/ui/data_definition_panel.py`: target service/controller/UI owners.
- `apps/train/ui/data_mapping_models.py`, `apps/train/ui/feature_catalog/table_model.py`, `apps/train/ui/feature_catalog/table_view.py`, `apps/predict/ui/tables/input_table_model.py`: bounded reference table implementations.
- broad read: none.
- repeated read: none.

## Structure Warnings

Existing unrelated soft warnings remain in calculator and code-map freshness areas. Changed/new files did not trigger structure warnings.

## Known Failures / Risks

- Full Excel-like table parity is weaker than the project-wide table contract for this new draft table; copy/paste/undo should be handled by a future common table interaction owner if this table becomes a high-volume editing surface.
- Save remains preview-only in this slice by design.

## Scope Compliance

- No writes to `config/**`, `data/**`, or `model/**`.
- No Predict runtime logic, Data Mapping behavior, Feature Catalog behavior, training execution, retrain, artifact activation, main merge, or main push.

## Commit / Push

Slice 1 source, test, and report changes are included in the slice commit. Push is deferred until all requested slices complete.

## Project Memory Delta

No memory seed update required. This slice follows the active Arc 15 design and prior active reports without adding a new unresolved project-level decision.
