# 558 - Arc 9.5 Predict Command and Status Surface

## Goal

Improve the Predict workspace top/bottom structure so the screen starts
matching the design asset hierarchy: status strip, grouped command bar,
panelized input/result tables, and bottom summary/status surface.

## Changes

- Added `apps/predict/ui/status_widgets.py`:
  - `StatusBadge`
  - `StatusStrip`
- Added `apps/predict/ui/command_bar.py`:
  - grouped Predict commands;
  - disabled placeholders for paste, result copy, and CSV export.
- Updated `apps/predict/ui/shell.py` to apply the shared PySide6 stylesheet.
- Updated `apps/predict/ui/workspace.py`:
  - top model/mapping/preprocess/schema badges;
  - grouped command bar;
  - panelized Input Cases and Prediction Results surfaces;
  - bottom summary/status bar;
  - row height baseline for denser table scanning;
  - controlled model/mapping missing status from existing file paths.
- Added `font.caption` token because the Predict bottom/status surface needs a
  smaller semantic text role.
- Narrowed `panel_stylesheet()` to `QFrame#Panel, QWidget#Panel` so panel
  styling does not leak into child buttons.

## Boundary Decision

The command bar owns only UI command widgets. Existing workspace methods remain
the command handlers and call existing controllers/session boundaries. The
table models still do not own command actions, mapping repository calls, or ML
prediction service calls.

Worker/progress/cancel remains deferred. Prediction execution still uses the
current synchronous controller path.

## Visual Check

Rendered the updated Predict shell offscreen to `/tmp/predict_slice3_fixed.png`.
The screen now shows a visible status strip, grouped command area, two panelized
tables, and a bottom summary/status row. It is closer to the design reference
but not final table parity.

Known remaining visual/table gaps:

- Dropdown affordance and one-click popup are still missing.
- TSV copy/paste/clear/undo/navigation are still Slice 4 work.
- Validation rendering and row-level warning/error surface are still Slice 4/5
  work.

## Excluded Scope

- No worker/progress/cancel implementation.
- No Trainer shell changes in this slice.
- No ML behavior, mapping schema, model artifact, calculator logic, fixtures,
  golden values, or public result contract changes.
- No production sample/default/prefill restoration.

## Verification

- `python3 -B -m py_compile apps/predict/**/*.py app_predict.py apps/common/**/*.py`: passed.
- `python3 -B -c "import app_predict"`: passed.
- `python3 -B -c "from PySide6.QtWidgets import QApplication; import os; os.environ.setdefault('QT_QPA_PLATFORM','offscreen'); app=QApplication.instance() or QApplication([]); from apps.predict.ui.workspace import PredictWorkspace; w=PredictWorkspace(); assert w is not None"`: passed.
- `git diff --check`: passed.
- `git status --short`: checked before closeout.

Note: offscreen smoke still emits the existing Qt font alias warning for the
environment; it does not block widget construction.

## Next

Slice 4 - Predict table visual parity and spreadsheet interaction slice.
