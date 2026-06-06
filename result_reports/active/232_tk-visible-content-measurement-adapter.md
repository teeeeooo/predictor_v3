# 232 — Tk Visible Content Measurement Adapter

## Goal

Extract the visible content measurement policy that remained inside
`Iso16358Tab` into a small Tk measurement adapter/provider. Hong Kong remains
the first consumer and Windows smoke target, but the adapter must not know
calculator formulas, region config, profile math, or seasonal metrics.

## Current Problem From 229 / 231

The content-hugging shell/refit/geometry owners now exist, but the Hong Kong
CSPF lower blank space remains after profile switch. The likely remaining
problem is stale or oversized visible-content measurement after render, not
the geometry apply itself.

`Iso16358Tab` still owned too much measurement policy:

- hidden metric tab width protection;
- current visible nested tab height selection;
- notebook chrome height subtraction;
- scroll overflow delta;
- suppressing refit requests while measurement temporarily selects hidden tabs.

That made the View both a widget composer and a measurement-policy owner.

## New Adapter / Provider

Added:

- `ui_tk/window_measurement.py`

The new `TkVisibleContentMeasurement` owner provides:

- visible content preferred size calculation;
- optional nested notebook measurement;
- hidden-tab width protection;
- current-visible-tab height preference;
- notebook chrome height calculation;
- vertical overflow delegation;
- measurement-time suppress guard integration.

The adapter is Tk measurement infrastructure. It has no Hong Kong, profile,
region, calculator, or table logic.

## Iso16358Tab Consumer Integration

`Iso16358Tab` now:

- creates `TkVisibleContentMeasurement` with content, scrollbar, scrollable
  overflow source, metric notebook, active predicate, and suppress guard;
- registers the adapter's `preferred_size` and `vertical_overflow_delta`
  providers with `TkContentHuggingShell`;
- keeps `preferred_initial_size()` and `vertical_overflow_delta()` as thin
  compatibility wrappers.

This reduces `Iso16358Tab` to composition plus provider wiring for this path.

## Boundary

- `window_measurement.py`: toolkit-specific visible content measurement policy.
- `window_shell.py`: reusable content-hugging shell/form API and one geometry
  apply target.
- `window_refit.py`: scheduling, pending/running guards, settled refit, and
  suppress guard.
- `window_geometry.py`: primitive geometry calculation and clamp helpers.
- `Iso16358Tab`: View/consumer that wires content-specific widgets and
  triggers.

## Tests

Added `tests/test_ui_tk_window_measurement.py`:

- simple content preferred size calculation;
- nested notebook uses hidden tabs for width but current visible tab for height;
- inactive nested notebook does not affect measurement;
- overflow delta delegates to the scrollable source.

Updated `tests/test_ui_tk_calculator_foundation.py` to assert the shell receives
adapter providers rather than direct `Iso16358Tab` measurement methods.

## Validation

- `python -m pytest -q tests/test_ui_tk_window_measurement.py`: passed.
- `python -m pytest -q tests/test_ui_tk_window_shell.py`: passed.
- `python -m pytest -q tests/test_ui_tk_calculator_foundation.py`: passed with
  Tk skips in this environment.
- `python -m pytest -q tests/test_ui_tk_iso_table_autocalc.py`: passed with Tk
  skips in this environment.
- `python -m pytest -q tests/test_ui_tk_iso16358_helpers.py tests/test_ui_tk_profile_resolver.py`: passed.
- `python3 -B tools/check_code_structure.py`: passed with existing warning:
  `ui_tk/sections/bin_detail_panel.py` exceeds the 400 LOC soft limit.
- `git diff --check`: passed.
- `git status --short`: expected code, test, WORK_PLAN, and report changes
  before commit.

## Windows Manual Smoke Needed

- Other profile to Hong Kong return: lower blank space removed or meaningfully
  reduced.
- Hong Kong profile reselect: no size jump.
- Detail open/close: lower blank space does not return.
- Profile/detail transition flicker is acceptable.
- No infinite refit loop.
- Selected-range fill paste remains OK.
- Batch dialog sizing remains at the previous state.

## Excluded

- No calculator core, region config, fixture, golden, or table foundation
  changes.
- No batch dialog sizing.
- No main table migration.
- No UI/UX, architecture, or window geometry policy document changes.
- No settle-cycle-only patch, Hong Kong local branch hotfix, or direct metric
  tab-change refit reintroduction.

## Next Action

Windows smoke closeout for Hong Kong profile-switch sizing and common dynamic
refit owner behavior.
