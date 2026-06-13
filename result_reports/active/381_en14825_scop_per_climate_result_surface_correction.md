# 381 EN14825 SCOP Per-Climate Result Surface Correction

## Goal

Correct the EN14825 SCOP result surface regression by removing the root-level
right-side result panel and placing compact results inside each climate
condition block.

## Scope / Non-goals

- Scope: SCOP section-local layout, SCOP-local result surface helper, focused
  SCOP UI test expectations, and `WORK_PLAN` next-action wording.
- Non-goals: core calculation, adapter/model/input mapper changes, SEER tab
  changes, common `MetricInputTable` or `ResultPanel` framework changes,
  fixture/golden updates, shared result framework extraction, or unrelated
  refactor.

## Changes

- Removed the SCOP section root-level `SCOP 결과` surface from `_frame`
  `column=1`.
- Added `ScopResultSurface`, a SCOP-local compact result table helper for
  Declared/Tested rows.
- Placed each climate result block inside its own `Average/Warmer/Colder 조건`
  LabelFrame, to the right of that climate's auxiliary inputs and input table.
- Kept the compatibility `result_panel` as an ungridded text/copy model for
  existing non-layout paths.
- Preserved Tdesignh as a read-only label sourced from climate config through
  the existing adapter path.
- Updated focused tests to assert that the old root surface is gone and that
  climate-local result blocks follow active/inactive climate visibility.

## Design / Boundary Judgment

The prompt-supplied boundary was sufficient for Design Gate: this is
section-local presentation work. Calculation, schema, adapter, model, mapper,
and common UI framework boundaries remain unchanged.

## Structure Warning Triage

- `en14825_scop_section.py` remains above the soft 400 LOC warning, but this
  slice reduced result-widget responsibility by extracting a SCOP-local helper.
- `ScopResultSurface` owns only widget construction, visibility, value clearing,
  and summary/error display for the compact SCOP result block.
- Remaining section responsibilities are climate card composition, input table
  ownership, scheduling, calculation orchestration, and table repainting.
- Next action: accepted for this slice. A broader climate card split remains a
  separate follow-up only if further SCOP layout/refit responsibility is added.

## Validation

- `python3 -B -m py_compile apps/calculator/ui/sections/en14825_scop_section.py` OK.
- `python3 -B -m py_compile apps/calculator/ui/sections/en14825_scop_result_formatter.py` OK.
- `python3 -B -m py_compile apps/calculator/ui/sections/en14825_scop_result_surface.py` OK.
- `python3 -B -m pytest tests/test_apps_calculator_ui_en14825_scop.py -q` OK, 23 passed.
- `python3 -B tools/check_code_structure.py` OK with one accepted soft LOC
  warning for `apps/calculator/ui/sections/en14825_scop_section.py` at 453 LOC.
- `git diff --check` OK.
- `git status --short` showed only scoped source/test/docs/report changes.
- Active report count check: 17 active reports; lifecycle cleanup remains a
  separate follow-up.

## Known Risks / Gaps

- Manual GUI smoke was not run in this slice; first-launch width, SEER tab
  width, and target desktop visual fit still require manual closeout.

## Project Memory Delta

- none

## Commit / Push

- Not performed.
