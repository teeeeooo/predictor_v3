# 198-b Detail-open Vertical Clamp Hotfix

## Goal

- Close out the 198-a Windows manual smoke.
- Prevent detail/profile fit from growing the window downward past the visible bottom edge.
- Preserve current monitor/current x policy from 197-b.

## Scope

- `ui_tk/window_geometry.py`
  - Added `clamp_geometry_vertically_to_visible_bounds()` pure helper.
  - Added `clamp_window_vertically_to_visible_bounds()` Tk wrapper.
  - Kept existing full `clamp_window_to_visible_bounds()` for initial launch only.
- `ui_tk/tabs/iso16358_tab.py`
  - Applies vertical-only clamp after `fit_window_to_preferred_content()` and `grow_window_by_vertical_delta()`.
- `tests/test_ui_tk_calculator_foundation.py`
  - Added pure vertical clamp coverage and fit-path call coverage.
- `docs/WORK_PLAN.md`
  - Moves next action to 198-b manual smoke.
- `result_reports/active/198a_tkinter-launch-fit-saso-default-router-output-budget.md`
  - Records user-provided Windows manual check result.

## Non-goals

- No AGENT_TASK_ROUTER changes.
- No core/profile/config/golden/fixture, PyQt, detail panel semantics, graph, CSV/export/copy, MetricInputTable, ExcelLikeTableController, ResultPanel, SASO calculation/default policy, Hong Kong HSPF, or HSPF trace changes.
- No full visible clamp in profile/detail fit and no primary-monitor recenter.

## Cause

- Detail open/profile fit preserved current x/y and resized height.
- When height increased while y stayed fixed, the bottom edge could move below the visible screen.
- The existing full visible clamp is not suitable for profile/detail fit because it also clamps x, which could break monitor 2 or negative-x placement.

## Change

- Vertical-only clamp preserves width, height, and x.
- It only adjusts y:
  - bottom overflow pulls y upward;
  - negative y is raised to 0;
  - height larger than screen height uses y = 0.
- `Iso16358Tab._fit_toplevel_to_current_content()` now runs vertical-only clamp after content fit and overflow growth, then resets scroll position.

## Verification

- Process check: no leftover pytest/python process beyond the check command itself.
- `python3 -B tools/check_code_structure.py`
  - Passed with existing soft-limit warning: `ui_tk/sections/bin_detail_panel.py` exceeds 400 LOC.
- `python3 -B -m py_compile ui_tk/window_geometry.py ui_tk/tabs/iso16358_tab.py tests/test_ui_tk_calculator_foundation.py tests/test_ui_tk_iso_table_autocalc.py`
  - Passed.
- Quick smoke with `-q`
  - Result: 2 passed, 1 skipped because Tk display is unavailable in Codespaces.
- Final focused with `-q`
  - `tests/test_ui_tk_calculator_foundation.py tests/test_ui_tk_iso_table_autocalc.py tests/test_ui_tk_profile_resolver.py`
  - Result: 36 passed, 47 skipped because Tk display is unavailable in Codespaces.
- `git diff --check`
  - Passed.

## Manual Check Needed

- Codespaces cannot perform Windows GUI smoke.
- User should verify:
  - detail open no longer clips the lower edge;
  - any correction moves only vertically as needed;
  - monitor 2 detail open/close still stays on monitor 2;
  - profile changes preserve current monitor/location;
  - ISO/ISEER, SASO, and Hong Kong CSPF detail open/close still work;
  - result/detail table, graph, CSV/export/copy, and SASO 4-point default behavior remain unchanged.

## Project Memory Delta

- none
