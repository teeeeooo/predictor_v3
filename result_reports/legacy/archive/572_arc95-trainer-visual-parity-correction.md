# 572 - Arc 9.5 Trainer Visual Parity Correction

## Goal

Correct Trainer visual hierarchy while keeping Trainer execution and mapping
update foundations deferred.

## Scope

- Re-check `docs/designs/assets/train_ref_img.png` as the Trainer visual
  reference.
- Confirm Trainer Predict tab reuses `PredictWorkspace`.
- Reduce top status strip emphasis and align it with low-chrome dot status
  presentation.
- Add visual-only Train / Model command row, progress area, summary table, log,
  and info summary.
- Add visual-only Data Mapping command row, source panel, status table, and log.
- Keep all trainer/mapping execution controls disabled.
- Add focused Train shell tests for construction, tab names, Predict reuse,
  disabled controls, visual widgets, and no direct execution imports.
- Update Work Plan next action to Slice 11.

## Non-goals

- No training execution implementation.
- No mapping Excel update implementation.
- No train worker/progress implementation.
- No ML algorithm, preprocessing, model artifact, or mapping schema changes.
- No duplicate Predict workspace implementation.
- No push before Slice 11.

## Boundary Decision

Owner boundary: Trainer PySide6 shell/panels and shared visual style adapter.

`TrainShell` continues to reuse `PredictWorkspace` for the Predict tab. The
Train / Model and Data Mapping panels remain QWidget presentation surfaces with
no direct training, worker, Excel, or mapping update execution imports.

change_gate:
  new_source: none
  hotspot_delta: visual-style-only
  code_map_check: skipped
  ui_literal_exemption: trainer-visual-copy-within-existing-surface
  reuse_commonization: reused-existing-trainer-panel-owners
  report_exemption: none
  read_ledger: included

Change gate notes:

- `hotspot_delta`: touched only allowed Trainer UI files, shared style adapter,
  tests, Work Plan, and this report.
- `code_map_check`: skipped because no new module was introduced and prompt
  scope does not include code-map regeneration.
- `reuse_commonization`: preserved `PredictWorkspace` reuse instead of adding a
  duplicate Predict tab implementation.

Read Ledger:

- `docs/designs/assets/train_ref_img.png`: visual inspection, reason: confirm
  current Trainer reference.
- `apps/train/ui/shell.py`: lines 1-75, reason: top status strip and
  `PredictWorkspace` reuse.
- `apps/train/ui/train_model_panel.py`: full file, reason: Train / Model visual
  hierarchy correction.
- `apps/train/ui/data_mapping_panel.py`: full file, reason: Data Mapping
  visual hierarchy correction.
- `apps/common/ui/style.py`: lines 1-232, reason: shared tab/input/table/progress
  style polish.
- `tests/test_apps_train_shell.py`: full file, reason: focused Trainer visual
  foundation tests.
- broad read: none.
- repeated read: generated offscreen screenshots for Train / Model and Data
  Mapping tabs.

## Visual Evidence

- Reference image: `docs/designs/assets/train_ref_img.png`.
- Before screenshot: `/tmp/arc95_slice10_train_shell_current.png`.
- Train / Model after screenshot: `/tmp/arc95_slice10_train_shell_after.png`.
- Data Mapping after screenshot: `/tmp/arc95_slice10_mapping_shell_after.png`.

Observed corrections:

- Top status strip now uses low-emphasis dot/text status rather than colored
  blocks.
- Tabs are flatter and visually grouped with selected-tab emphasis.
- Train / Model now has a command row, left configuration area, progress
  summary, target summary table, log, and info summary.
- Data Mapping now has a disabled command row plus source/status/log areas.
- Disabled actions remain visibly disabled and unwired.

## Verification

- `python3 -B -m py_compile apps/train/**/*.py apps/predict/**/*.py apps/common/**/*.py app_train.py`: passed.
- `python3 -B -m pytest tests/test_apps_train_shell.py`: passed, 4 selected.
- `python3 -B -m pytest tests/test_apps_train_shell.py tests -k "train or predict"`: passed, 98 selected.
- `python3 -B -c "from PySide6.QtWidgets import QApplication; import os; os.environ.setdefault('QT_QPA_PLATFORM','offscreen'); app=QApplication.instance() or QApplication([]); from apps.train.ui.shell import TrainShell; w=TrainShell(); assert w is not None"`: passed.
- `python3 -B tools/check_code_structure.py`: passed with pre-existing
  calculator soft warnings plus code-map freshness reminder; no changed/new
  source file warning.
- `git diff --check`: passed.
- `git status --short`: checked; Slice 10 Trainer/style/test, Work Plan, and
  this report were dirty before commit.

Structure Warnings:

- none from `tools/check_code_structure.py` for changed/new source files.

## Known Risks

- Trainer data/progress/summary values are intentionally visual placeholders
  because execution foundation is out of scope.
- Command buttons are disabled to avoid presenting unwired execution actions as
  available.

## Commit / Push

- Commit: pending.
- Push: not run; Slice 11 only.

## Next

Slice 11 - Arc 9.5 Final Acceptance / Closeout.
