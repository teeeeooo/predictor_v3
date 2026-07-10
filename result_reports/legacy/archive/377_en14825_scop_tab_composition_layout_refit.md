# 377 EN14825 SCOP Tab Composition Layout Refit

## Goal

Connect the EN14825 SCOP section into the EN14825 tab composition and preserve
layout/refit behavior before manual smoke closeout.

## Scope / Non-goals

- Scope: EN14825 nested `SEER`/`SCOP` selection surface, SCOP section
  composition, nested notebook measurement/refit wiring, focused integration
  test, `WORK_PLAN` update.
- Non-goals: new card UI, shared card framework, climate card component split,
  SCOP input mapping/result formatting changes, adapter/table model/model
  changes, `ResultPanel`/`MetricInputTable` changes, core/config changes,
  fixture/golden changes, workflow docs, memory, project log, lifecycle cleanup,
  or manual GUI smoke.

## Tab Composition Behavior

- `En14825Tab` now contains a nested `ttk.Notebook` with compact `SEER` and
  `SCOP` labels.
- Existing SEER section remains available through `seer_section` and keeps the
  compatibility `result_panel` alias.
- SCOP is instantiated as `scop_section` inside the EN14825 tab; the
  top-level `CalculatorTkApp` EN14825 notebook registration did not need
  changes.

## Layout / Refit Behavior

- The EN14825 tab passes its visible lifecycle refit callback into
  `En14825ScopSection`.
- SCOP Average/Warmer/Colder toggle changes continue to trigger section
  recalculation and now request parent tab refit through the composition layer.
- Nested notebook tab changes request the same refit scheduler.
- `TkVisibleContentMeasurement` now receives the EN14825 nested notebook so
  current SEER/SCOP content participates in preferred-size measurement.

## MVC/SoC Judgment

The tab owns composition and lifecycle/refit wiring. SCOP section remains widget
and lifecycle glue. Input mapping stays in `en14825_scop_input_mapper.py`; result
formatting stays in `en14825_scop_result_formatter.py`. No adapter/table
model/model responsibility changed.

## Behavior Preservation

- SEER remains the default nested tab and existing SEER integration tests pass.
- SCOP default Average recalculate still completes without crash.
- SCOP warmer/colder toggle requests parent refit without changing the existing
  LabelFrame card structure.

## Tests

- Added focused EN14825 tab composition/refit test:
  - `SEER`/`SCOP` selection surface exists;
  - SEER and SCOP sections are instantiated;
  - SCOP Average recalculation succeeds;
  - nested tab change and warmer/colder toggles request parent refit.
- Existing EN14825 SEER and SCOP focused test files pass.

## Validation

- `python3 -B -m py_compile apps/calculator/ui/tabs/en14825_tab.py` OK.
- `python3 -B -m py_compile apps/calculator/ui/calculator_app.py` OK.
- `python3 -B -m py_compile apps/calculator/ui/sections/en14825_scop_section.py` OK.
- `python3 -B -m pytest tests/test_apps_calculator_ui_en14825.py -q` OK, 16 passed.
- `python3 -B -m pytest tests/test_apps_calculator_ui_en14825_scop.py -q` OK, 22 passed.
- `python3 -B tools/check_code_structure.py` OK with one accepted soft LOC warning.
- `git diff --check` OK.
- `git status --short` showed only scoped source/test/docs/report changes before commit.
- `find result_reports/active -maxdepth 1 -type f -name '*.md' | wc -l` OK; exact count is reported only in terminal output.

## Structure Warnings / Warning Triage

- Structure Warnings: existing
  `apps/calculator/ui/sections/en14825_scop_section.py` 400 LOC soft warning
  remains.
- Warning Triage: accepted for this slice with reason. This task did not modify
  SCOP section mapping/formatting or add new section responsibility; it only
  composed the existing section and wired parent refit.

## Known Risks / Gaps

- Manual GUI smoke was intentionally not run in this task.
- Active report lifecycle cleanup remains a separate follow-up because this task
  does not move summary/archive files.

## Next Suggested Action

Run EN14825 SCOP tab composition manual smoke closeout on the target desktop.

## Project Memory Delta

- none

## Commit / Push

- Source/test and docs/report commits are separated when practical.
- Final commit hashes and push status are reported in terminal output to avoid a
  self-referential report update loop.
