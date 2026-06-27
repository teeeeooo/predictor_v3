# 512 PredictWorkspace Execution Integration

## Goal

Connect the PredictWorkspace run button to the prediction controller/service
foundation while preserving UI/table/core boundaries.

## Scope

- Added `PredictionController` ownership to `PredictWorkspace`.
- Connected `예측 실행` button to `PredictionController.run_all()`.
- Added status text for start, finish, invalid/error counts, and unexpected
  controller errors.
- Added per-row result refresh callback via `ResultTableModel.refresh_case_id()`.
- Extended status-area counts to include running and invalid rows.

## Changed Files

- `apps/predict/ui/workspace.py`
- `result_reports/active/512_predict-workspace-execution-integration.md`

## Verification

- `python3 -B -m py_compile app_predict.py app_train.py apps/predict/app.py apps/predict/ui/shell.py apps/predict/ui/workspace.py apps/predict/ui/tables/input_table_model.py apps/predict/ui/tables/result_table_model.py apps/predict/ui/tables/table_sync.py apps/predict/controllers/*.py apps/predict/adapters/*.py apps/predict/services/*.py apps/predict/state/*.py apps/train/app.py apps/train/ui/shell.py` - passed.
- `python3 -B -c "import app_predict; import app_train; import apps.predict.app; import apps.train.app"` - passed.
- `QT_QPA_PLATFORM=offscreen` PredictWorkspace / TrainShell construction plus `_run_prediction()` smoke - passed with Qt font alias warning only.
- `rg -n "QTableWidget|from ui\\.|import ui\\.|ui\\.predict_window|ui\\.train_window|Traceback|traceback\\.print_exc" app_predict.py app_train.py apps/predict apps/train` - no matches.
- `python3 -B tools/check_code_structure.py` - passed with pre-existing
  calculator soft-limit warnings and code-map freshness warning.
- `git diff --check` - passed.
- `git status --short` - checked.

Skipped:

- pytest: focused import/offscreen execution smoke covered this slice.
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

- `apps/predict/controllers/prediction_controller.py`: execution boundary.
- `apps/predict/ui/workspace.py`: button/status/result refresh integration.
- `docs/agent_workflows/UI_SURFACE_WORKFLOW.md`: result/status surface checks.
- `docs/ui_ux/03_SPREADSHEET_TABLE_UX_CONTRACT.md` and
  `docs/ui_ux/05_INPUT_MATRIX_AND_RESULT_SURFACE_RULES.md`: table/result
  acceptance and known gap context.

## UI/UX Contract Check

Pass:

- Run button is no longer an active no-op.
- Raw tracebacks are not shown in the workspace.
- Result updates flow through session/model notification boundaries.
- Result table remains read-only and case_id is not exposed as a user-facing
  column.

Gap / deferred:

- Worker/progress/cancel UI is not implemented; synchronous execution is a
  foundation path only and should not be treated as final large-batch behavior.
- TSV copy/paste, clear, undo, Tab/Enter navigation, click/type replace-on-type,
  and validation rendering remain separate table UX parity work.
- Selected-row and dirty-row execution scopes remain follow-ups; this slice uses
  all rows.

## Known Risks

- Local `model/model.pkl` is missing, so successful model prediction could not
  be smoked locally.
- Actual prediction latency with a real model is unknown; worker/progress should
  be considered before large-batch production use.

## Commit / Push

Commit is performed for this slice. Push is performed after Arc closeout.
