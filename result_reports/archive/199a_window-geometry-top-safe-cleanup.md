# 199-a Window Geometry Top-safe Cleanup

## Goal

- Close out the 198-d Windows manual smoke.
- Keep the 80% auto-fit height cap.
- Make large detail/profile auto-fit surfaces use a top-safe y policy while preserving x/current monitor location.
- Clarify duplicated geometry calculations without changing public helper contracts.

## Scope

- `ui_tk/window_geometry.py`
  - Added private helpers for y margin, max auto-fit height, and visible bottom.
  - Reused the max-height helper in `capped_window_size()`, `apply_overflow_correction()`, and `grow_window_by_vertical_delta()`.
  - Updated `clamp_geometry_vertically_to_visible_bounds()` so large surfaces use top-safe y positioning.
  - Kept public helper names and call contracts unchanged.
- `tests/test_ui_tk_calculator_foundation.py`
  - Updated vertical clamp coverage for small, bottom-overflow, large top-safe, monitor2-like x, and over-visible-height cases.
- `docs/WORK_PLAN.md`
  - Moves next action to 199-a manual smoke.
- `result_reports/active/198d_detail-open-vertical-clamp-bottom-margin-hotfix.md`
  - Records user-provided Windows manual check result.

## Non-goals

- No `APP_WINDOW_MAX_HEIGHT_RATIO` change.
- No x clamp, primary recenter, `root.maxsize()`, continuous `<Configure>` observer, tab call-site change, detail panel/graph/table/export/input logic, core/config/golden/PyQt, project log, memory seed, summaries, archive, or Hong Kong HSPF trace changes.

## Manual Check Result

- User completed Windows local GUI smoke for 198-d.
- The 80% height cap and bottom-margin vertical clamp behaved as intended.
- Monitor/current x preservation remained intact.
- Windows behavior indicates large detail surfaces are more stable with top-safe y positioning than bottom-only correction.

## Change

- Small windows preserve current y unless they would overflow bottom or start above the screen.
- Large detail-like windows, currently height >= 75% of screen height, use top-safe y near `APP_WINDOW_SCREEN_MARGIN_Y_RATIO`.
- Windows taller than visible area fall back to y = 0.
- x, width, and height are preserved in vertical-only clamp.
- Initial-launch full clamp remains separate and may still adjust both x and y.

## Verification

- Process check: no leftover pytest/python process beyond the check command itself.
- `python3 -B tools/check_code_structure.py`
  - Passed with existing soft-limit warning: `ui_tk/sections/bin_detail_panel.py` exceeds 400 LOC.
- `python3 -B -m py_compile ui_tk/window_geometry.py tests/test_ui_tk_calculator_foundation.py`
  - Passed.
- Quick smoke with `-q`
  - `tests/test_ui_tk_calculator_foundation.py::test_vertical_clamp_preserves_x_and_adjusts_y_only`
  - `tests/test_ui_tk_calculator_foundation.py::test_capped_window_size_matches_initial_geometry_policy`
  - `tests/test_ui_tk_calculator_foundation.py::test_preferred_content_fit_geometry_preserves_current_location`
  - Result: 3 passed.
- Final focused with `-q`
  - `tests/test_ui_tk_calculator_foundation.py tests/test_ui_tk_iso_table_autocalc.py tests/test_ui_tk_profile_resolver.py`
  - Result: 36 passed, 47 skipped because Tk display is unavailable in Codespaces.
- `git diff --check`
  - Passed.

## Manual Check Result

- User completed Windows local GUI smoke for 199-a.
- First launch size was normal.
- Detail open no longer clipped at the lower edge.
- Monitor 2 detail open/close preserved location.
- Profile changes preserved location.
- Manual window resizing remained available.
- ISO/SASO/Hong Kong detail, CSV/copy, and graph behavior remained intact.

## Project Memory Delta

- none
