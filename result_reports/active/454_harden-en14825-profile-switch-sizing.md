# 454 Harden EN14825 Profile-Switch Sizing

## Goal

Prevent invalid negative top-level geometry during a profile switch into
EN14825, while preserving the common visible-content sizing policy and wiring
the missing SEER detail visibility refit callback.

## Scope

- Diagnose the nested-notebook measurement path that produced
  `411x-80+285+100`.
- Add a bounded measurement fallback and a final common geometry lower clamp.
- Connect EN14825 SEER detail visibility to the existing tab refit lifecycle.
- Add relationship-based focused regressions for measurement, geometry, profile
  switching, and SEER/SCOP detail behavior.

## Non-goals

- No core, config, data, fixture, golden, calculator result, detail payload,
  profile layout, fixed geometry, or profile-specific minimum-size change.
- No AHRI SEER2 implementation or unrelated sizing refactor.

## Root Cause

During a profile transition, the raw content request and selected nested tab can
be transiently small while the nested notebook still reports a sticky requested
height from a larger sibling. The replacement arithmetic subtracted that sticky
notebook height from the smaller content request, producing a negative adjusted
content height. The negative value then reached the geometry formatter because
the common cap had only an upper bound. The parser correctly rejected the
invalid geometry and remains strict.

## Task Results

- `TkVisibleContentMeasurement` now records raw, adjusted, and effective content
  dimensions. A non-positive adjusted dimension falls back to the positive raw
  request or the current-tab-plus-chrome estimate before margins are calculated.
- `capped_window_size()` now applies the existing common minimum-visible width
  and height tokens after screen capping, so downstream geometry is always
  positive even if a caller supplies a transient invalid preferred size.
- `En14825Tab` now gives `En14825SeerSection` the same visible-lifecycle refit
  callback already used by SCOP.
- No parser relaxation, widget geometry forcing, or profile-local size special
  case was introduced.

## Verification

- Focused measurement/geometry/profile-switch/AHRI-refit suite — 28 passed.
- EN14825 SEER/SCOP detail suite — 9 passed.
- `python3 -B tools/check_code_structure.py` — no errors; four known soft
  warnings only.
- `python3 -B tools/code_checker/build_reference_map.py --check` — stale from
  prior commit metadata; regenerated once.
- `git diff --check` — passed.
- `python3 -B tools/check_agent_change_gate.py --cached` — passed.

## Manual Check

Required: switch another profile to EN14825 with SEER selected, repeat with SCOP,
toggle SEER/SCOP detail visibility, and confirm positive stable window geometry
without a Tk geometry exception.

## Changed Files

- `apps/calculator/ui/window_measurement.py`
- `apps/calculator/ui/window_geometry.py`
- `apps/calculator/ui/tabs/en14825_tab.py`
- `tests/test_ui_tk_window_measurement_side_effect_free.py`
- `tests/test_ui_tk_window_shell.py`
- `tests/test_ui_tk_en14825_profile_switch_fit.py`
- `docs/WORK_PLAN.md`
- `docs/code_map/CODEBASE_REFERENCE_MAP.md`
- `result_reports/active/454_harden-en14825-profile-switch-sizing.md`

## Known Risk

Tk requested-size timing is platform dependent. The relationship regressions
cover the failure arithmetic and actual profile-switch path, but final macOS
visual confirmation remains required.

## Change Gate

```yaml
change_gate:
  new_source: small
  hotspot_delta: none
  code_map_check: regenerated
  ui_literal_exemption: none
  report_exemption: none
  read_ledger: included
```

Read Ledger:

- `AGENT_TASK_ROUTER.md`: UI/source/report routes already reviewed; reason:
  implementation, validation, and report boundaries.
- `window_measurement.py`, `window_geometry.py`, EN14825 tab, and focused sizing
  tests: relevant measurement-to-geometry path only; reason: root-cause and
  bounded correction.
- EN14825 SEER/SCOP detail tests: focused lifecycle ranges; reason: callback and
  detail regression coverage.
- `docs/WORK_PLAN.md`: current/next sections; reason: execution-board sync.
- broad read: none
- repeated read: none

## Next Action

EN14825 profile-switch visual smoke, then AHRI SEER2 detail view implementation.
