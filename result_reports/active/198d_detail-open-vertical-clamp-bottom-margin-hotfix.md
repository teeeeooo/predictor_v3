# 198-d Detail-open Vertical Clamp Bottom-margin Hotfix

## Goal

- Close out the 198-c Windows manual smoke.
- Keep the 80% auto-fit height cap.
- Make detail/profile vertical clamp account for bottom safety margin while preserving x/current monitor location.

## Scope

- `ui_tk/window_geometry.py`
  - Updated `clamp_geometry_vertically_to_visible_bounds()` only.
  - Reused `APP_WINDOW_SCREEN_MARGIN_Y_RATIO` to compute a safer visible bottom.
- `tests/test_ui_tk_calculator_foundation.py`
  - Updated vertical clamp expectations for bottom safety margin.
- `docs/WORK_PLAN.md`
  - Moves next action to 198-d manual smoke.
- `result_reports/active/198c_auto-fit-height-cap-packaging-closeout.md`
  - Records user-provided Windows manual check result.

## Non-goals

- No new geometry helper/public function.
- No `APP_WINDOW_MAX_HEIGHT_RATIO` rollback, `root.maxsize()`, x clamp, primary recenter, continuous `<Configure>` observer, tab call-site change, detail panel/graph/table/export/input logic, core/config/golden/PyQt, router, project log, memory seed, summaries, or archive changes.

## Cause

- 198-b vertical clamp used `screen_height - height` as the maximum y.
- That did not reserve bottom space for taskbar/titlebar/scaling/work-area differences.
- With the 198-c 80% height cap, `screen_height - height` can be larger, so the window may not move upward enough.

## Change

- Vertical clamp now computes:
  - `margin_y = int(screen_height * APP_WINDOW_SCREEN_MARGIN_Y_RATIO)`
  - `visible_bottom = screen_height - margin_y`
  - `max_y = max(0, visible_bottom - height)`
- Width, height, and x are preserved.
- y alone is clamped to `[0, max_y]`.
- If height is larger than the visible area, y becomes `0`.

## Verification

- Process check: no leftover pytest/python process beyond the check command itself.
- `python3 -B tools/check_code_structure.py`
  - Passed with existing soft-limit warning: `ui_tk/sections/bin_detail_panel.py` exceeds 400 LOC.
- `python3 -B -m py_compile ui_tk/window_geometry.py tests/test_ui_tk_calculator_foundation.py`
  - Passed.
- Quick smoke with `-q`
  - `tests/test_ui_tk_calculator_foundation.py::test_vertical_clamp_preserves_x_and_adjusts_y_only`
  - `tests/test_ui_tk_calculator_foundation.py::test_capped_window_size_matches_initial_geometry_policy`
  - Result: 2 passed.
- Final focused with `-q`
  - `tests/test_ui_tk_calculator_foundation.py tests/test_ui_tk_iso_table_autocalc.py tests/test_ui_tk_profile_resolver.py`
  - Result: 36 passed, 47 skipped because Tk display is unavailable in Codespaces.
- `git diff --check`
  - Passed.

## Manual Check Needed

- Codespaces cannot perform Windows GUI smoke.
- User should verify:
  - detail open no longer clips the lower edge;
  - y moves upward enough to leave bottom safety margin;
  - x/current monitor location remains preserved, including monitor 2;
  - 80% auto-fit height cap remains acceptable;
  - ISO/ISEER, SASO, Hong Kong CSPF detail open/close and export/copy/graph behavior remain unchanged.

## Project Memory Delta

- none
