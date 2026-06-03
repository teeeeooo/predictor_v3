# 197-b Multi-monitor Geometry Role-split Hotfix

## Goal

- Fix the geometry policy that can move the app back to the primary monitor when detail/profile content is fitted.
- Reduce first-launch lower clipping after overflow correction.
- Keep Windows GUI verification as a separate manual check.

## Scope

- `ui_tk/window_geometry.py`
  - Added robust geometry parsing/formatting for positive and negative x/y coordinates.
  - Split shared size cap policy from initial center placement.
  - Kept `initial_window_geometry()` as initial-launch centered placement.
  - Changed profile/detail fit geometry to preserve current x/y and resize only.
  - Added initial-only visible-bounds clamp after overflow correction.
- `ui_tk/calculator_app.py`
  - Calls initial visible-bounds clamp after one-shot overflow correction.
- `tests/test_ui_tk_calculator_foundation.py`
  - Added/updated focused geometry helper tests.
- `docs/WORK_PLAN.md`
  - Moved next action to 197-b manual smoke.

## Non-goals

- No detail panel layout or semantics changes.
- No graph, CSV/export/copy, MetricInputTable, ExcelLikeTableController, ResultPanel, core/profile/config/golden/fixture, PyQt, or Hong Kong HSPF changes.
- No continuous `<Configure>` observer and no external monitor dependency.

## Cause

- `initial_window_geometry()` intentionally combines size cap policy with centered initial placement.
- `fit_window_to_preferred_content()` reused `initial_window_geometry()` for profile/detail content changes.
- That reuse also reapplied centering, so detail/profile fit could move a window from monitor 2 back toward the primary monitor center.
- Initial launch could also grow height after centering through one-shot overflow correction, leaving the lower edge clipped.

## Change

- Added `capped_window_size()` as the shared size cap/min/max policy owner.
- Added `preferred_content_fit_geometry()` so profile/detail fit uses capped preferred size while preserving current x/y.
- Added `parse_window_geometry()` and `format_window_geometry()` to support negative and multi-monitor-like coordinates.
- Added `clamp_window_to_visible_bounds()` for initial launch only, called after `apply_overflow_correction()`.
- Kept `initial_window_geometry()` available for initial centered placement.

## Verification

- Process check before verification: no leftover pytest/python process beyond the check command itself.
- `python3 -B tools/check_code_structure.py`
  - Passed with existing soft-limit warning: `ui_tk/sections/bin_detail_panel.py` exceeds 400 LOC.
- `python3 -B -m py_compile ui_tk/window_geometry.py ui_tk/calculator_app.py tests/test_ui_tk_calculator_foundation.py tests/test_ui_tk_iso_table_autocalc.py`
  - Passed.
- Quick smoke:
  - Geometry helper tests plus full app smoke.
  - Result: 2 passed, 1 skipped because Tk display is unavailable in Codespaces.
- Final focused:
  - `tests/test_ui_tk_calculator_foundation.py`, `tests/test_ui_tk_iso_table_autocalc.py`, `tests/test_ui_tk_profile_resolver.py`
  - Result: 35 passed, 45 skipped because Tk display is unavailable in Codespaces.
- `git diff --check`
  - Passed.

## Manual Check Needed

- Codespaces cannot perform Windows multi-monitor GUI smoke.
- User should verify:
  - First launch stays within visible bounds and lower edge is not clipped.
  - Moving the app to monitor 2 and opening/closing detail keeps the app on monitor 2.
  - Profile changes preserve current monitor/location.
  - ISO/ISEER, SASO T3, and Hong Kong CSPF detail open/close still work.
  - Result/detail table, graph, CSV/export/copy behavior is unchanged.

## Project Memory Delta

- none
