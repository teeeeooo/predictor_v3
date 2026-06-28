# 561 - Arc 9.5 Train Shell Visual Parity

## Goal

Replace the Train app placeholder panels with design-asset-aligned visual
admin surfaces while preserving Predict workspace reuse and excluding Trainer
execution.

## Changes

- Updated `apps/train/ui/shell.py`:
  - applies shared PySide6 stylesheet;
  - adds top model/preprocess/training-data/mapping status strip;
  - preserves three-tab shell;
  - keeps Predict tab as `PredictWorkspace`.
- Replaced `apps/train/ui/train_model_panel.py` placeholder with a visual
  Train / Model admin surface:
  - dataset path field;
  - model path field;
  - disabled train/stop action placeholders;
  - progress/status cards;
  - training summary statuses;
  - read-only training log area.
- Replaced `apps/train/ui/data_mapping_panel.py` placeholder with a visual Data
  Mapping admin surface:
  - mapping path field;
  - disabled update/reload action placeholders;
  - mapping status;
  - read-only mapping log area.
- Updated shared style so disabled primary buttons look disabled.
- Added `tests/test_apps_train_shell.py`.

## Boundary Decision

This slice is visual/admin surface foundation only. It does not call training
execution, mapping Excel update execution, or worker/progress/cancel code.
Predict tab reuse remains through `PredictWorkspace`.

## Visual Check

Rendered Train shell offscreen:

- `/tmp/train_slice6.png`: default Predict tab reuse.
- `/tmp/train_model_slice6_fixed.png`: Train / Model visual panel.

The Train / Model tab now follows the reference hierarchy with left
configuration, center progress/log, and right summary areas. The design asset is
used for hierarchy and density, not pixel-perfect reproduction.

## Excluded Scope

- No Trainer execution foundation.
- No model training execution changes.
- No mapping Excel update execution changes.
- No worker/progress/cancel.
- No ML algorithm, feature list, preprocessing formula, model artifact, mapping
  JSON schema, calculator formula/config/fixture/golden, or public result
  contract changes.

## Verification

- `python3 -B -m py_compile apps/train/**/*.py apps/predict/**/*.py apps/common/**/*.py app_train.py`: passed.
- `python3 -B -c "import app_train"`: passed.
- `python3 -B -c "from PySide6.QtWidgets import QApplication; import os; os.environ.setdefault('QT_QPA_PLATFORM','offscreen'); app=QApplication.instance() or QApplication([]); from apps.train.ui.shell import TrainShell; w=TrainShell(); assert w is not None"`: passed.
- `python3 -B -m pytest tests/test_apps_train_shell.py tests/test_pyside6_style_adapter.py`: 7 passed.
- `python3 -B -m pytest tests -k "train or predict"`: 63 passed, 1201 deselected.
- `rg -n "PyQt5|from ui\\.|import ui\\." apps core tests scripts docs ui_common --glob "!result_reports/archive/**" --glob "!docs/archive/**"`: no matches.
- `git diff --check`: passed.
- `git status --short`: checked before closeout.

Note: offscreen smoke still emits the existing Qt font alias warning for the
environment; it does not block widget construction.

## Next

Slice 7 - Arc 9.5 integration smoke, docs closeout, and next action.
