# 221C — Dynamic Content Refit Loop Stabilization

## Goal

Stabilize the Hong Kong profile after the 221B nested notebook refit change and
stop the Windows resize / repaint / refit loop. Height optimization is
secondary to keeping the app usable.

## Windows Symptom

After `a0799a3`, entering the Hong Kong profile produced a rapid loop between a
grey intermediate screen and the real window. The app was repainting/resizing
instead of becoming idle.

## Cause Path

221B introduced two local refit changes inside `Iso16358Tab`:

- direct metric notebook `<<NotebookTabChanged>>` refit scheduling;
- a two-step idle scheduler that temporarily released the pending guard between
  the first and second idle callbacks.

The risky loop path is:

1. `preferred_initial_size()` selects hidden metric tabs to measure width.
2. `ttk.Notebook.select()` can emit `<<NotebookTabChanged>>` now or on a later
   event-loop turn.
3. The tab-change handler schedules another refit.
4. The refit calls `preferred_initial_size()` again.
5. The pending guard was already released during the intermediate idle phase,
   so duplicate/reentrant scheduling could continue.

Detail open/close appearing to fix the size is still evidence that a later
settled refit is useful, but direct tab-change refit inside the tab is not safe
without a stronger common owner.

## Stabilization Changes

Modified `ui_tk/tabs/iso16358_tab.py`:

- removed the direct `<<NotebookTabChanged>>` binding from the Hong Kong metric
  notebook;
- kept `_on_metric_tab_changed()` as a disabled compatibility hook with an
  explicit comment;
- kept the settled refit scheduler for profile/detail/region paths;
- changed the scheduler so `_pending_refit_id` stays set through the
  intermediate idle and active fit, and is cleared only after the fit completes;
- kept the `preferred_initial_size()` hidden-tab measurement suppress guard.

This intentionally rolls back the risky part of 221B: direct metric tab-change
refit scheduling. The app should prefer stable behavior over the remaining
height optimization until a common dynamic refit owner exists.

## Tests

Modified `tests/test_ui_tk_iso_table_autocalc.py`:

- updated metric tab-change acceptance to disabled until a common owner exists;
- kept measurement suppress coverage;
- added a reentrant scheduling guard test for requests made during an active
  fit;
- strengthened the settled scheduler test so intermediate idle callbacks do
  not allow duplicate scheduling.

## Owner Boundary Judgment

The refit responsibility is now too broad for `Iso16358Tab` alone. The behavior
crosses:

- profile switch;
- nested tab switch;
- detail open/close;
- scrollable content settle;
- hidden-tab measurement suppress guards;
- reentrant scheduling protection.

This is not Hong Kong-specific and can repeat in Tkinter, PySide/WPF, or Web
surfaces with nested/dynamic content. A common dynamic content refit owner is
recommended before reintroducing nested tab-change refit.

## 221D Need

Yes. Proposed next task: common dynamic content refit owner preflight. It should
decide the shared owner boundary and first slice for coalescing refit requests,
measurement suppress guards, running/pending protection, and toolkit adapter
responsibilities.

## Validation

- `python -m pytest -q tests/test_ui_tk_iso_table_autocalc.py` — passed with
  Tk-dependent skips in the headless environment.
- `python -m pytest -q tests/test_ui_tk_calculator_foundation.py` — passed with
  Tk-dependent skips in the headless environment.
- `python -m pytest -q tests/test_ui_tk_iso16358_helpers.py tests/test_ui_tk_profile_resolver.py` — passed.
- `python3 -B tools/check_code_structure.py` — passed with the existing soft
  warning that `ui_tk/sections/bin_detail_panel.py` exceeds 400 LOC.
- `git diff --check` — passed.
- `git status --short` — reviewed before commit.

Not run:

- `python app_calculator_tk.py` — `DISPLAY` is not set in the Codex
  environment.

## Windows Manual Smoke

- Hong Kong profile entry no longer loops.
- Hong Kong CSPF screen is usable.
- Profile switch away and back to Hong Kong does not loop.
- CSPF/HSPF metric tab switching does not loop.
- Detail open/close does not loop.
- Selected-range fill paste remains OK.
- Batch dialog sizing remains OK.

## Excluded Scope

- no calculator core changes;
- no region config, fixture, or golden changes;
- no table foundation changes;
- no main table migration;
- no HSPF / EN14825 / AHRI / KS batch work;
- no 07 policy or docs/designs edits;
- no report lifecycle/archive maintenance;
- no common refit owner implementation.

## Next Action

Common dynamic content refit owner preflight.
