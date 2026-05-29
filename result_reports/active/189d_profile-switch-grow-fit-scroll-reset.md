# 189-d Profile Switch Grow-fit / Scroll Reset Hotfix

Date: 2026-05-29

## Goal

Fix the remaining profile-switch geometry issues from manual smoke:

- Hong Kong switch could still leave avoidable overflow/scrollbar.
- Switching back to ISO/ISEER 2-point could shrink the window below the prior size.
- Profile switches should reset the scroll position to top.

## Changed Files

- `ui_tk/window_geometry.py`
- `ui_tk/tabs/iso16358_tab.py`
- `ui_tk/scrollable_frame.py`
- `tests/test_ui_tk_calculator_foundation.py`
- `tests/test_ui_tk_iso_table_autocalc.py`
- `docs/WORK_PLAN.md`
- `result_reports/active/189d_profile-switch-grow-fit-scroll-reset.md`

## Implementation

- Replaced profile-switch exact-fit behavior with grow-only helpers:
  - `grow_window_to_preferred_content()`
  - `grow_window_by_vertical_delta()`
- `Iso16358Tab` now performs one after-idle profile-switch correction:
  1. update idle tasks
  2. grow to preferred content if needed
  3. update idle tasks
  4. grow once more by measured vertical overflow delta if needed
  5. reset scroll position to top
- Added `ScrollableFrame.reset_scroll_position()`.
- Kept the existing no-overflow wheel guard.

## Verification

- `python3 -B -m py_compile ui_tk/scrollable_frame.py ui_tk/tabs/iso16358_tab.py ui_tk/window_geometry.py tests/test_ui_tk_calculator_foundation.py tests/test_ui_tk_iso_table_autocalc.py` -> OK
- `python3 -B tools/check_code_structure.py` -> OK
- quick smoke -> 2 passed
- focused suite -> 45 passed
- `git diff --check` -> OK
- leftover pytest process check -> none after verification

Full pytest was intentionally not run.

## Manual Check Needed

- Confirm Hong Kong switch grows enough to avoid unnecessary clipping/scrollbar within screen cap.
- Confirm switching back to ISO/ISEER 2-point does not shrink the window.
- Confirm profile switch resets viewport to the top.

## Excluded Scope

- No root/toplevel `<Configure>` binding.
- No continuous geometry observer.
- No hardcoded pixel tuning.
- No 2-point section/result table, ResultPanel, resolver, core/config/golden/fixture, PyQt, SASO, multi/batch, detail/trace, graph, EN/AHRI, project log, memory seed, or lifecycle changes.

## Commit / Push

- Source/test commit: `5c560a8 fix: grow iso profile switch window`
- Docs/report commit: pending at report write time
- Push: pending at report write time

## Project Memory Delta

- none
