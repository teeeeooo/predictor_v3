# 225 — Hong Kong Profile-switch Sizing Closeout

## Goal

Close the remaining Hong Kong profile-switch sizing gap without reintroducing
the infinite refit loop fixed in 221C. Scope is limited to the path where the
user switches away from Hong Kong and returns.

## Windows Smoke Reproduction

- Switching from another profile back to Hong Kong leaves lower blank space on
  the CSPF screen.
- Re-selecting a CSPF/HSPF metric tab inside the Hong Kong notebook normalizes
  the height.
- Opening and closing detail also normalizes the height.
- There is no infinite resize loop.
- Selected-range fill paste is OK.
- Batch dialog blank space is out of scope for this task.

## Cause Judgment

The common refit owner from 224 correctly coalesces and guards refit requests,
but the Hong Kong profile-switch path still has a timing gap:

1. `_on_mode_changed()` renders Hong Kong and packs the Hong Kong frame.
2. `_render_region()` recreates metric sections and adds them to the nested
   metric notebook.
3. The default settled refit can still measure before the nested notebook /
   current tab requested size has fully stabilized.
4. A later user event, such as metric tab re-selection or detail toggle, causes
   another fit after layout has settled, which removes the blank space.

This points to stale requested size after profile switch rather than a geometry
math defect. `ui_tk/window_geometry.py` was not changed.

## Changes

Modified `ui_tk/window_refit.py`:

- `request_refit()` now accepts `settle_cycles`.
- the default remains one settle cycle, preserving existing behavior;
- pending requests can extend settle cycles upward without creating duplicate
  refit callbacks;
- pending/running/suppress guards remain in place.

Modified `ui_tk/tabs/iso16358_tab.py`:

- Hong Kong profile-switch refit now requests `settle_cycles=2`;
- other profile/detail/region paths keep the default behavior;
- direct metric notebook tab-change refit remains disabled.

Modified tests:

- added common scheduler tests for extra settle cycles;
- added pending-request cycle extension coverage;
- updated the `Iso16358Tab` profile/detail scheduler test to confirm Hong Kong
  mode switch requests the extra settle cycle.

## Flicker Judgment

This slice may still show ordinary resize/repaint during profile switch because
window fitting is still automatic. It should not recreate the rapid loop. A
broader flicker policy or full geometry redesign is intentionally out of scope.

## Validation

- `python -m pytest -q tests/test_ui_tk_window_refit.py` — passed.
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

- Switching from another profile back to Hong Kong reduces the CSPF lower blank
  space.
- Hong Kong profile entry has no infinite resize loop.
- CSPF/HSPF metric tab re-selection remains normal.
- Detail open/close remains normal.
- Profile switch flicker level is acceptable.
- Selected-range fill paste remains OK.
- Batch dialog sizing remains in its previous OK state.

## Excluded Scope

- no calculator core changes;
- no region config, fixture, or golden changes;
- no table foundation changes;
- no main table migration;
- no batch dialog sizing fix;
- no HSPF / EN14825 / AHRI / KS batch work;
- no PySide/WPF/Web implementation;
- no UI policy, docs/designs, or report lifecycle work;
- no full window sizing redesign.

## Next Action

Windows smoke closeout for Hong Kong profile-switch sizing and common dynamic
refit owner behavior.
