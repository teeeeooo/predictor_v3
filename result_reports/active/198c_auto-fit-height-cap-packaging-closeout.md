# 198-c Auto-fit Height Cap and Packaging Closeout

## Goal

- Close out the 198-b Windows manual smoke.
- Reduce detail-open lower clipping by lowering automatic fit height cap.
- Record Windows `calculator_tk` packaging size closeout.

## Scope

- `ui_tk/layout_constants.py`
  - Lowered `APP_WINDOW_MAX_HEIGHT_RATIO` from `0.92` to `0.80`.
- `tests/test_ui_tk_calculator_foundation.py`
  - Added explicit assertion that the capped geometry policy follows the 80% height cap.
- `result_reports/active/198b_detail-open-vertical-clamp-hotfix.md`
  - Converted Manual Check Needed to Manual Check Result.
- `docs/WORK_PLAN.md`
  - Moved next action to 198-c manual smoke and closed Windows packaging-size pending state.
- Packaging docs/guides
  - Recorded Windows `calculator_tk` packaged size as approximately 11 MB and acceptable for the current deployment candidate.

## Non-goals

- No `root.maxsize()` and no user manual resize restriction.
- No x clamp, primary monitor recenter, continuous `<Configure>` observer, detail panel/graph/table/export/input logic, core/config/golden/PyQt, project log, memory seed, summaries, or archive changes.

## Manual Check Result

- User completed Windows local GUI smoke for 198-b.
- Vertical clamp behaved as intended and preserved monitor/location behavior.
- Remaining issue was excessive auto-fit height for long detail content, split to this 198-c cap change.

## Change

- Automatic window fit now caps requested height to approximately 80% of screen height through the existing shared cap policy.
- This affects programmatic initial/profile/detail auto-fit only.
- It does not set `root.maxsize()`, so users can still manually resize the window larger.
- Content beyond the auto-fit cap remains reachable through the existing scrollable container.

## Packaging Closeout

- Windows `calculator_tk` packaged size was measured at approximately 11 MB.
- This is acceptable for the current deployment candidate.
- PyQt baseline comparison remains a later retirement-gate input if source retirement resumes.

## Verification

- Process check: no leftover pytest/python process beyond the check command itself.
- `python3 -B tools/check_code_structure.py`
  - Passed with existing soft-limit warning: `ui_tk/sections/bin_detail_panel.py` exceeds 400 LOC.
- `python3 -B -m py_compile ui_tk/layout_constants.py ui_tk/window_geometry.py tests/test_ui_tk_calculator_foundation.py`
  - Passed.
- Quick smoke with `-q`
  - `tests/test_ui_tk_calculator_foundation.py::test_capped_window_size_matches_initial_geometry_policy`
  - `tests/test_ui_tk_calculator_foundation.py::test_vertical_clamp_preserves_x_and_adjusts_y_only`
  - Result: 2 passed.
- Final focused with `-q`
  - `tests/test_ui_tk_calculator_foundation.py tests/test_ui_tk_iso_table_autocalc.py tests/test_ui_tk_profile_resolver.py`
  - Result: 36 passed, 47 skipped because Tk display is unavailable in Codespaces.
- `git diff --check`
  - Passed.

## Manual Check Result

- User completed Windows local GUI smoke for 198-c.
- Auto-fit max height 80% cap was acceptable and remains in place.
- Windows `calculator_tk` packaged size remains approximately 11 MB and acceptable.
- Remaining issue: detail open can still clip at the bottom because vertical clamp lacks a bottom safety margin; owner is 198-d.

## Project Memory Delta

- none
