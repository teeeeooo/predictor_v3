# 504 PredictWorkspace Arc 3 Closeout

## Goal

Close out Arc 3 by confirming the PredictWorkspace work stayed within the
variable-size batch UI skeleton scope, then point the work plan to Arc 4.

## Scope

- Audited Arc 3 state, table model, split-table UI, and sync slices.
- Adjusted `PredictWorkspace` constructor argument order so existing
  `PredictShell` and `TrainShell` parent-based construction remains valid while
  still allowing session injection by keyword.
- Updated `docs/WORK_PLAN.md` next action to Arc 4 prediction execution/result
  mapping skeleton.
- Added this closeout report.

## Changed Files

- `apps/predict/ui/workspace.py`
- `docs/WORK_PLAN.md`
- `result_reports/active/504_predict-workspace-arc3-closeout.md`

## Arc 3 Audit

- `PredictSession` and `CaseStore` own variable-size case list and shared
  `case_order`.
- Row count is not fixed; UI default rows are constructor-configured display
  seed rows only.
- `InputTableModel` and `ResultTableModel` use the same session/case order.
- `ResultRow` is linked by `case_id`, and result lookup is by `case_id`.
- `PredictWorkspace` contains Input Cases and Prediction Results split
  `QTableView` surfaces.
- `TrainShell` still reuses `PredictWorkspace` in its Predict tab.
- `QTableWidget` was not used.
- Prediction execution was not implemented.
- `core.predictor.predict_row` was not called.
- Training, mapping, calculator, model artifact, fixture, golden, data, and
  core ML behavior were not changed.
- New production code does not import legacy `ui.*`.

## Verification

- `python3 -B -m py_compile app_predict.py app_train.py apps/predict/app.py apps/predict/ui/shell.py apps/predict/ui/workspace.py apps/predict/ui/tables/input_table_model.py apps/predict/ui/tables/result_table_model.py apps/predict/ui/tables/table_sync.py apps/predict/state/case_row.py apps/predict/state/result_row.py apps/predict/state/case_store.py apps/predict/state/predict_session.py apps/train/app.py apps/train/ui/shell.py` - passed.
- `python3 -B -c "import app_predict; import app_train; import apps.predict.app; import apps.train.app"` - passed.
- `QT_QPA_PLATFORM=offscreen python3 -B -c "import sys; from PySide6.QtWidgets import QApplication; from apps.predict.ui.workspace import PredictWorkspace; from apps.train.ui.shell import TrainShell; app=QApplication(sys.argv); pw=PredictWorkspace(); tw=TrainShell(); assert pw is not None and tw is not None"` - passed with Qt font alias warning only.
- `rg -n "QTableWidget|core\\.predictor|predict_row|from ui\\.|import ui\\.|ui\\.predict_window|ui\\.train_window" app_predict.py app_train.py apps/predict apps/train` - no matches.
- `python3 -B tools/check_code_structure.py` - passed with pre-existing
  calculator soft-limit warnings and code-map freshness warning.
- `git diff --check` - passed.
- `git status --short` - checked.

Skipped:

- pytest: Arc 3 is UI/state/table skeleton work with focused import and
  offscreen widget smoke.
- Manual GUI smoke: not run in the agent session; offscreen construction smoke
  covered PredictWorkspace and TrainShell instantiation.

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

- `docs/architecture/pyside6_train_predict_architecture.md`: Arc 3 state, table,
  workspace, and sync boundaries.
- `docs/WORK_PLAN.md`: next action and active constraints.
- `apps/predict/ui/workspace.py`: constructor compatibility and final workspace
  wiring.
- `apps/train/ui/shell.py`: Predict tab reuse smoke target.

Structure / code map judgment:

- Existing structure warnings are unrelated calculator soft-limit warnings and a
  known code-map freshness warning.
- No architecture contract change was needed.
- Active report count now exceeds the lifecycle threshold; report lifecycle
  cleanup should be a separate follow-up.

## Work Plan

Updated to make Arc 4 the next action:

- prediction execution and result mapping skeleton;
- training execution, mapping updates, calculator integration, and paste/export
  remain deferred.

## Known Risks

- Table UX is still a skeleton. Paste/export, sorting/filtering, full keyboard
  parity, validation rendering, and final column schema mapping remain future
  work.
- Arc 4 must avoid changing core ML behavior unless a later approved slice
  explicitly allows it.

## Commit / Push

Commit is performed for this closeout slice. Push is performed after Arc
closeout.
