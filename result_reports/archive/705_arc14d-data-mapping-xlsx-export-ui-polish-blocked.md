# Arc 14D Data Mapping XLSX Export / UI Polish - Blocked

## Goal

Add Data Mapping XLSX read-only snapshot export, integrate JSON/XLSX export
selection in the UI, polish related Data Mapping copy, and distinguish invalid
Predict mapping status from missing mapping status.

## Scope Completed

- 14D-0 current-state audit.
- Dependency audit for workbook writer libraries.
- Design note capturing current JSON export path, UI/status wording findings,
  and blocked implementation contract.

## Blocker

Implementation is blocked by the explicit dependency gate in the prompt:

- no project dependency manifest exists in this checkout;
- `openpyxl` is installed in the current system Python environment but is not a
  declared project dependency;
- `xlsxwriter` is not installed;
- existing `openpyxl` imports are archived reverse-engineering scripts only,
  not current production dependency evidence.

Per user instruction, a new dependency must not be added arbitrarily, and XLSX
must not be hand-written through raw zip/XML. Therefore slices 14D-1 through
14D-4 were not started.

## Slice Results

- 14D-0: OK - audited JSON export path, UI/status wording, and dependency
  availability; wrote the design note.
- 14D-1: NG - blocked before implementation by missing approved XLSX writer
  dependency.
- 14D-2: skipped - blocked by 14D-1.
- 14D-3: skipped - blocked by 14D-1 per bundle rule.
- 14D-4: skipped - final implementation verification and push not run.

## Current Export Path

- `core/mapping/editor_export.py` owns JSON payload and write behavior.
- `DataMappingService.export_snapshot()` exports the current draft without
  saving `mapping.json`.
- `DataMappingController.export_json()` maps success/failure to UI state.
- `DataMappingPanel._export()` opens a JSON-only save dialog and delegates to
  the controller.

## UI Polish Findings

- `DataMappingPanel` docstring still says read-only although the manager is now
  editable.
- Import disabled reason still says `Read-only mode.`
- Export action key still uses internal `export_csv_v2`, though the user label
  is `Export`.
- Export dialog currently offers JSON only.
- Predict `mapping_status_badge_state()` maps `invalid` to missing.
- Predict edit status message distinguishes missing only, not invalid.

## Validation

- `git diff --check`: OK.
- `git status --short`: expected 14D-0 docs/report changes before commit.

## Changed Files

- `docs/designs/2026-07-06-arc14d-data-mapping-xlsx-export-ui-polish.md`
- `docs/designs/README.md`
- `result_reports/active/705_arc14d-data-mapping-xlsx-export-ui-polish-blocked.md`

## Export Contract

- JSON export preserved: yes, unchanged.
- XLSX export added: no, blocked.
- XLSX read-only review snapshot: no, blocked.
- XLSX import contract created: no.
- dirty draft export preserves dirty state: yes for existing JSON path.
- export modifies `mapping.json`: no for existing JSON path.
- Import implemented: no.

## Architecture

- core owns export payload/workbook generation: intended, not implemented.
- service/controller/UI responsibilities preserved: yes, no source changes.
- UI raw JSON/XLSX content creation: no.
- unrelated refactor: no.
- schema/public API changed: no.
- Feature Catalog changed: no.
- ML/model/calculator changed: no.

## Read Ledger

- `spreadsheets` skill: lines 1-220, reason: XLSX task handling guidance.
- `AGENT_TASK_ROUTER.md`: lines 124-260 and 296-345, reason: report, commit,
  coding, test, UI, and ML/Predictor route requirements.
- `docs/agent_workflows/UI_SURFACE_WORKFLOW.md`: lines 1-220, reason:
  export/status UI surface workflow.
- `docs/ui_ux/05_INPUT_MATRIX_AND_RESULT_SURFACE_RULES.md`: lines 1-240,
  reason: export/result surface policy.
- `docs/WORK_PLAN.md`: keyword ranges for Arc 14D next action and constraints.
- `docs/designs/2026-07-05-arc14b5-data-mapping-ui-crud-workflow-design.md`:
  keyword ranges for read-only export policy.
- `docs/designs/2026-07-05-arc14c-runtime-cascade-integration.md`: keyword
  ranges for missing/invalid mapping behavior and XLSX exclusion.
- `result_reports/active/702_arc14b5-data-mapping-crud-implementation-bundle.md`:
  keyword ranges for JSON export and deferred XLSX.
- `result_reports/active/703_arc14b5g-data-mapping-validation-reload-feedback-fixes.md`:
  keyword ranges for export failure feedback.
- `result_reports/active/704_arc14c-runtime-cascade-integration.md`: keyword
  ranges for invalid mapping behavior and next action.
- `docs/code_map/CODEBASE_REFERENCE_MAP.md`: keyword ranges for mapping
  hotspots.
- `core/mapping/editor_export.py`: lines 1-260, reason: current JSON export
  owner.
- `core/mapping/editor_model.py`: lines 1-260, reason: draft/group/row model.
- `apps/train/services/data_mapping_service.py`: lines 1-340, reason: service
  export workflow.
- `apps/train/controllers/data_mapping_controller.py`: lines 1-360, reason:
  controller export state handling.
- `apps/train/ui/data_mapping_panel.py`: lines 1-420, reason: export dialog and
  stale wording.
- `apps/train/ui/data_mapping_models.py`: lines 1-260, reason: table model
  copy/status inspection.
- `apps/train/ui/data_mapping_view_models.py`: lines 1-260, reason: issues
  presentation columns.
- `apps/predict/ui/status_widgets.py`: lines 1-180, reason: mapping badge
  status mapping.
- `apps/predict/ui/workspace.py`: lines 80-100 and 330-342, reason: mapping
  badge and edit status message.
- `tests/test_core_mapping_editor_export.py`: lines 1-260, reason: JSON export
  tests.
- `tests/test_apps_train_data_mapping_service.py`: lines 1-320, reason: export
  service tests.
- `tests/test_apps_train_data_mapping_controller.py`: lines 1-320, reason:
  export controller tests.

## Change Gate

```yaml
change_gate:
  new_source: none
  hotspot_delta: none
  code_map_check: checked
  ui_literal_exemption: none
  reuse_commonization: checked
  report_exemption: none
  read_ledger: included
```

Code map judgment: checked mapping/export/UI hotspots; no source structure
change or code map regeneration needed for this blocked audit slice.

## Commit / Push

- 14D-0 commit is recorded in the terminal response.
- Push: not run because the bundle is blocked before implementation.

## Next Required Action

Approve and record a project XLSX writer dependency, then resume Arc 14D from
14D-1. Candidate dependency should be explicit, such as `openpyxl` or
`xlsxwriter`, before implementation starts.
