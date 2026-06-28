# 544 Arc 9.1 Legacy UI Inventory

## Goal

Audit legacy PyQt `ui/` and toolkit-neutral `ui_common/` usage before visual
parity work and legacy retirement.

## Active Caller Audit

Commands checked:

- `rg -n "from ui\.|import ui\.|ui\.base_|ui\.predict_window|ui\.train_window|ui\.spreadsheet_table|ui\.theme" apps core tests scripts docs --glob "!result_reports/archive/**"`
- `rg -n "ui_common|visual_tokens" apps core tests scripts docs --glob "!result_reports/archive/**"`
- `rg -n "PyQt5" apps core ui ui_common tests scripts docs --glob "!result_reports/archive/**"`

## Classification

- Active runtime caller of `ui/`: none found under `apps/`, `core/`, or
  entrypoint paths.
- Active tests referencing `ui/`:
  - `tests/test_spreadsheet_table_model.py`
  - `tests/test_spreadsheet_table_view.py`
  - `tests/test_ui_theme_tokens.py`
- Current docs references:
  - `docs/architecture/project_architecture.md`
  - `docs/architecture/pyside6_train_predict_architecture.md`
  - `docs/WORK_PLAN.md`
  - `project_brief.md`
  - `docs/designs/README.md`
  - selected historical design/guides still mentioning PyQt history or adapters.
- Archive/history references: present under `docs/archive/**` and excluded from
  active ownership decisions.
- Remaining active `PyQt5` source import outside `ui/`:
  - `scripts/update_mapping.py` uses `QApplication` and `QFileDialog` as a thin
    file-selection script. This is not a runtime Train/Predict caller, but it is
    a PyQt5 dependency and must be removed or converted before final Arc 9.1
    closeout if the active PyQt5 import guard is to pass.

## Delete / Keep / Harvest Decision

- Delete target:
  - legacy `ui/` folder and its PyQt Train/Predict files;
  - legacy tests that exercise `ui.spreadsheet_table` and `ui.theme`.
- Keep target:
  - `ui_common/visual_tokens.py` and `ui_common/__init__.py`.
- Harvest target:
  - `ui/base_view.py`: dropdown delegate, non-editing arrow rendering,
    one-click popup behavior.
  - `ui/spreadsheet_table.py`: TSV copy/paste, clear, undo, numeric validation,
    and helper-level table interaction ideas.
  - `ui/theme.py`: semantic color/font/spacing token ideas, to be consolidated
    under `ui_common.visual_tokens`.
  - `ui/predict_window.py` and `ui/train_window.py`: feature inventory only;
    code structure must not be copied into PySide6.

## Boundary Decision

- Legacy `ui/` is not a current runtime path.
- `ui_common.visual_tokens` is the active toolkit-neutral visual token
  foundation for Arc 9.5.
- Legacy PyQt code must not be copied into PySide6 implementation.
- `scripts/update_mapping.py` PyQt5 usage is a non-runtime script dependency
  and is a closeout cleanup candidate.

## Verification

- `git diff --check`: pending for slice closeout.
- `git status --short`: pending for slice closeout.

## Next Action

Arc 9.1 Slice 2 - harvest legacy UX ideas into current UI/UX docs.
