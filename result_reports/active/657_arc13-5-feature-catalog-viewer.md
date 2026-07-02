# Arc 13.5 Feature Catalog Viewer

## Goal

Add a read-only Feature Catalog tab to Train/Admin with catalog and project
consistency validation status.

## Scope

- Added a Train Feature Catalog application service under
  `apps/train/application/feature_catalog/`.
- Added a thin controller for controlled load/error state.
- Added a read-only `QTableView` / `QAbstractTableModel` UI package under
  `apps/train/ui/feature_catalog/`.
- Added `Feature Catalog` as a top-level `TrainShell` tab.
- Added focused service/controller/table model and shell/panel tests.
- Regenerated the codebase reference map after adding source surfaces.

## Non-goals

- No export, save, edit, row add/delete, schema change, Train runtime behavior
  change, Predict schema/result change, or calculator change.

## Verification

- `python3 -B -m compileall -q apps/train core/ml tests` - OK
- `python3 -B -m pytest tests/test_apps_train_feature_catalog.py tests/test_apps_train_shell.py tests/test_ml_feature_catalog.py` - OK, 53 passed
- `python3 -B tools/code_checker/build_reference_map.py` - OK, map regenerated
- `git diff --check` - OK
- `python3 -B tools/check_code_structure.py --verbose` - NG, pre-existing
  unrelated `apps/calculator/ui/calculator_app.py` raw hex literal error;
  changed/new Slice 1 source files were not reported in guard errors/warnings.

## Task Results

- `FeatureCatalogService` loads `config/ml/features.csv`, reuses
  `load_feature_catalog()`, reuses `validate_feature_catalog()`, and cleanly
  calls `validate_registry_references()` with `MODEL_REGISTRY`.
- `FeatureCatalogController` catches load failures and returns UI-safe state
  instead of exposing raw exceptions.
- `FeatureCatalogPanel` displays path, total row count, active row count,
  validation status, and validation messages.
- `FeatureCatalogTableModel` is read-only and displays canonical headers in
  `REQUIRED_HEADERS` order.

## Reference Parity

- Checked existing Train shell/panel patterns and reused the local Panel,
  status, `QTableView`, and offscreen test conventions.
- Checked Predict table model/view patterns for `QAbstractTableModel` and
  model/view separation.
- Calculator table/export helpers were not reused because Slice 1 is a
  PySide6 Train/Admin read-only viewer and export belongs to Slice 2.

## Table Parity

- Pass: `QTableView`, `QAbstractTableModel`, no `QTableWidget`, no
  `setCellWidget`, selectable read-only cells, mutation prevention.
- Deferred: copy/paste/delete/undo/navigation parity beyond default Qt table
  behavior, because Slice 1 is a read-only viewer and export/edit are later
  slices.

## Structure Warnings

- Changed/new source files: none reported.
- Existing unrelated guard failure: `apps/calculator/ui/calculator_app.py`
  raw hex literal.
- Existing unrelated soft warnings remain in calculator/core hotspots.

## Read Ledger

- `docs/designs/2026-07-02-arc13-5-feature-catalog-editor-revised-slice-plan.md`: full file, reason: user-required Arc 13.5 slice contract.
- `apps/train/ui/shell.py`: lines 1-139, reason: TrainShell tab insertion.
- `apps/train/ui/train_model_panel.py`: lines 37-165 and 291-390, reason: panel/table construction pattern.
- `apps/train/ui/data_mapping_panel.py`: lines 26-155, reason: sibling visual-only Train panel pattern.
- `apps/train/ui/models/static_table_model.py`: lines 1-57, reason: existing read-only table model pattern.
- `core/ml/feature_catalog.py`: lines 1-151, reason: loader/model/header owner.
- `core/ml/feature_catalog_validation.py`: lines 1-127, reason: catalog and registry validation owner.
- `core/ml/registry.py`: lines 1-63, reason: project consistency validation input.
- `tests/test_apps_train_shell.py`: lines 1-257, reason: Train shell/panel test pattern.
- `docs/code_map/CODEBASE_REFERENCE_MAP.md`: lines 1-120, reason: reuse/code-map preflight.
- broad read: none beyond user-required plan file.
- repeated read: none.

## Change Gate

```yaml
change_gate:
  new_source: small
  hotspot_delta: wiring-only
  code_map_check: regenerated
  ui_literal_exemption: none
  reuse_commonization: checked
  report_exemption: none
  read_ledger: included
```

- `hotspot_delta`: `apps/train/ui/shell.py` received only tab wiring.
- `code_map_check`: regenerated; `docs/code_map/CODEBASE_REFERENCE_MAP.md`
  is included in the diff.
- `reuse_commonization`: checked sibling Train/Predict patterns; kept a local
  Train Feature Catalog package because this workflow has distinct service,
  controller, table model, and view responsibilities.

## Known Risks

- Manual GUI smoke was not run; automated Qt tests used offscreen mode.
- Full table spreadsheet parity is deferred until edit/export slices.
- Structure guard remains blocked by an unrelated pre-existing calculator UI
  literal error.

## Next Suggested Action

Proceed to Slice 2 Excel-safe export.

## Commit / Push

- Commit: included in Slice 1 commit.
- Push: deferred until Slice 4 per Arc 13.5 plan.

## Project Memory Delta

- none
