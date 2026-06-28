# 562 - Arc 9.5 Visual Parity Closeout

## Goal

Close Arc 9.5 after improving PySide6 Predict / Train visual parity from the
stored design assets and Arc 9.2 harvest checklist.

## Visual Parity Changes

- Added shared PySide6 style adapter at `apps/common/ui/style.py`.
- Extended `ui_common.visual_tokens` with minimal Arc 9.5 semantic roles while
  keeping it toolkit-neutral.
- Applied token-backed shell, panel, badge, button, table, and status styling.
- Regenerated `docs/code_map/CODEBASE_REFERENCE_MAP.md` because new source
  files were added.

## Predict Surface Changes

- Added top model/mapping/preprocess/schema status strip.
- Added grouped command bar with Run, Reset, Add Row, Delete Row, Paste,
  Copy Results, and disabled Export placeholder.
- Panelized Input Cases and Prediction Results tables.
- Added bottom summary/status surface with result badge.
- Preserved synchronous prediction execution; no worker/progress/cancel added.

## Predict Table Interaction Status

Implemented:

- TSV copy selected rectangle.
- TSV paste anchored at current/top-left selection.
- CRLF/CR/LF normalization.
- Trailing newline handling.
- Out-of-bounds paste drop.
- Delete/Backspace clear editable cells only.
- Read-only result cells copyable but mutation-protected.
- Dropdown affordance and one-click combo popup foundation.
- `ref_type` / `exp_type` fallback dropdown options.
- Invalid numeric background/tooltip rendering.
- Result status background/tooltip rendering.
- Row headers remain user-facing identity; no visible `case_id` column.

Deferred:

- Grouped undo.
- Tab/Enter navigation override.
- Full click/type replace-on-type state machine.
- Mapping-backed per-row dropdown option updates beyond safe fallback options.
- Detailed result filtering/search/export polish.

## Train Shell Changes

- Added top model/preprocess/training-data/mapping status strip.
- Preserved three-tab shell and Predict tab reuse.
- Replaced Train Model placeholder with visual dataset/model/progress/summary/log
  panels.
- Replaced Data Mapping placeholder with visual mapping path/status/log panels.
- Kept Train and Mapping execution controls disabled as explicit placeholders.

## Design Asset / Harvest Coverage

Covered:

- layout density;
- surface hierarchy;
- command/status grouping;
- input/auto/result visual distinction;
- table header/row sizing foundation;
- dropdown affordance;
- validation/error/result status rendering;
- large-batch split workspace foundation;
- Train admin tab structure;
- Predict workspace reuse.

Observed asset note:

- Asset filenames now match their visual screen type: `predict_ref_img.png`
  shows the Predictor screen and `train_ref_img.png` shows the Trainer /
  Train Model screen.

## Excluded Scope

- No legacy `ui/` restoration.
- No PyQt production dependency.
- No root compatibility wrapper recreation.
- No ML algorithm, feature list, target list, preprocessing formula, model
  artifact, mapping JSON schema, calculator formula/config/fixture/golden, or
  public result contract changes.
- No prediction worker/progress/cancel.
- No trainer execution foundation.
- No model training execution changes.
- No mapping Excel update execution changes.
- No production sample/default/prefill restoration.

## Validation Summary

- `python3 -B -m py_compile apps/predict/**/*.py apps/train/**/*.py core/**/*.py ui_common/*.py app_predict.py app_train.py app_calculator.py`: passed.
- `python3 -B -c "import app_predict; import app_train; import app_calculator; import ui_common.visual_tokens"`: passed.
- `python3 -B -c "from PySide6.QtWidgets import QApplication; import os; os.environ.setdefault('QT_QPA_PLATFORM','offscreen'); app=QApplication.instance() or QApplication([]); from apps.predict.ui.workspace import PredictWorkspace; from apps.train.ui.shell import TrainShell; p=PredictWorkspace(); t=TrainShell(); assert p is not None and t is not None"`: passed.
- `python3 -B -m pytest tests -k "predict or train or visual or table or mapping or schema"`: 439 passed, 825 deselected.
- `python3 -B tools/check_code_structure.py`: passed with 9 pre-existing calculator soft warnings.
- `python3 -B tools/code_checker/build_reference_map.py --check`: stale before regeneration.
- `python3 -B tools/code_checker/build_reference_map.py`: regenerated reference map.
- `python3 -B tools/check_code_structure.py`: passed after regeneration with the same 9 pre-existing calculator soft warnings and no code-map stale warning.
- `rg -n "PyQt5|from ui\\.|import ui\\." apps core tests scripts docs ui_common --glob "!result_reports/archive/**" --glob "!docs/archive/**"`: no matches.
- `git diff --check`: to be run before closeout commit.
- `git status --short`: to be checked before closeout commit.

Offscreen visual checks:

- `/tmp/predict_slice3_fixed.png`
- `/tmp/predict_slice4.png`
- `/tmp/train_slice6.png`
- `/tmp/train_model_slice6_fixed.png`

## Slice Commits

- Slice 1: `1a63e8c` docs(reports): audit arc95 visual parity gaps
- Slice 2: `90a48a7` feat(ui): add pyside6 visual style adapter
- Slice 3: `3b94ef4` feat(ui): improve predict command status surface
- Slice 4: `7eeea57` feat(ui): add predict table clipboard parity
- Slice 5: `ff09a30` feat(ui): surface predict result statuses
- Slice 6: `967ce4a` feat(ui): build train visual admin panels

## Active Report Count

- Before this closeout report: 7 active reports.
- After this closeout report: 8 active reports expected.

## Next

Arc 10 - Prediction Worker / Progress.
