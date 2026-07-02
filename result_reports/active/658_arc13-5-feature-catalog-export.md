# Arc 13.5 Feature Catalog Export

## Goal

Add Excel-safe CSV export for the Train Feature Catalog viewer without mutating
the canonical catalog.

## Scope

- Added `FeatureCatalogFileAdapter` under `apps/train/adapters/feature_catalog/`
  for UTF-8-SIG CSV export.
- Added `FeatureCatalogService.export_snapshot()` so export uses the current
  table snapshot and returns validation-aware export metadata.
- Added `FeatureCatalogController.export_csv()` to convert export failures into
  UI-safe state.
- Added `CSV 내보내기` button and export status text to `FeatureCatalogPanel`.
- Added focused export adapter/service/controller and panel state tests.

## Non-goals

- No canonical `config/ml/features.csv` writes.
- No edit/save workflow, row add/delete, schema change, Train runtime behavior
  change, Predict schema/result change, or calculator change.

## Verification

- `python3 -B -m compileall -q apps/train core/ml tests` - OK
- `python3 -B -m pytest tests/test_apps_train_feature_catalog.py tests/test_apps_train_shell.py tests/test_ml_feature_catalog.py` - OK, 56 passed
- `python3 -B tools/code_checker/build_reference_map.py` - OK, map regenerated
- `git diff --check` - OK
- `python3 -B tools/check_code_structure.py --verbose` - NG, pre-existing
  unrelated `apps/calculator/ui/calculator_app.py` raw hex literal error;
  changed/new Slice 2 source files were not reported in guard errors/warnings.

## Task Results

- Export writes UTF-8-SIG CSV and test verifies the BOM bytes.
- Export writes current snapshot headers and rows, preserving canonical header
  order in the exported copy.
- Export status reports whether the exported snapshot had validation errors.
- UI owns file selection only; file writing remains in adapter/service.

## Reference Parity

- Checked `apps/calculator/ui/table_csv_export.py`.
- Did not reuse it because it is a Tkinter UI helper that combines filedialog
  selection with CSV writing. Arc 13.5 requires PySide6 UI file selection and
  service/adapter-owned writing.

## Read Ledger

- `apps/train/application/feature_catalog/service.py`: lines 1-91, reason: export usecase insertion.
- `apps/train/application/feature_catalog/models.py`: lines 1-92, reason: export DTO/protocol insertion.
- `apps/train/controllers/feature_catalog_controller.py`: lines 1-88, reason: controlled export state.
- `apps/train/ui/feature_catalog/panel.py`: lines 1-196, reason: command bar and export status surface.
- `apps/calculator/ui/table_csv_export.py`: lines 1-39, reason: existing CSV export helper parity check.
- `tests/test_apps_train_feature_catalog.py`: lines 1-93, reason: focused export tests.
- `tests/test_apps_train_shell.py`: lines 1-230, reason: panel smoke update.
- broad read: none.
- repeated read: none.

## Change Gate

```yaml
change_gate:
  new_source: small
  hotspot_delta: accepted-for-slice
  code_map_check: regenerated
  ui_literal_exemption: none
  reuse_commonization: checked
  report_exemption: none
  read_ledger: included
```

- `hotspot_delta`: `FeatureCatalogPanel` gained export command/status wiring
  and remains below source soft limits; future edit/save should avoid growing
  it into validation or file I/O owner.
- `code_map_check`: regenerated; `docs/code_map/CODEBASE_REFERENCE_MAP.md`
  is included in the diff.
- `reuse_commonization`: existing CSV helper checked; local Train adapter used
  because calculator helper owns a different toolkit and UI/file-dialog flow.

## Structure Warnings

- Changed/new source files: none reported.
- Existing unrelated guard failure: `apps/calculator/ui/calculator_app.py`
  raw hex literal.

## Known Risks

- Manual GUI export smoke was not run; automated tests cover adapter/service
  writing and panel button state.
- Full editable table parity remains deferred to Slice 3.

## Next Suggested Action

Proceed to Slice 3 editable table and validation-gated canonical save.

## Commit / Push

- Commit: included in Slice 2 commit.
- Push: deferred until Slice 4 per Arc 13.5 plan.

## Project Memory Delta

- none
