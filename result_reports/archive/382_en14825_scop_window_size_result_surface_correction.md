# 382 EN14825 SCOP Window Size Result Surface Correction

## Goal

Fix EN14825 SCOP manual-smoke UX regressions around first-launch/SEER tab window
width and the per-climate SCOP result surface presentation.

## Scope / Non-goals

- Scope: SCOP section layout, SCOP-local result surface styling, EN14825 tab
  focused tests, window measurement owner correction for nested notebook width,
  and `WORK_PLAN` next-action wording.
- Non-goals: core/data/tools changes, EN14825 adapter/model/table model changes,
  SEER calculation/table logic changes, common `MetricInputTable` or
  `ResultPanel` framework changes, fixture/golden changes, shared result
  framework extraction, or unrelated refactor.

## Root Cause

Manual smoke exposed two related issues:

- The SCOP per-climate side-by-side result block increased the hidden SCOP tab
  requested width.
- `TkVisibleContentMeasurement` replaced sticky nested-notebook width with
  `chrome + current_tab_width`, but its chrome estimate was computed as
  `notebook_reqwidth - current_tab_width`. When SEER was selected and hidden
  SCOP was wider, that produced an inflated chrome estimate and made SEER
  preferred width inherit the hidden SCOP width.

Measured before correction in the local Tk environment:

- SEER selected preferred width: 1389.
- SCOP frame requested width: 1247.
- Chrome width estimate: 524.

Measured after correction:

- SEER selected preferred width: 895.
- SCOP selected preferred width: 1389.
- Chrome width estimate: 54.

## Changes

- `window_measurement.py` now estimates nested-notebook width chrome by
  subtracting the widest known tab requested width, while still measuring the
  current selected tab for preferred visible content.
- SCOP climate cards now place auxiliary inputs in row 0 and both the input
  table and result surface in row 1, aligning result table top with the input
  table top border.
- `ScopResultSurface` now starts with the header row, replaces the blank
  top-left placeholder with `구분`, moves status below the result rows, and uses
  pass-green background for Tested row/value cells.
- Focused tests cover SEER preferred-size isolation from hidden SCOP width,
  SCOP result/input row alignment, top-left header styling, and Tested pass
  emphasis.

## Boundary Judgment

The window owner change is minimal and limited to nested-notebook measurement.
It does not select hidden tabs, does not change refit scheduling, and preserves
the current visible tab as the preferred-size source. SCOP visual changes remain
inside the SCOP section/helper.

## Structure Warning Triage

- `en14825_scop_section.py` remains above the 400 LOC soft warning but this
  slice did not add new calculation/model responsibility.
- `ScopResultSurface` remains SCOP-local and owns only compact result widget
  construction, visibility, clearing, and value/status display.
- Next action: accepted for this slice. A broader climate card split remains a
  separate follow-up only if future SCOP layout/refit responsibility grows.

## Validation

- `python3 -B -m py_compile apps/calculator/ui/sections/en14825_scop_section.py` OK.
- `python3 -B -m py_compile apps/calculator/ui/sections/en14825_scop_result_surface.py` OK.
- `python3 -B -m pytest tests/test_apps_calculator_ui_en14825.py -q` OK, 17 passed.
- `python3 -B -m pytest tests/test_apps_calculator_ui_en14825_scop.py -q` OK, 23 passed.
- `python3 -B -m pytest tests/test_ui_tk_window_measurement_side_effect_free.py -q` OK, 9 passed.
- `python3 -B tools/check_code_structure.py` OK with one accepted soft LOC
  warning for `apps/calculator/ui/sections/en14825_scop_section.py` at 450 LOC.
- `git diff --check` OK.
- `git status --short` showed only scoped source/test/docs/report changes.
- Active report count check: 18 active reports; lifecycle cleanup remains a
  separate follow-up.

## Known Risks / Gaps

- Target desktop manual smoke still needs to confirm first-launch width, SEER
  tab width, and final visual alignment.

## Project Memory Delta

- none

## Commit / Push

- Pending commit/push.
