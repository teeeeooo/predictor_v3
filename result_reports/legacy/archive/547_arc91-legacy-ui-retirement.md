# 547 Arc 9.1 Legacy UI Retirement

## Goal

Retire the legacy PyQt `ui/` folder after confirming it is not an active runtime
path, and remove active PyQt dependency references before Arc 9.5 visual parity.

## Deleted Legacy Files

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

## Other Changes

- Converted `scripts/update_mapping.py` from a GUI file picker script to a
  CLI-only mapping conversion utility.
- Updated active architecture/workflow/project docs to describe the legacy
  `ui/` path as retired.
- Updated active UI/UX/design docs and tests to avoid active PyQt dependency
  wording. Archive history was not edited.
- Preserved guard-test intent by constructing retired module names dynamically
  where needed instead of keeping literal active imports.

## Boundary Decision

- Legacy `ui/` code is retired, not copied into PySide6.
- `ui_common.visual_tokens` remains the active toolkit-neutral visual token
  owner.
- PySide6 visual parity implementation remains deferred to Arc 9.5.
- Worker/progress/cancel remains deferred.

## Verification

- `python3 -B -m py_compile apps/predict/**/*.py apps/train/**/*.py apps/calculator/**/*.py core/**/*.py ui_common/*.py app_predict.py app_train.py app_calculator.py scripts/update_mapping.py`
- `python3 -B -c "import app_predict; import app_train; import app_calculator"`
- `rg -n "from ui\.|import ui\.|ui\.base_|ui\.predict_window|ui\.train_window|ui\.spreadsheet_table|ui\.theme" apps core tests scripts docs --glob "!result_reports/archive/**" || true`
- Active-range PyQt literal guard excluding archive history:
  `rg -n "PyQt5" apps core tests scripts docs ui_common --glob "!docs/archive/**" --glob "!result_reports/archive/**" || true`
- `test ! -d ui`
- `python3 -B -m pytest tests/test_visual_tokens.py tests/test_code_structure_guard.py tests/test_apps_predict_schema_adapter.py tests/test_ui_tk_calculator_foundation.py tests/test_ui_tk_table_grid_model.py tests/test_ui_tk_iso16358_helpers.py tests/test_ui_tk_table_grid.py tests/test_ui_tk_profile_resolver.py tests/test_ui_tk_iso_table_autocalc.py`
- `git diff --check`
- `git status --short`

## Validation Notes

- `docs/archive/**` still contains historical PyQt text. This is intentional:
  archive/history content is not active runtime or owner documentation and was
  excluded from the active guard rather than mass-edited.

## Excluded Scope

- No Arc 9.5 visual parity implementation.
- No worker/progress/cancel implementation.
- No Trainer foundation implementation.
- No ML, mapping schema, calculator formula/config/fixture/golden, public
  result, or model artifact changes.

## Next Action

Arc 9.1 Slice 5 - code map, docs closeout, and next action update.
