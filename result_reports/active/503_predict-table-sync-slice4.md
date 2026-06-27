# 503 Predict Table Sync Slice 4

## Goal

Synchronize Input Cases and Prediction Results table selection/vertical scroll
so the two views reinforce their shared `case_order`.

## Scope

- Added `TableSelectionScrollSync`.
- Connected input/result vertical scrollbars in both directions.
- Connected input/result row selection in both directions.
- Added guard flags to avoid signal loops.
- Added simple result row-height mirroring from the input table.
- Wired the sync helper into `PredictWorkspace`.

## Changed Files

- `apps/predict/ui/tables/table_sync.py`
- `apps/predict/ui/workspace.py`
- `result_reports/active/503_predict-table-sync-slice4.md`

## Verification

- `python3 -B -m py_compile apps/predict/ui/tables/table_sync.py apps/predict/ui/workspace.py` - passed.
- `python3 -B -c "from apps.predict.ui.tables.table_sync import TableSelectionScrollSync"` - passed.
- `QT_QPA_PLATFORM=offscreen python3 -B -c "import sys; from PySide6.QtWidgets import QApplication; from apps.predict.ui.workspace import PredictWorkspace; app=QApplication(sys.argv); w=PredictWorkspace(); assert w is not None"` - passed with Qt font alias warning only.
- `git diff --check` - passed.
- `git status --short` - checked.

Skipped:

- pytest: focused import/offscreen widget smoke covered this slice.
- Manual GUI selection smoke: not run in the agent session; offscreen
  construction smoke verifies helper wiring.

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

- `docs/architecture/pyside6_train_predict_architecture.md`: table sync
  responsibility and sorting/filtering exclusion.
- `apps/predict/ui/workspace.py`: table construction and sync wiring site.

Structure / code map judgment:

- Sync helper is UI-only and does not know prediction/model/core state.
- Sorting and filtering remain disabled.
- No common table abstraction was introduced beyond this focused sync helper.

## Known Risks

- Row-height sync mirrors current input row heights to result rows only during
  workspace refresh.
- More advanced keyboard/navigation parity remains a future table UX slice.

## Commit / Push

Commit is performed for this slice. Push is performed after Arc closeout.
