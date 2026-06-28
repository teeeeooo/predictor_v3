# 548 Arc 9.1 Legacy UI Retirement Closeout

## Goal

Close Arc 9.1 after retiring legacy `ui/`, adopting `ui_common.visual_tokens`,
and preparing Arc 9.5 visual parity work.

## Deleted Legacy UI Files

- `ui/.DS_Store`
- `ui/base_model.py`
- `ui/base_view.py`
- `ui/predict_window.py`
- `ui/spreadsheet_table.py`
- `ui/theme.py`
- `ui/train_window.py`

## Removed Legacy Tests

- `tests/test_spreadsheet_table_model.py`
- `tests/test_spreadsheet_table_view.py`
- `tests/test_ui_theme_tokens.py`
- `tests/helpers/pyqt_env.py`
- `tests/test_pyqt_environment_guard.py`

## Harvested UX Ideas

- Legacy dropdown affordance and one-click popup ideas are preserved in
  `docs/ui_ux/06_PYSIDE6_VISUAL_AND_TABLE_PARITY_HARVEST.md`.
- Legacy spreadsheet copy/paste/clear/undo/validation ideas are preserved as
  Arc 9.5/table parity acceptance hints.
- Legacy theme ideas were folded into `ui_common.visual_tokens`.

## ui_common Visual Token Adoption

- `ui_common.visual_tokens` is the active toolkit-neutral token owner for
  Arc 9.5.
- The module remains toolkit-free and imports no GUI toolkit.
- Concrete PySide6 styling remains deferred to Arc 9.5.

## Docs / Code Map Closeout

- `docs/WORK_PLAN.md` next action now points to Arc 9.5.
- `project_brief.md` records Arc 9.1 complete and Arc 9.5 ready.
- `docs/architecture/pyside6_train_predict_architecture.md` records the
  retired legacy path and `ui_common.visual_tokens` ownership.
- `ACTIVE_DOCUMENTS.md` includes the PySide6 visual/table parity harvest doc.
- `docs/code_map/CODEBASE_REFERENCE_MAP.md` was regenerated.

## PyQt Remaining Import Status

- Active source/docs/tests/scripts have no `PyQt5` literal after excluding
  `docs/archive/**` and `result_reports/archive/**`.
- Active source/docs/tests/scripts have no retired `ui.*` import/reference
  patterns from the validation search.
- `docs/archive/**` still contains historical PyQt text and was intentionally
  not mass-edited.

## Validation Summary

- `python3 -B -m py_compile apps/predict/**/*.py apps/train/**/*.py apps/calculator/**/*.py core/**/*.py ui_common/*.py scripts/*.py app_predict.py app_train.py app_calculator.py`
- `python3 -B -c "import app_predict; import app_train; import app_calculator; import ui_common.visual_tokens"`
- `python3 -B -m pytest tests/test_visual_tokens.py`
- `python3 -B tools/check_code_structure.py`
  - passed with existing soft warnings only.
- `python3 -B tools/code_checker/build_reference_map.py --check`
  - fresh, with dirty-working-tree caveat before closeout commit.
- Active `ui.*` and PyQt literal guards passed.
- `test ! -d ui`
- `git diff --check`
- `git status --short`

## Excluded Scope

- No Arc 9.5 visual implementation.
- No worker/progress/cancel implementation.
- No Trainer foundation implementation.
- No ML, mapping schema, calculator formula/config/fixture/golden, public
  result, or model artifact changes.
- No archive/history mass edit.

## Active Report Count

Checked before closeout commit; active reports are above the ideal low-water
mark after this multi-slice arc and should be considered for a later lifecycle
cleanup.

## Next Action

Arc 9.5 - Predict / Train Visual UI Parity from Design Assets.
