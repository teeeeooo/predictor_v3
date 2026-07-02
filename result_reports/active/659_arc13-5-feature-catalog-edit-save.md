# Arc 13.5 Feature Catalog Edit Save

## Goal

Allow whitelisted Feature Catalog edits and save them to the canonical catalog
only after strict validation and safe-write.

## Scope

- Added editable whitelist behavior for `label`, `notes`, `active`,
  `zero_fill_policy`, `source`, `mapping_key`, and `one_hot_group`.
- Kept `order`, `feature_id`, `ml_name`, `role`, and `ui_key` locked.
- Added dirty state, save enablement, and reload/revert workflow.
- Added strict DTO-to-canonical-row conversion errors for invalid `active`,
  invalid `zero_fill_policy`, missing required fields, and malformed rows.
- Added canonical UTF-8 without BOM safe-write through temp file and
  `os.replace`.
- Added save reload + validate flow.
- Added Feature Catalog table view support for TSV copy/paste, Delete clear,
  grouped undo, and keyboard navigation.

## Non-goals

- No row add/delete, schema change, Train runtime behavior change, Predict
  schema/result change, calculator change, or ML projection semantics change.

## Verification

- `python3 -B -m compileall -q apps/train core/ml tests` - OK
- `python3 -B -m pytest tests/test_apps_train_feature_catalog.py tests/test_apps_train_shell.py tests/test_ml_feature_catalog.py` - OK, 61 passed
- `python3 -B tools/code_checker/build_reference_map.py` - OK, map regenerated
- `git diff --check` - OK
- `python3 -B tools/check_code_structure.py --verbose` - NG, pre-existing
  unrelated `apps/calculator/ui/calculator_app.py` raw hex literal error;
  changed/new Slice 3 source files were not reported in final guard
  errors/warnings.

## Task Results

- Invalid edited values are retained in the table and surfaced as validation
  errors on save; save remains blocked and dirty state remains.
- Valid edited rows save through `write_canonical()` and reload into a fresh
  validated snapshot.
- Canonical save writes UTF-8 without BOM and uses same-directory temp file
  replacement.
- Export remains separate and still writes UTF-8-SIG.

## Table Parity

- Pass: `QTableView`, `QAbstractTableModel`, no `QTableWidget`, no
  `setCellWidget`, editable whitelist, locked-cell mutation prevention, TSV
  copy/paste, Delete/Backspace clear, grouped undo, Tab/Enter navigation, and
  invalid enum cell marking.
- Row add/delete remains intentionally out of scope.

## Reference Parity

- Reused Predict table clipboard and undo helpers
  (`apps.predict.ui.tables.clipboard`, `apps.predict.ui.tables.undo`) instead
  of duplicating TSV and grouped undo primitives.
- Kept a feature-local `FeatureCatalogTableView` because editable whitelist,
  save validation, and row add/delete restrictions are Feature Catalog-specific.

## Structure Warnings

- A changed-file class-count warning appeared during implementation in
  `apps/train/application/feature_catalog/models.py`.
- Resolved by moving export/save I/O DTOs and writer protocol to
  `apps/train/application/feature_catalog/io_models.py`.
- Final changed/new source files: no structure warnings reported.
- Existing unrelated guard failure remains in `apps/calculator/ui/calculator_app.py`.

## Read Ledger

- `apps/train/application/feature_catalog/service.py`: lines 1-226, reason: DTO conversion, validation, and save flow.
- `apps/train/adapters/feature_catalog/file_adapter.py`: lines 1-56, reason: canonical safe-write implementation.
- `apps/train/ui/feature_catalog/table_model.py`: lines 1-137, reason: editable whitelist, dirty state, invalid markers.
- `apps/train/ui/feature_catalog/table_view.py`: lines 1-203, reason: table interaction parity.
- `apps/train/ui/feature_catalog/panel.py`: lines 1-229, reason: save/reload UI state.
- `apps/predict/ui/tables/clipboard.py`: lines 1-36, reason: TSV helper reuse.
- `apps/predict/ui/tables/undo.py`: lines 1-36, reason: grouped undo helper reuse.
- `apps/predict/ui/tables/case_table_view.py`: lines 1-260, reason: existing Qt table interaction parity evidence.
- `tests/test_apps_train_feature_catalog.py`: lines 1-165, reason: focused edit/save/table interaction tests.
- broad read: none.
- repeated read: none.

## Change Gate

```yaml
change_gate:
  new_source: small
  hotspot_delta: accepted-for-slice
  code_map_check: regenerated
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner
  report_exemption: none
  read_ledger: included
```

- `hotspot_delta`: panel/service grew within soft limits; I/O DTO split avoided
  a changed-file class-count warning.
- `code_map_check`: regenerated; `docs/code_map/CODEBASE_REFERENCE_MAP.md`
  is included in the diff.
- `reuse_commonization`: reused existing Predict clipboard/undo primitives and
  kept Feature Catalog-specific view/model/service policy local.

## Known Risks

- Manual GUI smoke was not run; automated Qt tests used offscreen mode.
- Structure guard remains blocked by an unrelated pre-existing calculator UI
  literal error.

## Next Suggested Action

Proceed to Slice 4 closeout, docs sync, final validation, and push.

## Commit / Push

- Commit: included in Slice 3 commit.
- Push: deferred until Slice 4 per Arc 13.5 plan.

## Project Memory Delta

- none
