# 221B — Hong Kong Nested Notebook Refit Scheduling

## Goal

Apply the 221A nested notebook / dynamic sub-tab refit policy to the Hong Kong
metric notebook so CSPF/HSPF visible content drives main-window height after
profile switches, metric tab switches, and detail toggles.

## Cause

220 changed Hong Kong preferred height to follow the current visible metric tab,
but the nested metric notebook did not schedule a refit when its visible tab
changed. Profile switch and detail toggle had separate direct `after_idle`
paths, so the first fit could still run before nested notebook content had fully
settled. Opening and closing detail later made the height look correct because
that path happened to force another fit after layout stabilization.

## Changes

Modified `ui_tk/tabs/iso16358_tab.py`:

- added a shared `_schedule_toplevel_refit()` path used by profile switch,
  detail visibility changes, region changes, and metric tab changes;
- implemented a settled two-step idle refit so the final fit runs after a later
  event-loop turn;
- bound Hong Kong metric notebook `<<NotebookTabChanged>>` to the scheduler;
- added a measurement suppress guard so `preferred_initial_size()` can
  temporarily select hidden metric tabs for width measurement without queuing
  recursive refits;
- kept hidden tab width protection and current-visible-tab height behavior.

Modified `tests/test_ui_tk_iso_table_autocalc.py`:

- added scheduler tests for double-idle settled refit;
- added metric tab-change scheduler test;
- added measurement suppress guard test;
- added profile/detail shared scheduler path test;
- updated the preferred-size wording to state that hidden metric tabs are not
  summed for height.

Modified `docs/WORK_PLAN.md`:

- moved next action back to Windows GUI smoke closeout for the common-foundation
  batch table and Hong Kong metric notebook sizing.

## 221A Policy Coverage

- Profile switch, nested tab switch, and detail toggle now use one scheduling
  policy.
- Metric tab changes are explicit refit triggers.
- Hidden-tab measurement suppresses tab-change refit callbacks.
- Geometry measurement and mutation remain outside synchronous configure paths.
- Focused tests cover scheduler and suppress behavior before Windows smoke.

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

- Hong Kong CSPF main screen lower blank space is reduced.
- Switching away from Hong Kong and back preserves normal height.
- CSPF/HSPF metric tab switching refits to the current visible tab height.
- Detail open/close keeps height normal.
- Batch dialog sizing remains unchanged from the previous OK state.

## Excluded Scope

- no calculator core changes;
- no region config, fixture, or golden changes;
- no table foundation changes;
- no main table migration;
- no HSPF / EN14825 / AHRI / KS batch work;
- no docs/designs or report lifecycle/archive work.

## Next Action

Windows GUI smoke closeout for the common-foundation batch table and Hong Kong
metric notebook sizing.
