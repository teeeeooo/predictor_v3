# Arc 15B Data Definition Read-only UI

## Goal

Add a Train/Admin read-only Data Definition tab that displays the Arc 15A
`DataDefinitionReport` without edit, save, runtime, config, mapping, training,
or model behavior changes.

## Modified Files

- `apps/train/services/data_definition_service.py`
- `apps/train/controllers/data_definition_controller.py`
- `apps/train/ui/data_definition_panel.py`
- `apps/train/ui/shell.py`
- `tests/test_train_data_definition_readonly_ui.py`
- `result_reports/active/715_arc15b-data-definition-readonly-ui.md`

## UI Summary

- Added a read-only Data Definition panel to the Train/Admin shell.
- Added Summary, Projected Features, Mapping Requirements, One-hot
  Relationships, Readiness, and Issues tables.
- Added a Refresh button that only reloads the report through the controller.
- Summary shows report status, projected/catalog counts, parity issue count,
  mapping requirement count, one-hot relationship count, readiness summary, and
  error issue count.
- The tab order is now Predict, Train / Model, Data Definition, Data Mapping,
  Feature Catalog. Existing Data Mapping and Feature Catalog tabs remain.

## MVC / SoC Boundary

- Service: `DataDefinitionService` calls
  `core.data_definition.build_data_definition_report()` and does not own
  training data defaults, path policy, save, or write behavior.
- Controller: `DataDefinitionController` converts the core report into
  UI-facing rows and summary state. It does not implement projection or
  validation logic.
- Panel: `DataDefinitionPanel` builds PySide6 read-only widgets and formats
  display tables only.
- Shell: `TrainShell` only imports and registers the new Data Definition tab.

## Read-only Guarantees

- No Save, Apply, Import, or Export actions were added.
- Tables use `QTableView` plus the existing read-only `QAbstractTableModel`.
- Table edit triggers are disabled.
- No `Practice_4.csv` or training data filename default was introduced.
- No core, config, mapping, Predict runtime, Data Mapping, or Feature Catalog
  behavior was changed.

## Validation Result

- `python3 -m py_compile apps/train/services/data_definition_service.py apps/train/controllers/data_definition_controller.py apps/train/ui/data_definition_panel.py`:
  OK.
- `python3 -m pytest tests/test_train_data_definition_readonly_ui.py tests/test_data_definition_core_projection.py tests/test_predict_schema_catalog_v2_projection.py`:
  OK, 27 passed.
- `python3 -B tools/check_code_structure.py`: OK with pre-existing calculator
  hotspot warnings and stale code-map reminder; no changed-file warning.
- `python3 -B tools/code_checker/build_reference_map.py --check`: STALE;
  recorded as source-change evidence, no unrelated code-map regeneration.
- Programmatic controller state check: ready, 28 projected features, 8 mapping
  requirements, 2 one-hot relationships, 3 readiness rows.
- `git status --short`: OK; only expected allowed files are modified/created.
- `git diff --name-only` / `git diff --stat`: OK; tracked diff shows shell
  modification before staging new files.
- `git diff --check`: OK.
- `git diff --cached --check`: OK.
- `git diff --cached --name-only` / `--stat`: OK; staged scope is the three
  new Data Definition UI files, shell tab update, focused test, and this report.

Table parity note: this is a read-only report surface. It reuses the existing
`ReadOnlyMappingTableModel`, uses `QTableView`, prevents mutation, supports
selection/copy of rendered values through the Qt view/model path, and does not
add paste/edit/delete behavior because no cells are editable.

## Manual Check

Manual GUI smoke is not required for this focused read-only UI slice. Offscreen
panel and shell construction tests cover the wiring.

## Excluded Scope

- No Add/Edit/Save implementation.
- No Data Definition row editing.
- No `schema.csv`, `features.csv`, `mapping.json`, data, model, core, Predict,
  Data Mapping, or Feature Catalog behavior changes.
- No generic one-hot owner switch.
- No training/model readiness execution, model retrain, or artifact activation.
- No legacy wide CSV import, broad refactor, main merge, or main push.

## Structure / Change Gate

change_gate:
  new_source: small
  hotspot_delta: none
  code_map_check: checked
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner
  report_exemption: none
  read_ledger: checked

Read Ledger:
- `AGENT_TASK_ROUTER.md` and `docs/agent_workflows/UI_SURFACE_WORKFLOW.md`:
  UI/table workflow ranges, reason: UI route and validation gate.
- `docs/ui_ux/03_SPREADSHEET_TABLE_UX_CONTRACT.md` and
  `docs/ui_ux/adapters/PYQT_TABLE_IMPLEMENTATION.md`: table contract ranges,
  reason: read-only QTableView surface.
- `docs/designs/2026-07-06-arc15-unified-data-definition-manager-foundation.md`:
  Arc 15B scope and excluded behavior, reason: implementation contract.
- `result_reports/active/713_arc15a-data-definition-core-projection-validator.md`
  and `result_reports/active/714_arc15a-followup-data-definition-cleanup.md`:
  Arc 15A report and cleanup evidence, reason: report source.
- `core/data_definition/__init__.py`, `core/data_definition/report_model.py`,
  `core/data_definition/model.py`, `core/data_definition/validation.py`: public
  report model and builder ranges, reason: service/controller input.
- `apps/train/ui/shell.py`, Data Mapping service/controller/panel, Feature
  Catalog panel package, and related focused tests: sibling pattern evidence,
  reason: Train/Admin UI consistency.
- `docs/code_map/CODEBASE_REFERENCE_MAP.md`: narrow keyword check, reason:
  reuse/commonization decision.
- broad read: none.
- repeated read: none.

## Next Action

Arc 15C — Add/Edit/Save Data Definition.
