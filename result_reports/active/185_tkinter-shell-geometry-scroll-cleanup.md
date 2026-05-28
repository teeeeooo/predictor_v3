# 185 Tkinter Shell Geometry Scroll Cleanup

## Goal

Catch up the active report trail for the 185-a through 185-d Tkinter
calculator shell cleanup work before starting the 186 PyQt reference
parity audit.

## Scope

- Summarize the no-change structure audit, geometry helper extraction,
  `ScrollableFrame` extraction, and wheel-binding micro cleanup.
- Record the relevant source commits and focused verification outcome.
- Update `docs/WORK_PLAN.md` with the checkpoint and next action.

## Non-goals

- No Python source or test changes.
- No `project_log.md` or `result_reports/memory/project_memory_seed.md`
  updates.
- No lifecycle summary/archive maintenance.
- No full pytest run.

## Background

Tkinter calculator shell stabilization used several fast smoke-loop
source cleanup commits where result report creation was intentionally
deferred. This report captures that cleanup as one active checkpoint so
the next work item can move to parity auditing with the current shell
state documented.

## Task Results

### 185-a No-change Source Structure Audit

- Conclusion: the current Tkinter shell structure was still viable, but
  small cleanup was needed before extending more PyQt reference features.
- Cleanup candidates identified:
  - extract app window geometry helpers from the shell;
  - reduce shell-tab coupling through duck-typed/protocol-style helpers;
  - extract Canvas/Scrollbar/content-frame scroll responsibility into a
    reusable `ScrollableFrame`.

### 185-b Geometry Helper Extraction

- Source commit: `e0ca860` (`refactor: extract window geometry helpers to ui_tk/window_geometry.py`).
- Added `ui_tk/window_geometry.py`.
- Moved five window geometry helpers out of `ui_tk/calculator_app.py`.
- Relaxed `apply_overflow_correction()` to work against a duck-typed
  scroll target instead of the concrete ISO tab implementation.

### 185-c ScrollableFrame Extraction

- Source commit: `6878732` (`refactor: extract ScrollableFrame helper, decouple Iso16358Tab scroll logic`).
- Added `ui_tk/scrollable_frame.py`.
- Moved Canvas, vertical Scrollbar, content frame, auto-hide scrollbar,
  mousewheel handling, and width sync responsibility into
  `ScrollableFrame`.
- Reduced `Iso16358Tab` to region selector, metric notebook, metric
  section rendering, and preferred-size delegation.

### 185-d Micro Cleanup

- Source commit: `411b975` (`Fix Tk scrollable frame wheel cleanup`).
- Corrected the `Iso16358Tab` class docstring to match the current
  region selector plus metric sub-tab structure.
- Removed `ScrollableFrame` global `bind_all()` / `unbind_all()` wheel
  binding dependency.
- Switched to toplevel-scoped per-instance wheel bindings with stored
  funcids and targeted unbind on destroy.
- Added a sibling destroy regression test so destroying one
  `ScrollableFrame` does not remove another instance's wheel handling.

## Verification

- 185-b focused verification included `python3 -B tools/check_code_structure.py`,
  targeted py_compile, and focused Tkinter foundation tests for geometry
  helper behavior.
- 185-c focused verification covered `ScrollableFrame` overflow/auto-hide
  behavior, resize geometry no-hang guard, CSPF/HSPF metric sub-tab
  presence, and default result rendering.
- 185-d focused verification:
  - `python3 -B tools/check_code_structure.py`: OK.
  - `python3 -B -m py_compile ui_tk/scrollable_frame.py ui_tk/tabs/iso16358_tab.py tests/test_ui_tk_calculator_foundation.py tests/test_ui_tk_iso_table_autocalc.py`: OK.
  - `python3 -B -m pytest tests/test_ui_tk_calculator_foundation.py tests/test_ui_tk_iso_table_autocalc.py -q -rxXs`: `23 passed in 1.17s`.
  - `git diff --check`: clean.
- This report catch-up task verified documentation only with
  `python3 -B tools/check_code_structure.py` and `git diff --check`.

## Changed Files

- `result_reports/active/185_tkinter-shell-geometry-scroll-cleanup.md`
  - New active checkpoint report for the 185-a through 185-d cleanup.
- `docs/WORK_PLAN.md`
  - Added the 185 shell cleanup checkpoint and the recommended next
    action.

## Known Failures / Risks

- Manual smoke was already reported as passing for window size, resize,
  scrollbar, CSPF/HSPF sub-tabs, auto-calc, and table edit/copy/paste/
  undo/navigation, but this catch-up task did not rerun manual UI smoke.
- `ScrollableFrame` is still intentionally narrow: no geometry policy
  redesign, no scrollbar behavior redesign, and no root-level Configure
  binding were added.
- Graph/detail, multi calculation, SASO, ISO 2-point, EN/AHRI expansion,
  packaging, and PyQt retirement remain outside this cleanup.

## Next Suggested Action

Run the 186 PyQt reference parity audit.

## Scope Compliance

- Python source and tests were not modified by this report catch-up task.
- Only `docs/WORK_PLAN.md` and this active report were modified.
- `project_log.md`, `result_reports/memory/project_memory_seed.md`, and
  lifecycle summary/archive maintenance were not touched.
- Full pytest was not run.

## Commit / Push

- Related source commits: `e0ca860`, `6878732`, `411b975`.
- Report/docs catch-up commit: '998db9b' (Report/docs catch-up commit: recorded in final terminal summary)
- Push target: `origin/work/ui-ux-ssot-adoption`.

## Project Memory Delta

- none
