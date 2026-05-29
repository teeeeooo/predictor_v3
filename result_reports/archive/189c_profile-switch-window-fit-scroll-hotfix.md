# 189-c Profile Switch Window Fit / No-overflow Scroll Hotfix

Date: 2026-05-29

## Goal

Fix two manual-smoke issues after the 189-b ISO/ISEER 2-point result refinement:

- no-overflow ISO/ISEER 2-point view could still wheel/trackpad-scroll into blank space;
- switching from default ISO/ISEER 2-point to Hong Kong could leave the taller Hong Kong content clipped.

## Scope

Changed:

- `ui_tk/scrollable_frame.py`
- `ui_tk/tabs/iso16358_tab.py`
- `ui_tk/window_geometry.py`
- `tests/test_ui_tk_calculator_foundation.py`
- `tests/test_ui_tk_iso_table_autocalc.py`
- `docs/WORK_PLAN.md`
- `result_reports/active/189c_profile-switch-window-fit-scroll-hotfix.md`

## Non-goals

- No changes to 2-point calculation/result table logic.
- No changes to `ResultPanel`, profile resolver, core calculator, profiles/configs, fixtures/goldens, PyQt source, SASO, multi/batch, detail/trace, graph, EN/AHRI, `project_log.md`, memory seed, summary, or archive.

## Implementation

### No-overflow Wheel Guard

`ScrollableFrame._on_mousewheel()` now:

- still ignores events outside the scrollable frame with `""`;
- returns `"break"` for internal wheel events when `vertical_overflow_delta() <= 0`;
- calls `canvas.yview_scroll(units, "units")` only when there is real vertical overflow.

No `bind_all` / `unbind_all` was introduced.

### Profile Switch Window Fit

- Added `fit_window_to_preferred_content(root, preferred_content_size)` in `ui_tk/window_geometry.py`.
- `Iso16358Tab._on_mode_changed()` schedules one after-idle call to fit the toplevel to the current profile content.
- The helper reuses existing `initial_window_geometry()` screen-cap policy.
- No root/toplevel `<Configure>` binding, continuous observer, or resize loop was added.

## Tests

Added/updated focused tests for:

- no-overflow internal wheel events consuming the event without scrolling;
- overflow internal wheel events still scrolling;
- outside widget wheel events staying ignored;
- profile switch to Hong Kong fitting current content without overflow;
- switch back to ISO/ISEER 2-point keeping the comparison table normal;
- one-shot preferred-content geometry helper;
- existing full app subprocess smoke and resize-hang regression.

## Verification

Commands run:

- `ps -axo pid,args | rg 'pytest|python3 -B -m pytest|Python -B'` -> no leftover pytest process after verification
- `python3 -B tools/check_code_structure.py` -> OK (`code structure guard: OK (no findings)`)
- `python3 -B -m py_compile ui_tk/scrollable_frame.py ui_tk/tabs/iso16358_tab.py ui_tk/window_geometry.py tests/test_ui_tk_calculator_foundation.py tests/test_ui_tk_iso_table_autocalc.py` -> OK
- `python3 -B -m pytest tests/test_ui_tk_iso_table_autocalc.py::test_iso_iseer_2point_mode_renders_default_summaries tests/test_ui_tk_calculator_foundation.py::test_calculator_tk_app_builds_widget_tree -q -rxXs` -> 2 passed
- `python3 -B -m pytest tests/test_ui_tk_profile_resolver.py tests/test_ui_tk_iso_table_autocalc.py tests/test_ui_tk_calculator_foundation.py -q -rxXs` -> 44 passed
- `git diff --check` -> OK
- `git status --short`, `git diff --name-only`, `git diff --stat` -> reviewed before commits

Full pytest was intentionally not run.

## Manual Check Needed

- Confirm ISO/ISEER 2-point default view no longer scrolls into blank vertical space when content fits.
- Confirm switching ISO/ISEER 2-point -> Hong Kong fits the taller Hong Kong content without clipping.
- Confirm switching Hong Kong -> ISO/ISEER 2-point keeps the comparison table visible and does not leave blank scroll space.

## Excluded Scope

- SASO
- multi/batch
- detail/trace table
- graph
- EN/AHRI
- core/profile/config/golden/fixture
- PyQt source
- lifecycle summary/archive

## Next Suggested Action

Run manual smoke, then choose the next Design First Gate slice.

## Scope Compliance

- No root/toplevel `<Configure>` binding was added.
- No continuous geometry observer was added.
- No `bind_all` / `unbind_all` was introduced.
- `ui_tk/sections/iso_iseer_2point_section.py` and `ui_tk/sections/iso_iseer_2point_result_table.py` were not modified.

## Commit / Push

- Source/test commit: `95fe983 fix: fit iso profile switch window`
- Docs/report commit: pending at report write time
- Push: pending at report write time

## Project Memory Delta

- none
