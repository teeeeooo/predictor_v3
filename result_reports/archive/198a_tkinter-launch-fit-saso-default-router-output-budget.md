# 198-a Tkinter Launch Fit, SASO Default, Router Output Budget

## Goal

- Close out 197-b Windows manual smoke.
- Reduce first-launch ISO profile height oversizing with a one-shot post-launch fit.
- Make SASO T3 use 4-point as the default while still showing required-only 3-point comparison.
- Add a small verification output/token budget guard to `AGENT_TASK_ROUTER.md`.

## Scope

- `ui_tk/calculator_app.py`
  - Schedules a one-shot idle content fit after initial center, overflow correction, and visible-bounds clamp.
- `ui_tk/tabs/iso16358_tab.py`
  - Adds a public one-shot wrapper around the existing current-content fit path.
- `ui_tk/sections/iso_saso_t3_section.py`
  - Keeps 35 Min enabled by default and hides the old optional-test checkbox text/UI.
  - Shows 4-point row first and 3-point required-only row second.
  - Uses 4-point as the detail default source while keeping 3-point selectable.
  - Keeps 3-point output available when 35 Min is invalid and marks 4-point as safe status.
- `tests/test_ui_tk_calculator_foundation.py`
  - Adds one-shot launch fit scheduling coverage.
- `tests/test_ui_tk_iso_table_autocalc.py`
  - Updates SASO default/result/detail/export expectations.
- `AGENT_TASK_ROUTER.md`
  - Adds focused verification output budget guidance.
- `docs/WORK_PLAN.md`
  - Moves next action to 198-a manual smoke.
- `result_reports/active/197b_multi-monitor-geometry-role-split-hotfix.md`
  - Records user-provided Windows manual check result.

## Non-goals

- No core/profile/config/golden/fixture changes.
- No PyQt, graph, CSV/export/copy, MetricInputTable, ExcelLikeTableController, ResultPanel, Hong Kong HSPF, or HSPF trace changes.
- No continuous `<Configure>` observer and no magic pixel size hardcoding.

## Cause / Change

- First launch used initial center/overflow/clamp, but did not rerun the existing stable profile/content fit after Tk idle layout settled.
- The fix schedules `Iso16358Tab.fit_toplevel_to_current_content_once()` through `root.after_idle()` once after launch geometry setup.
- This reuses the existing current-location-preserving fit policy and avoids a continuous geometry loop.

## SASO T3 Default

- SASO now treats 35 Min as enabled by default.
- The old optional-test checkbox is not exposed to users.
- Result order is `With 35 Min (4-point)` followed by `Required only (3-point)`.
- Detail default source is `With 35 Min (4-point)`; `Required only (3-point)` remains selectable.
- Invalid 35 Min input produces a safe 4-point status row while preserving the 3-point required-only result/detail.

## Router Output Guard

- Added guidance to avoid repeated `-rxXs` output in known headless Tk skip situations.
- Default focused verification should use `-q`; `-rxXs` is fallback for failures or unexpected skip/xfail/xpass investigation.
- Reports should be written after verification, with post-report checks limited to diff/status style checks.

## Verification

- Process check: no leftover pytest/python process beyond the check command itself.
- `python3 -B tools/check_code_structure.py`
  - Passed with existing soft-limit warning: `ui_tk/sections/bin_detail_panel.py` exceeds 400 LOC.
- `python3 -B -m py_compile ui_tk/calculator_app.py ui_tk/tabs/iso16358_tab.py ui_tk/sections/iso_saso_t3_section.py tests/test_ui_tk_calculator_foundation.py tests/test_ui_tk_iso_table_autocalc.py`
  - Passed.
- Quick smoke with `-q`
  - Result: 1 passed, 3 skipped because Tk display is unavailable in Codespaces.
- Final focused with `-q`
  - `tests/test_ui_tk_calculator_foundation.py tests/test_ui_tk_iso_table_autocalc.py tests/test_ui_tk_profile_resolver.py`
  - Result: 35 passed, 46 skipped because Tk display is unavailable in Codespaces.
- `git diff --check`
  - Passed.

## Manual Check Result

- User completed Windows local GUI smoke for 198-a.
- 197-b multi-monitor geometry behavior remained fixed: monitor 2 detail open/close and profile changes preserved location.
- First-launch ISO one-shot fit was confirmed: initial height was not excessive and lower edge was visible.
- SASO T3 4-point default was confirmed: result table showed 4-point and 3-point rows, and detail source selection exposed both.
- Router verification output guard was accepted.
- New follow-up: opening detail can grow the window downward enough to clip the lower edge; owner is 198-b vertical-only clamp.

## Project Memory Delta

- none
