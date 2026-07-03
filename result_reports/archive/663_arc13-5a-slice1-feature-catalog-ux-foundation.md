# Arc 13.5A Slice 1 - Feature Catalog UX Foundation

## Goal

Implement the Feature Catalog Manager UX foundation after Slice 0: user-friendly headers, allowlist dropdown delegates, Help dialog, current-state export, and baseline-diff dirty state.

## Scope

- Added application DTO support for display headers and field option candidates.
- Added Feature Catalog dropdown delegate using model/service-provided options.
- Added read-only Help dialog with role, `ml_name`, `ui_key`, zero-fill, one-hot, and retraining guidance.
- Changed table header display to user-friendly Korean labels while preserving canonical headers internally.
- Changed dirty state to compare current table rows against the loaded baseline.
- Changed panel export to write current table records, including unsaved edits.
- Added focused tests for labels, options, dirty baseline behavior, Help dialog content, and current-state export.

## Non-goals Held

- No add/delete/duplicate feature row implementation.
- No schema live refresh implementation.
- No model artifact hash implementation.
- No derived formula editor.

## Verification

- `python3 -m compileall apps/train core/ml tests/test_apps_train_feature_catalog.py tests/test_apps_train_shell.py` - OK
- `python3 -m pytest tests/test_apps_train_feature_catalog.py tests/test_apps_train_shell.py` - OK, 24 passed
- `git diff --check` - OK
- `python3 -B tools/check_code_structure.py` - NG, pre-existing unrelated raw hex literal:
  - `apps/calculator/ui/calculator_app.py:105`
- `python3 -B tools/code_checker/build_reference_map.py --check` - STALE before commit; checked for this slice and not regenerated because the temporary map did not add the new Feature Catalog UI helper files as separate entries, and a full map refresh would be lifecycle/tooling cleanup outside this UX slice.

## Table / Dialog Parity

- Table remains `QTableView` + `QAbstractTableModel`; no `QTableWidget` or `setCellWidget()` was introduced.
- Dropdowns use `QStyledItemDelegate` with combo editors and model-provided options.
- Existing copy/paste/clear/undo/navigation behavior remains in `FeatureCatalogTableView`.
- Help is a modal dialog with read-only body text and a standard close action.

## Changed Files

- `apps/train/application/feature_catalog/__init__.py`
- `apps/train/application/feature_catalog/models.py`
- `apps/train/application/feature_catalog/service.py`
- `apps/train/controllers/feature_catalog_controller.py`
- `apps/train/ui/feature_catalog/__init__.py`
- `apps/train/ui/feature_catalog/delegates.py`
- `apps/train/ui/feature_catalog/help_dialog.py`
- `apps/train/ui/feature_catalog/panel.py`
- `apps/train/ui/feature_catalog/table_model.py`
- `tests/test_apps_train_feature_catalog.py`
- `tests/test_apps_train_shell.py`

## Structure

```yaml
change_gate:
  new_source: justified
  hotspot_delta: none
  code_map_check: checked
  ui_literal_exemption: none
  reuse_commonization: local-with-reason
  report_exemption: none
  read_ledger: included
```

Reuse/commonization decision: checked the existing Predict dropdown delegate and table helper pattern. Feature Catalog gets a local delegate because options come from Feature Catalog DTOs and the common table helper cleanup is explicitly Slice 5, not Slice 1. The existing Predict clipboard/undo helper reuse remains unchanged until Slice 5.

## Read Ledger

- `docs/designs/2026-07-02-arc13-5a-feature-catalog-manager-correction-design.md` - Slice 1 scope and non-goals.
- `AGENT_TASK_ROUTER.md` - Shared, UI, coding, ML, docs, result report, commit routes.
- `docs/agent_workflows/UI_SURFACE_WORKFLOW.md` - table/dialog gates.
- `docs/ui_ux/03_SPREADSHEET_TABLE_UX_CONTRACT.md` - table parity checklist.
- `docs/ui_ux/adapters/PYQT_TABLE_IMPLEMENTATION.md` - Qt table/delegate pattern.
- `docs/ui_ux/07_WINDOW_GEOMETRY_AND_VIEWPORT_POLICY.md` - dialog lifecycle policy.
- Feature Catalog application, controller, panel, model, and table view files.
- `tests/test_apps_train_feature_catalog.py`, `tests/test_apps_train_shell.py`.

## Risks

- `source` and `mapping_key` dropdown candidates are inferred from existing catalog rows until a dedicated mapping allowlist owner is implemented.
- Code map remains stale from pre-existing repository state; this slice recorded a checked judgment but did not perform lifecycle cleanup.

## Commit / Push

Committed as one Slice 1 commit. Push is deferred until all requested Arc 13.5A remaining slices are complete.

## Next

Arc 13.5A Slice 2 - Add / Delete / Duplicate feature rows.
