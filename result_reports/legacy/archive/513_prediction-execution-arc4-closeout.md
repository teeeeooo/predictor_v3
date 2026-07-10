# 513 Prediction Execution Arc 4 Closeout

## Goal

Close out Arc 4 by confirming the implementation stayed within prediction
execution/result mapping foundation scope and recording the required follow-up
before moving on to Trainer work.

## Scope

- Audited Slice 1-4 changes.
- Updated `docs/WORK_PLAN.md` next action from Arc 4 start to Arc 4 follow-up:
  prediction worker/progress boundary and real-model smoke readiness.
- Added this closeout report.

## Changed Files

- `docs/WORK_PLAN.md`
- `result_reports/active/513_prediction-execution-arc4-closeout.md`

## Arc 4 Audit

- `app_predict.py` and `app_train.py` remain thin wrappers.
- Prediction input adapter exists under `apps/predict/adapters/` and is not
  UI/widget-owned.
- Prediction service exists under `apps/predict/services/` and is Qt-free.
- Prediction controller exists under `apps/predict/controllers/` and mediates
  workspace-to-service execution.
- UI/workspace/table models do not directly call core ML.
- Result mapping is internal `case_id` based.
- Case ID is not exposed as a user-facing table column.
- Result table avoids raw `None`, raw dict, raw traceback, and long float noise
  through result adapter/model display boundaries.
- Row-level invalid/error handling exists.
- Partial row failures become row-level results rather than silently failing the
  batch.
- TrainShell Predict tab still reuses `PredictWorkspace`.
- Legacy `ui/` files were not deleted or moved.
- New production code does not import legacy `ui.*`.
- Core ML behavior, artifacts, fixtures, golden files, calculator code, training
  execution, mapping update, and paste/export were not changed.

## Verification

- `python3 -B -m py_compile app_predict.py app_train.py apps/predict/app.py apps/predict/ui/shell.py apps/predict/ui/workspace.py apps/predict/ui/tables/input_table_model.py apps/predict/ui/tables/result_table_model.py apps/predict/ui/tables/table_sync.py apps/predict/controllers/*.py apps/predict/adapters/*.py apps/predict/services/*.py apps/predict/state/*.py apps/train/app.py apps/train/ui/shell.py` - passed.
- `python3 -B -c "import app_predict; import app_train; import apps.predict.app; import apps.train.app"` - passed.
- `QT_QPA_PLATFORM=offscreen` PredictWorkspace / TrainShell construction smoke - passed with Qt font alias warning only.
- `rg -n "QTableWidget|from ui\\.|import ui\\.|ui\\.predict_window|ui\\.train_window|Traceback|traceback\\.print_exc" app_predict.py app_train.py apps/predict apps/train` - no matches.
- `git diff --check` - passed.
- `git status --short` - checked.

Skipped:

- pytest: focused compile/import/offscreen smoke covered this foundation arc.
- Successful real-model prediction smoke: blocked by missing `model/model.pkl`
  in the current checkout.
- Full manual GUI smoke: not run in the agent session.

## UI/UX Contract Check

Pass:

- Run button is connected to real controller/service flow, not a no-op.
- Result table remains read-only.
- Case ID remains internal identity only.
- Row-level invalid/error messages are concise and user-facing.

Gap:

- Worker/progress/cancel UI is not implemented.
- TSV copy/paste, clear, undo, Tab/Enter navigation, click/type
  replace-on-type, and validation rendering remain separate table UX parity
  work.
- Selected-row and dirty-row execution scopes remain follow-ups; this foundation
  uses all rows.

## Work Plan

Updated next action:

- Resolve Arc 4 follow-up: prediction worker/progress boundary and real-model
  smoke readiness.
- Then start Arc 5: Trainer Admin App foundation.

## Known Risks

- Synchronous execution is foundation-only and should not be treated as final
  large-batch behavior.
- Real prediction success was not verified locally because the model artifact is
  absent and dependency/artifact files are outside this task scope.

## Commit / Push

Commit is performed for this closeout slice. Push is performed after closeout.
