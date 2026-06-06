# 233C - Profile Reselect / Detail Lifecycle Orchestration

## Goal

Unify profile switch, same-profile reselect, and detail toggle around the same
visible-surface lifecycle refit path. This is a lifecycle orchestration slice,
not a Hong Kong sizing hotfix.

## Current Lifecycle Evaluation

Before this change:

- profile switch called `_render_mode(...)` and then scheduled a refit;
- Hong Kong reselect also called `_render_mode(...)`, which rebuilt the Hong
  Kong metric notebook even though the same surface was already visible;
- detail toggle called the refit scheduler directly;
- all paths eventually reached the same scheduler and shell fit, but they did
  not share a small visible-lifecycle boundary.

The main visible mutation risk was same-profile reselect causing unnecessary
forget/destroy/create work before the fit path. The 233A/233B findings remain
valid: snapshot measurement is kept, and the remaining issue is lifecycle
ordering/visible mutation rather than geometry primitives.

## MVC / SoC Boundary

- `Iso16358Tab` remains the view/consumer that knows profile widgets and user
  events.
- `window_refit.py` remains the scheduling/guard owner.
- `window_shell.py` remains the shell geometry apply owner.
- `window_measurement.py` remains the Tk measurement snapshot adapter.

No new abstraction was added. The view now exposes a smaller
`_request_visible_lifecycle_refit(...)` boundary instead of each event path
owning its own refit call shape.

## Implementation

- Added `_request_visible_lifecycle_refit(...)` as the common lifecycle request
  boundary in `Iso16358Tab`.
- Updated profile switch, region change, and detail toggle to use that boundary.
- Added `_rendered_mode_label` tracking.
- Same-profile reselect now skips `_render_mode(...)` and only requests a
  lifecycle refit. This avoids unnecessary visible destroy/create work.
- First switch into Hong Kong still uses the existing extra settled cycle.
- 233B snapshot provider registration remains unchanged.
- Direct metric tab-change refit remains disabled.

No Hong Kong-only branch, fixed window size, withdraw/deiconify hack, extra
settle-cycle-only patch, or batch dialog change was added.

## Tests

- `tests/test_ui_tk_iso_table_autocalc.py`
  - confirms profile and detail paths share the lifecycle refit boundary;
  - confirms same-profile reselect requests refit without rerendering;
  - confirms region change uses the lifecycle refit boundary;
  - keeps scheduler, metric-tab suppression, and lower-level behavior tests.

## Validation

- `python -m pytest -q tests/test_ui_tk_iso_table_autocalc.py`: passed with Tk
  skips in this environment.
- `python -m pytest -q tests/test_ui_tk_window_refit.py`: passed.
- `python -m pytest -q tests/test_ui_tk_window_shell.py`: passed.
- `python -m pytest -q tests/test_ui_tk_window_measurement.py`: passed.
- `python -m pytest -q tests/test_ui_tk_calculator_foundation.py`: passed with
  Tk skips in this environment.
- `python -m pytest -q tests/test_ui_tk_iso16358_helpers.py tests/test_ui_tk_profile_resolver.py`: passed.
- `python3 -B tools/check_code_structure.py`: passed with existing warning:
  `ui_tk/sections/bin_detail_panel.py` exceeds the 400 LOC soft limit.
- `git diff --check`: passed.
- `git status --short`: showed only expected 233C changes before commit.

## Windows Manual Smoke Needed

- Hong Kong profile switch after another profile: lower blank space remains
  resolved.
- No infinite refit loop.
- Profile switch flicker is reduced.
- Hong Kong reselect has no size jump.
- Detail open/close flicker is reduced.
- CSPF/HSPF metric tab switching remains normal.
- Selected-range fill paste remains OK.
- Batch dialog remains at previous sizing/UX state.

## Excluded

- No batch dialog sizing/UX fix.
- No batch copy/export or two-row matrix work.
- No HSPF detail, EN14825/AHRI/KS expansion.
- No calculator core, region config, fixture/golden, UI/UX doc, architecture
  doc, or report lifecycle change.

## Next Action

Windows smoke closeout for 233C flicker reduction. If acceptable, continue to
batch dialog sizing/UX under the same window shell policy.
