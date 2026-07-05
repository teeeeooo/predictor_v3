# Arc 14B-5B~5F Data Mapping CRUD Implementation Bundle

## Goal

Implement the Data Mapping Manager user-facing draft, validation, CRUD, save,
and read-only export slices while preserving `mapping.json` as the runtime SSOT.

## Scope

- Slice 5B: project runtime `mapping.json` into the seven user-facing editor
  groups in read-only mode.
- Later slices in this bundle will add Predict dropdown fallback removal,
  draft validation, editable CRUD, atomic save, and read-only export.

## Non-goals

- No Import workflow.
- No CSV import/export contract.
- No raw `mapping.json` editor.
- No Feature Catalog, Predict Schema Catalog, ML, model, calculator, fixture,
  or golden changes.

## Slice Results

### 5B - Editor Draft Projection

- Added Qt-free editor draft models and runtime-to-draft projection under
  `core/mapping`.
- Projected runtime sections into the user-facing groups: IDU, Evap Index, ODU,
  Compressor, Refrigerant, Expansion, and ODU Cond Specs.
- Preserved unknown runtime sections as draft metadata.
- Reconstructed ODU Cond Specs rows through `odu_cascade` candidate
  combinations matched against `cond_specs`; unmatched `cond_specs` rows are
  preserved as unresolved draft rows.
- Switched Train Data Mapping service/controller/UI state from the generic
  entity catalog view to user-facing draft groups.
- Kept the surface read-only and preserved the no-initial-`selectRow`
  regression guard.

### 5B-F - Predict Dropdown Fallback Removal

- Removed the hard-coded Predict dropdown fallback for `ref_type` and
  `exp_type`.
- Kept dropdown option resolution on the existing mapping-backed adapter path:
  schema column key -> mapping target section -> section keys.
- Missing or empty `ref_type` / `exp_type` sections now return empty option
  tuples instead of generating `R410A` / `R32` / `R290` / `EEV` / `Capi`.

## Verification

- 5B py_compile: OK
  `python3 -m py_compile core/mapping/editor_model.py core/mapping/editor_projection.py apps/train/services/data_mapping_service.py apps/train/controllers/data_mapping_controller.py apps/train/ui/data_mapping_view_models.py apps/train/ui/data_mapping_panel.py`
- 5B projection tests: OK
  `python3 -m pytest tests/test_core_mapping_editor_projection.py -q`
- 5B Train Data Mapping tests: OK
  `python3 -m pytest tests/test_apps_train_data_mapping_service.py tests/test_apps_train_data_mapping_controller.py tests/test_apps_train_data_mapping_ui_models.py -q`
- 5B git diff check: OK
  `git diff --check`
- 5B-F py_compile: OK
  `python3 -m py_compile apps/predict/adapters/dropdown_option_adapter.py`
- 5B-F dropdown adapter tests: OK
  `python3 -m pytest tests/test_apps_predict_mapping_backed_dropdown.py -q`
- 5B-F Predict mapping controller tests: OK
  `python3 -m pytest tests/test_apps_predict_mapping_controller.py -q`

## Changed Files

- `core/mapping/editor_model.py`
- `core/mapping/editor_projection.py`
- `core/mapping/__init__.py`
- `apps/train/services/data_mapping_service.py`
- `apps/train/controllers/data_mapping_controller.py`
- `apps/train/ui/data_mapping_panel.py`
- `apps/train/ui/data_mapping_view_models.py`
- `tests/test_core_mapping_editor_projection.py`
- `tests/test_apps_train_data_mapping_service.py`
- `tests/test_apps_train_data_mapping_controller.py`
- `tests/test_apps_train_data_mapping_ui_models.py`
- `apps/predict/adapters/dropdown_option_adapter.py`
- `tests/test_apps_predict_mapping_backed_dropdown.py`
- `result_reports/active/702_arc14b5-data-mapping-crud-implementation-bundle.md`

## Known Failures / Risks

- 5B intentionally does not validate draft edits, enable Save, edit rows, save
  `mapping.json`, or export snapshots.
- ODU Cond Specs unresolved rows are preserved for data loss prevention; 5C
  will turn them into user-facing Issues.
- Table UX remains read-only in 5B; editable parity belongs to 5D.

## Scope Compliance

- Import implemented: no
- Export read-only snapshot: not yet
- `mapping.json` SSOT for `ref_type` / `exp_type`: yes for editor projection
  and Predict base dropdown options.
- `FALLBACK_DROPDOWN_OPTIONS` removed: yes.
- UI raw JSON parse/write: no
- Unknown sections preserved on save: save not yet implemented; projection
  preserves metadata.
- ODU Cond Specs derives internal sections: read projection added; save
  projection is 5E.

## Architecture

- Core owns draft projection.
- Service/controller own workflow and UI-facing state conversion.
- UI displays tables and forwards selection only.
- No schema/public API, Feature Catalog, Predict Schema Catalog, ML, model,
  calculator, fixture, or golden changes.

## Read Ledger

- `/Users/sunjaekim/Downloads/arc14b_5b_to_5f_data_mapping_crud_bundle_prompt.md`: lines 1-900, reason: user-supplied bundle contract.
- `AGENT_TASK_ROUTER.md`: lines 211-340, reason: coding/test/UI/commit routes.
- `docs/WORK_PLAN.md`: lines 1-220, reason: active Arc 14B-5 context.
- `docs/designs/2026-07-05-arc14b5-data-mapping-ui-crud-workflow-design.md`: lines 1-520, reason: user-facing group and CRUD contract.
- `docs/designs/2026-07-05-arc14b4-legacy-mapping-csv-to-json-rule-reconstruction-audit.md`: lines 1-220, reason: export/import exclusion and runtime shape.
- `docs/designs/2026-07-05-arc14b-runtime-mapping-repository-read-adapter.md`: lines 1-220, reason: existing runtime read adapter boundary.
- `docs/architecture/PROJECT_CLEAN_ARCHITECTURE_BOUNDARY.md`: lines 1-220, reason: core/service/controller/UI responsibility boundary.
- `docs/agent_workflows/UI_SURFACE_WORKFLOW.md`: lines 1-220, reason: table/UI surface gate.
- `docs/ui_ux/03_SPREADSHEET_TABLE_UX_CONTRACT.md`: lines 1-220, reason: table-shaped surface acceptance context.
- `docs/ui_ux/adapters/PYQT_TABLE_IMPLEMENTATION.md`: lines 1-220, reason: Qt table implementation constraints.
- `docs/agent_workflows/AGENT_CHANGE_GATES.md`: lines 1-220, reason: source change gate/report contract.
- `docs/agent_workflows/DIFF_READ_BUDGET.md`: lines 1-220, reason: read ledger and reuse gate.
- Source/test ranges: targeted reads of current Data Mapping service,
  controller, panel, view models, runtime adapter, dropdown adapter, and focused
  tests.
- Broad read: bundle prompt and design docs because the user explicitly supplied
  a multi-slice implementation contract.

```yaml
change_gate:
  new_source: small
  hotspot_delta: accepted-for-slice
  code_map_check: checked
  ui_literal_exemption: none
  reuse_commonization: checked
  report_exemption: none
  read_ledger: included
```

Change gate notes:

- `new_source`: small; new files live inside the existing `core/mapping` owner
  package and are split into model/projection responsibilities.
- `hotspot_delta`: accepted for this slice; existing Train service/controller/UI
  files were changed to switch projection surfaces, with no new raw JSON or file
  I/O in UI.
- `reuse_commonization`: checked; existing runtime entity adapter remains for
  generic read-only catalog use, but user-facing draft projection has distinct
  group/ODU Cond Specs rules.

## Commit / Push

- 5B commit hash is reported in terminal/final output to avoid a
  self-referential report update loop.
- 5B-F commit hash is reported in terminal/final output to avoid a
  self-referential report update loop.
- Push is deferred until all slices complete.
