# 502 PredictWorkspace Split-table Skeleton

## Goal

Replace the PredictWorkspace placeholder with a variable-size split-table UI
skeleton for editable Input Cases and read-only Prediction Results.

## Scope

- `PredictWorkspace` now owns or receives a `PredictSession`.
- Added local display default rows through a constructor option, without fixing
  the row-count contract.
- Added command buttons: disabled prediction placeholder, reset, add row, delete
  row.
- Added split main area with `InputTableView` and `ResultTableView`.
- Added bottom status text based on `PredictSession.summary_counts()`.
- Added minimal row add/delete/reset behavior through `CaseStore`.

## Changed Files

- `apps/predict/ui/workspace.py`
- `apps/predict/ui/tables/input_table_view.py`
- `apps/predict/ui/tables/result_table_view.py`
- `result_reports/active/502_predict-workspace-split-table-skeleton.md`

## Verification

- `python3 -B -m py_compile apps/predict/ui/workspace.py apps/predict/ui/tables/input_table_model.py apps/predict/ui/tables/result_table_model.py apps/predict/ui/tables/input_table_view.py apps/predict/ui/tables/result_table_view.py` - passed.
- `python3 -B -c "from apps.predict.ui.workspace import PredictWorkspace"` - passed.
- `QT_QPA_PLATFORM=offscreen python3 -B -c "import sys; from PySide6.QtWidgets import QApplication; from apps.predict.ui.workspace import PredictWorkspace; app=QApplication(sys.argv); w=PredictWorkspace(); assert w is not None"` - passed with Qt font alias warning only.
- `git diff --check` - passed.
- `git status --short` - checked.

Skipped:

- pytest: focused import/offscreen widget smoke covered this slice.
- Manual GUI smoke: not run; offscreen construction smoke covered widget
  creation without leaving an event loop open.

## Change Gate

```yaml
change_gate:
  new_source: small
  hotspot_delta: none
  code_map_check: checked
  ui_literal_exemption: none
  reuse_commonization: checked
  report_exemption: none
  read_ledger: included
```

Read Ledger:

- `docs/architecture/pyside6_train_predict_architecture.md`: split workspace,
  table view, and no-prediction-execution boundaries.
- `apps/predict/state/predict_session.py`: session and summary-count API.
- `apps/predict/ui/tables/input_table_model.py`,
  `apps/predict/ui/tables/result_table_model.py`: model refresh and row-order
  behavior.

Structure / code map judgment:

- `QTableView` was used; `QTableWidget` was not introduced.
- No common widget hierarchy was extracted beyond small view classes because
  this slice only needs table-specific configuration.
- Prediction execution remains disabled and unimplemented.

## Known Risks

- Row delete uses selected input rows, falling back to the last row when nothing
  is selected.
- Selection/scroll synchronization is not implemented yet; that is the next
  slice.

## Commit / Push

Commit is performed for this slice. Push is performed after Arc closeout.
