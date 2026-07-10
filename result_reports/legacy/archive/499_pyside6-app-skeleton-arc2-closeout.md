# 499 PySide6 App Skeleton Arc 2 Closeout

## Goal

Close out Arc 2 by confirming the PySide6 Train/Predict work stayed within the
package-boundary and minimal-shell scope, then point the work plan to Arc 3.

## Scope

- Audited the Slice 1-3 commits for package boundary, entrypoint, shell, and
  exclusion compliance.
- Updated `docs/WORK_PLAN.md` next action from Arc 2 preflight/skeleton to Arc 3
  PredictWorkspace variable-size batch UI skeleton.
- Added this closeout report.

## Changed Files

- `docs/WORK_PLAN.md`
- `result_reports/active/499_pyside6-app-skeleton-arc2-closeout.md`

## Arc 2 Audit

- `apps/predict/` package exists.
- `apps/train/` package exists.
- `app_predict.py` is a Predict-only thin wrapper around `apps.predict.app.main`.
- `app_train.py` is an administrator/developer thin wrapper around
  `apps.train.app.main`.
- `PredictWorkspace` exists under `apps.predict.ui.workspace`.
- `TrainShell` reuses `PredictWorkspace` in the `Predict` tab.
- `apps.predict` does not import `apps.train`.
- New production code does not import legacy `ui.*`.
- Legacy PyQt5 `ui/` files were not deleted or moved.
- No `core/` ML behavior changed.
- No input table, result table, prediction execution, training worker, or data
  mapping update behavior was implemented.

## Verification

- `python3 -B -m py_compile app_predict.py app_train.py apps/predict/app.py apps/predict/ui/shell.py apps/predict/ui/workspace.py apps/train/app.py apps/train/ui/shell.py apps/train/ui/train_model_panel.py apps/train/ui/data_mapping_panel.py` - passed.
- `python3 -B -c "import app_predict; import app_train; import apps.predict.app; import apps.train.app"` - passed.
- `rg -n "from ui\\.|import ui\\.|ui\\.predict_window|ui\\.train_window" app_predict.py app_train.py apps/predict apps/train` - no matches.
- `git diff --check` - passed.
- `git status --short` - checked.

Skipped:

- pytest: Arc 2 is entrypoint/package/shell skeleton work only.
- Full manual GUI smoke: not repeated in closeout; Slice 3 ran a short
  offscreen shell construction smoke with exit code 0.
- code map regeneration: source structure changed, but the gate/report recorded
  checked code-map judgment and existing freshness warning; regeneration was
  not required for this Arc.

## Work Plan

Updated to make Arc 3 the next action:

- PredictWorkspace variable-size batch UI skeleton.
- Prediction execution, training execution, and data-mapping updates remain
  deferred to later approved slices.

## Known Risks

- PySide6 was installed locally during the Arc because it was required for
  shell/import smoke, but dependency files were not changed.
- The shell is intentionally not feature-complete. The next Arc must add the
  variable-size PredictWorkspace UI without wiring prediction execution.

## Commit / Push

Commit is performed for this closeout slice. Push is performed after Arc
closeout per the updated user request.
