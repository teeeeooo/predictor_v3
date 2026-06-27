# 505 Predict Table Polish Before Arc 4

## Goal

Polish the Arc 3 PredictWorkspace table skeleton before Arc 4 so selection sync,
row add/delete notifications, and user-facing row identity are safer for the
next prediction-result mapping slice.

## Scope

- Aligned `ResultTableView` selection mode with `InputTableView` by using
  `ExtendedSelection`.
- Removed user-facing `Case ID` display columns from Input Cases and Prediction
  Results tables.
- Kept `case_id` as internal `PredictSession` / `CaseStore` identity only.
- Kept row headers as the user-facing row identity.
- Preserved result lookup by `case_id` through `session.case_order`.
- Replaced row add/delete paths with `beginInsertRows` / `beginRemoveRows`
  notifications and reset with model reset boundaries.
- Reduced selection sync duplicate row processing for multi-row selections.

## Changed Files

- `apps/predict/ui/tables/input_table_model.py`
- `apps/predict/ui/tables/result_table_model.py`
- `apps/predict/ui/tables/result_table_view.py`
- `apps/predict/ui/tables/table_sync.py`
- `apps/predict/ui/workspace.py`
- `result_reports/active/505_predict-table-polish-before-arc4.md`

## Verification

- `python3 -B -m py_compile app_predict.py app_train.py apps/predict/app.py apps/predict/ui/shell.py apps/predict/ui/workspace.py apps/predict/ui/tables/input_table_model.py apps/predict/ui/tables/result_table_model.py apps/predict/ui/tables/table_sync.py apps/predict/ui/tables/input_table_view.py apps/predict/ui/tables/result_table_view.py apps/predict/state/case_row.py apps/predict/state/result_row.py apps/predict/state/case_store.py apps/predict/state/predict_session.py apps/train/app.py apps/train/ui/shell.py` - passed.
- `python3 -B -c "import app_predict; import app_train; import apps.predict.app; import apps.train.app"` - passed.
- `QT_QPA_PLATFORM=offscreen` PredictWorkspace add/delete smoke - passed after
  rerunning with `Qt.Horizontal` in the header assertion.
- `rg -n "QTableWidget|core\\.predictor|predict_row|from ui\\.|import ui\\.|ui\\.predict_window|ui\\.train_window" app_predict.py app_train.py apps/predict apps/train` - no matches.
- UI/UX contract read:
  - `docs/ui_ux/00_UI_UX_SYSTEM.md`
  - `docs/ui_ux/03_SPREADSHEET_TABLE_UX_CONTRACT.md`
  - `docs/ui_ux/05_INPUT_MATRIX_AND_RESULT_SURFACE_RULES.md`
- `git diff --check` - passed.
- `git status --short` - checked.

Skipped:

- pytest: focused import/offscreen table smoke covered this polish slice.
- Manual GUI smoke: not run in the agent session.

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

Read Ledger:

- `apps/predict/ui/tables/input_table_model.py`,
  `apps/predict/ui/tables/result_table_model.py`: column display and row
  notification boundaries.
- `apps/predict/ui/workspace.py`: row add/delete/reset paths.
- `apps/predict/ui/tables/table_sync.py`: multi-row selection sync behavior.

## UI/UX Contract Check

Compliant:

- User-facing tables no longer expose internal `case_id`.
- Row headers remain the user-facing row identity.
- Input and result surfaces are table-shaped `QTableView` surfaces with visible
  row and column headers.
- `case_id` remains internal state identity in `PredictSession` / `CaseStore` /
  `ResultRow`, and result lookup still follows `case_id` through
  `session.case_order`.
- Result table selection mode now matches input table multi-row selection.

Corrected in this slice:

- Removed `Case ID` display columns from input/result table schemas.
- Replaced basic row add/delete refresh with insert/remove model notification
  boundaries.
- Reset now uses model reset boundaries.
- Multi-row selection sync now de-duplicates selected row indexes.

Intentionally deferred:

- TSV copy.
- TSV paste.
- Delete/Backspace clear.
- Grouped undo.
- Tab/Enter navigation.
- Click/type replace-on-type.
- Validation rendering.

Remaining gap:

- The PredictWorkspace table is a skeleton/polish surface, not yet a
  spreadsheet-complete table per
  `docs/ui_ux/03_SPREADSHEET_TABLE_UX_CONTRACT.md`.
- Do not mix these gaps into Arc 4 prediction execution. Handle them in a
  separate table UX parity slice.

## Known Risks

- Row add/delete notifications are now model-boundary aware, but more complete
  table UX behavior is still pending.
- Arc 4 should continue to avoid prediction execution changes outside the
  approved prediction execution/result mapping skeleton.

## Commit / Push

Commit is performed for this slice. Push is not required for this task unless
requested separately.
