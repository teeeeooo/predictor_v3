# Arc 13.5A Slice 5 - Common Table Helper Cleanup

## Goal

Move generic clipboard and undo helpers out of Predict-specific ownership so Train and Predict tables share a common UI helper path.

## Scope

- Added `apps/common/ui/tables/clipboard.py`.
- Added `apps/common/ui/tables/undo.py`.
- Updated Predict table views to import clipboard/undo helpers from `apps.common.ui.tables`.
- Updated Train Feature Catalog table view to import the same common helpers.
- Removed old Predict-owned generic helper modules.
- Updated focused table interaction tests for the new import path.

## Non-goals Held

- No Feature Manager behavior changes.
- No table interaction behavior changes.
- No UI visual redesign.

## Verification

- `python3 -m compileall apps/common apps/predict apps/train tests/test_apps_predict_table_interactions.py tests/test_apps_train_feature_catalog.py` - OK
- `python3 -m pytest tests/test_apps_predict_table_interactions.py tests/test_apps_train_feature_catalog.py tests/test_apps_predict_table_models.py tests/test_apps_predict_workspace_unified_table.py` - OK, 46 passed
- `git diff --check` - OK
- `python3 -B tools/check_code_structure.py --verbose` - NG, pre-existing unrelated raw hex literal:
  - `apps/calculator/ui/calculator_app.py:105`
  - Existing unrelated soft warnings remained outside changed files.
- `python3 -B tools/code_checker/build_reference_map.py --check` - STALE from existing repository state; checked and not regenerated in this feature slice.

## Changed Files

- `apps/common/ui/tables/__init__.py`
- `apps/common/ui/tables/clipboard.py`
- `apps/common/ui/tables/undo.py`
- `apps/predict/ui/tables/case_table_view.py`
- `apps/predict/ui/tables/input_table_view.py`
- `apps/predict/ui/tables/result_table_view.py`
- `apps/predict/ui/tables/clipboard.py`
- `apps/predict/ui/tables/undo.py`
- `apps/train/ui/feature_catalog/table_view.py`
- `tests/test_apps_predict_table_interactions.py`

## Structure

```yaml
change_gate:
  new_source: justified
  hotspot_delta: none
  code_map_check: checked
  ui_literal_exemption: none
  reuse_commonization: reused-existing-owner
  report_exemption: none
  read_ledger: included
```

New source justification: `apps/common/ui/tables` is the common UI helper owner for generic spreadsheet-like clipboard and undo behavior shared by Predict and Train.

Code map judgment: checked current and temporary maps. The generated map does not add the new common helper modules as separate entries, and a full stale-map refresh is outside this cleanup slice.

## Risk

External imports from the old Predict helper path would break, but repository imports now use the common path and these helpers were UI-internal.

## Commit / Push

Committed as one Slice 5 commit. Push remains deferred until closeout is complete.

## Next

Arc 13.5A closeout.
