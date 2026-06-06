# 233C-2 - Hong Kong Profile Switch Reuse Cache

## Goal

Reduce the remaining soft flicker after 233C by reusing the already-rendered
Hong Kong metric surface when returning from another profile with the same
region. This is a micro-slice, not a new lifecycle framework.

## Reuse Safety Judgment

Hong Kong sections are created by `_render_region(...)` inside the metric
notebook. Moving to another profile hides `_hong_kong_frame` but does not need
to destroy the metric notebook children. The destructive work was happening
when returning to Hong Kong because `_render_mode(MODE_HONG_KONG)` always
called `_render_region(...)`.

Reuse is safe when:

- the rendered Hong Kong region label matches the current region combo value;
- cached Hong Kong sections exist;
- the metric notebook still has tabs.

Region change still requires rerender because the supported metrics and section
configuration can change. Pending Hong Kong auto-calc jobs continue to be
cancelled when leaving the Hong Kong surface.

## Implementation

- Added cached Hong Kong state in `Iso16358Tab`:
  - `_rendered_hong_kong_region_label`;
  - `_hong_kong_sections`;
  - `_hong_kong_result_panel`.
- Added `_can_reuse_hong_kong_region(...)`.
- On Hong Kong mode entry, the tab now reuses cached sections/result panel when
  the region is unchanged and notebook tabs are still valid.
- Region change still calls `_render_region(...)` and refreshes the cache.
- Same-profile reselect behavior from 233C is unchanged.
- Snapshot provider, refit scheduler, and shell fit contracts are unchanged.

No Hong Kong sizing branch, fixed window size, withdraw/deiconify, extra settle
cycle, or cache framework was added.

## MVC / SoC Boundary

This stays inside `Iso16358Tab` because it is view-owned surface reuse for
already-created widgets. Measurement, scheduling, and geometry ownership remain
in `window_measurement.py`, `window_refit.py`, and `window_shell.py`.

## Tests

- `tests/test_ui_tk_iso_table_autocalc.py`
  - confirms profile switch back to Hong Kong with the same region reuses the
    existing surface and does not call `_render_region(...)`;
  - confirms lifecycle refit is still requested;
  - confirms region change still rerenders;
  - keeps same-profile reselect and existing refit tests.

## Validation

- `python -m pytest -q tests/test_ui_tk_iso_table_autocalc.py`: passed with Tk
  skips in this environment.
- `python -m pytest -q tests/test_ui_tk_calculator_foundation.py`: passed with
  Tk skips in this environment.
- `python3 -B tools/check_code_structure.py`: passed with existing warning:
  `ui_tk/sections/bin_detail_panel.py` exceeds the 400 LOC soft limit.
- `git diff --check`: passed.
- `git status --short`: showed only expected 233C-2 changes before commit.

## Windows Manual Smoke Needed

- Other profile -> Hong Kong return: flicker is reduced.
- Hong Kong lower blank space remains resolved.
- No infinite refit loop.
- Hong Kong reselect has no size jump.
- Region change updates the screen correctly.
- Detail open/close remains normal.
- Selected-range fill paste remains OK.
- Batch dialog remains at the previous state.

## Excluded

- No lifecycle controller/framework.
- No batch dialog sizing/UX fix.
- No batch copy/export or two-row matrix work.
- No HSPF detail or EN14825/AHRI/KS expansion.
- No calculator core, region config, fixture/golden, UI/UX doc, architecture
  doc, or report lifecycle change.

## ROI Judgment

If Windows smoke still shows only soft residual flicker after this reuse slice,
further broad lifecycle refactoring should be held unless smoke evidence points
to a specific remaining visible mutation owner.

## Next Action

Windows smoke closeout for 233C-2 flicker reduction and sizing behavior.
