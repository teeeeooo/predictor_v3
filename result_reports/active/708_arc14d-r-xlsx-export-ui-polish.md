# Arc 14D-R XLSX Export UI Polish

## Goal

Resume the blocked Arc 14D implementation after Bundle 2A/2A-F dependency
foundation work by adding Data Mapping Manager XLSX read-only snapshot export,
preserving JSON export, polishing stale UI/status wording, and distinguishing
Predict invalid mapping status from missing mapping status.

## Slice Results

- 14D-R0: OK - re-audited export/UI/status paths and updated the Arc 14D design
  record with the resumed implementation boundary.
- 14D-R1: OK - added `openpyxl` XLSX workbook generation under
  `core/mapping/editor_export.py` with focused workbook tests.
- 14D-R2: OK - wired service/controller/UI JSON/XLSX export selection while
  preserving JSON export behavior and dirty draft state.
- 14D-R3: OK - polished stale Data Mapping Manager docstrings and user-facing
  Import/Export wording.
- 14D-R4: OK - mapped invalid Predict mapping status to an error badge and a
  distinct edit-status message.
- 14D-R5: OK - synced design/work-plan/index docs and created this report.

## Modified Files

- `core/mapping/editor_export.py`
- `apps/train/services/data_mapping_service.py`
- `apps/train/controllers/data_mapping_controller.py`
- `apps/train/ui/data_mapping_panel.py`
- `apps/train/ui/data_mapping_models.py`
- `apps/train/ui/data_mapping_view_models.py`
- `apps/predict/ui/status_widgets.py`
- `apps/predict/ui/workspace.py`
- `tests/test_core_mapping_editor_export.py`
- `tests/test_apps_train_data_mapping_service.py`
- `tests/test_apps_train_data_mapping_controller.py`
- `tests/test_apps_train_data_mapping_ui_models.py`
- `tests/test_apps_predict_mapping_backed_dropdown.py`
- `docs/designs/2026-07-06-arc14d-data-mapping-xlsx-export-ui-polish.md`
- `docs/designs/README.md`
- `docs/WORK_PLAN.md`
- `result_reports/active/708_arc14d-r-xlsx-export-ui-polish.md`

## Export Contract

- JSON export is preserved and continues to write the existing read-only
  snapshot payload.
- XLSX export is generated with `openpyxl`.
- XLSX output is a read-only review/share/report snapshot, not an import
  contract.
- Workbook sheets are user-facing: IDU, Evap Index, ODU, Compressor,
  Refrigerant, Expansion, ODU Cond Specs, Issues, and Snapshot Info.
- Snapshot Info records that the workbook is not an import contract.
- Export uses the current draft snapshot, including dirty draft edits.
- Export does not save or modify `mapping.json`.
- Export does not clear dirty state.
- Import, Excel read, `xlwings`, and edit/reimport workflows were not
  implemented.

## UI Polish Summary

- Data Mapping Manager export dialog now offers JSON and XLSX filters.
- Missing extension is appended based on the selected export filter.
- Import remains disabled with user-facing copy directing edits to the current
  screen.
- Export tooltip states that output is a read-only review snapshot and cannot be
  imported back.
- Data Mapping Manager docstrings no longer describe the surface as read-only
  Mapping Entity/Master Data foundation.
- Predict invalid mapping status now displays as `invalid` / `error`, distinct
  from missing.
- Predict edit feedback distinguishes missing mapping file from invalid mapping
  data.

## Architecture

- Core owns export payload and workbook generation.
- Service owns export workflow and format dispatch.
- Controller owns export result to UI state conversion and failure issue rows.
- UI owns file dialog, selected filter, extension resolution, and controller
  invocation only.
- Predict dropdown/autofill logic and Runtime Cascade behavior were not
  changed.

## Validation

- 14D-R1 `python3 -m py_compile core/mapping/editor_export.py`: OK.
- 14D-R1 `python3 -m pytest tests/test_core_mapping_editor_export.py -q`: OK,
  5 passed.
- 14D-R1 `git diff --check`: OK.
- 14D-R2 py_compile changed export UI/service/controller/core files: OK.
- 14D-R2 core export tests: OK, 5 passed.
- 14D-R2 train Data Mapping service/controller/UI model tests: OK, 34 passed.
- 14D-R2 `git diff --check`: OK.
- 14D-R3 py_compile Data Mapping UI/service files: OK.
- 14D-R3 UI model tests: OK, 13 passed.
- 14D-R3 service/controller tests: OK, 21 passed.
- 14D-R3 `git diff --check`: OK.
- 14D-R4 py_compile Predict status/workspace files: OK.
- 14D-R4 Predict mapping-backed dropdown tests: OK, 22 passed.
- 14D-R4 core mapping autofill tests: OK, 13 passed.
- 14D-R4 `git diff --check`: OK.
- Final py_compile changed Python files: OK.
- Final core export tests: OK, 5 passed.
- Final train Data Mapping tests: OK, 34 passed.
- Final Predict mapping/status tests: OK, 22 passed.
- Final core mapping autofill tests: OK, 13 passed.
- Final `git diff --check`: OK.
- Final `python3 -B tools/check_code_structure.py`: OK with pre-existing
  calculator LOC/class soft warnings unrelated to this task.
- Final `python3 -B tools/code_checker/build_reference_map.py --check`: OK
  after regenerating `docs/code_map/CODEBASE_REFERENCE_MAP.md`; freshness
  `FRESH`, with informational dirty-worktree note before commit.

## Excluded Scope

- No import implementation.
- No XLSX edit/reimport workflow.
- No CSV import/export contract.
- No Excel read implementation.
- No `xlwings` implementation.
- No Runtime Cascade behavior changes.
- No Predict Schema CSV, Feature Catalog, ML/model, calculator, fixture/golden,
  requirements, or dependency structure changes.
- No unrelated refactor.

## Known Risks

- XLSX workbook styling is intentionally minimal.
- Qt validation is programmatic/offscreen; no manual desktop smoke was run.
- `openpyxl` failure path is unit-tested by import monkeypatch, not by removing
  the installed package from the environment.

## Next Action

Arc 15 - ML Catalog-Aligned Real Dataset Readiness Audit.
