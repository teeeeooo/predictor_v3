# 380 EN14825 SCOP Result Surface UX Correction

## Goal

Move active SCOP results from the bottom of the input area to a compact
right-side result surface and add read-only Tdesignh display beside Pdesignh.

## Scope / Non-goals

- Scope: SCOP section-local compact result surface, SCOP result formatter rows,
  read-only Tdesignh labels, focused tests, `WORK_PLAN` next-action update.
- Non-goals: adapter/table model/model changes, input mapper changes,
  `ResultPanel` framework changes, EN14825 tab/common input changes, result
  framework extraction, climate card component split, editable Tdesignh, core or
  config changes, fixture/golden changes, workflow docs, memory/project log, or
  lifecycle cleanup.

## Result Surface Behavior

- Active Average/Warmer/Colder results render in a right-side `SCOP 결과`
  section-local surface.
- Declared and Tested values are displayed as stacked rows instead of a long
  horizontal summary.
- The previous bottom `ResultPanel` is not gridded; it remains as a compatibility
  text model for existing non-layout assertions.

## Tdesignh Display

- Each SCOP condition row now shows read-only `Tdesignh [°C]` next to
  `Pdesignh [W]`.
- Values are read from existing climate config through the adapter.
- No editable Tdesignh input was added.

## MVC/SoC Judgment

This is section-local presentation work. Input mapping, adapter calculation,
table model formatting, and common EN14825 input ownership remain unchanged.

## Behavior Preservation

- Existing SCOP recalculate path, active climate toggles, dynamic TOL/Tbiv
  headers, static table updates, and compatibility summary text still work.
- Inactive climate result cards stay hidden until their climate is activated.

## Tests

- Added/updated focused SCOP tests for right-side result surface placement,
  hidden bottom compatibility panel, Declared/Tested compact values, active
  climate result visibility, and read-only Tdesignh labels.
- Added formatter test coverage for compact Declared/Tested rows.

## Validation

- `python3 -B -m py_compile apps/calculator/ui/sections/en14825_scop_section.py` OK.
- `python3 -B -m py_compile apps/calculator/ui/sections/en14825_scop_result_formatter.py` OK.
- `python3 -B -m pytest tests/test_apps_calculator_ui_en14825_scop.py -q` OK, 23 passed.
- `python3 -B tools/check_code_structure.py` OK with one accepted soft LOC warning.
- `git diff --check` OK.
- `git status --short` showed only scoped source/test/docs/report changes before commit.

## Structure Warnings / Warning Triage

- Structure Warnings: `apps/calculator/ui/sections/en14825_scop_section.py`
  remains above the 400 LOC soft limit at 480 LOC.
- Warning Triage: accepted for this slice with reason. The requested UX is
  section-local presentation work and does not add mapping/calculation/model
  ownership. Revisit a section-local presentation split before adding further
  SCOP view responsibilities.

## Known Risks / Gaps

- Manual GUI smoke was intentionally not run in this task.
- Active report lifecycle cleanup remains a separate follow-up.

## Next Suggested Action

Run EN14825 SCOP result surface manual smoke closeout.

## Project Memory Delta

- none

## Commit / Push

- Final commit hashes and push status are reported in terminal output.
