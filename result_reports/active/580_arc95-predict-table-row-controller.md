# 580 Arc 9.5 Predict Table Row Controller

## Goal

- Move Predict workspace row lifecycle session mutations behind a controller and
  clear stale table undo history on reset.

## Scope

- Added `apps/predict/controllers/table_edit_controller.py`.
- Updated `PredictWorkspace` to use `TableEditController` for initial rows,
  append, remove, and reset mutations.
- Added `CaseTableView.clear_undo_history()`.
- Added focused tests for controller lifecycle, workspace source guard, and
  reset undo clearing.

## Non-goals

- Prediction execution orchestration remains in `PredictWorkspace` for this
  slice.
- No ML, calculator, schema, mapping JSON, or visual token changes.

## Verification

- `PYTHONPATH=. QT_QPA_PLATFORM=offscreen pytest -q tests/test_apps_predict_workspace_unified_table.py` - OK, 10 passed.
- `python3 -B tools/check_code_structure.py` - OK with pre-existing unrelated soft warnings and code-map freshness reminder.
- `python3 -B tools/code_checker/build_reference_map.py --check` - STALE; not regenerated in this focused controller slice.
- `git diff --check` - OK.

## Task Results

- `PredictWorkspace` no longer directly calls `case_store.append_empty_rows` or
  `case_store.remove_rows`.
- Row result clearing now happens through `TableEditController`.
- Reset clears table-local undo history so stale edits from the old context
  cannot be undone into fresh rows.

## Reference Parity / Change Gate

- Existing session/model/view boundaries were preserved; Qt begin/end model
  notification remains in the workspace because it coordinates the Qt view.
- Reuse/commonization decision: this is a Predict-specific controller because
  it operates on `PredictSession` and case/result row identity.
- `code_map_check`: checked; stale before this slice, not regenerated because
  the new controller is narrow and the map was already stale.

## Structure Warnings

- No changed/new source file emitted a LOC/class warning.
- Existing unrelated calculator and code-map freshness warnings remain.

## Changed Files

- `apps/predict/controllers/table_edit_controller.py`
- `apps/predict/ui/workspace.py`
- `apps/predict/ui/tables/case_table_view.py`
- `tests/test_apps_predict_workspace_unified_table.py`

## Known Risks

- Prediction run command orchestration still lives in `PredictWorkspace` and may
  be revisited during Arc 10 worker/progress work.

## Commit / Push

- Commit: pending for this slice.
- Push: deferred per user request until all slices complete.

## Project Memory Delta

- none
