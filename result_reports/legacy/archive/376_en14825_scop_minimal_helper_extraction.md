# 376 EN14825 SCOP Minimal Helper Extraction

## Goal

Extract non-widget SCOP input mapping and result formatting responsibilities
from `En14825ScopSection` before SCOP Slice 3.

## Scope / Non-goals

- Scope: SCOP-local result formatter, SCOP-local input mapper, section glue
  update, focused helper tests, `WORK_PLAN` next-action update.
- Non-goals: climate card subcomponent split, SCOP Slice 3, tab registration,
  core/config changes, `ScopAdapter`/`ScopTableModel`/`ScopModels` changes,
  `MetricInputTable` changes, common `ResultPanel` framework changes, hard guard
  changes, memory/project log/lifecycle changes.

## Extracted Helpers And Owner Boundaries

- `en14825_scop_result_formatter.py`
  - Owns `ScopResultSummary` + climate key to `ResultSummary` formatting.
  - Owns SCOP status-code display text mapping.
  - Does not import Tk or manipulate `ResultPanel`.
- `en14825_scop_input_mapper.py`
  - Owns table text dict parsing, invalid numeric field detection, and
    `ScopPointInput` mapping by `ScopTableModel.COL_KEYS`.
  - Takes text values, not `MetricInputTable` widgets.
- `En14825ScopSection`
  - Keeps widget construction, climate toggle handling, table/controller wiring,
    dynamic TOL/Tbiv header updates, static cell updates, cell background
    resolving, scheduler lifecycle, and parent refit signal.

## MVC/SoC Judgment

The section is now thinner glue for widget and lifecycle concerns. Mapping and
result formatting are testable outside Tk, while adapter/table model/model
owners keep their existing boundaries.

## Behavior Preservation

The section still reads the same table text, sets invalid fields on the same
widget, clears computed rows on invalid input, computes through the same
adapter/table model path, updates dynamic TOL/Tbiv headers, repaints controller
selection colors, and writes summaries to the same `ResultPanel`.

## Tests

- Added input mapper tests for complete declared/tested values, declared-only
  blank tested values, and invalid numeric fields.
- Added formatter tests for complete/missing values and climate-local error
  summaries.
- Existing SCOP GUI integration test still passes.

## Validation

- `python3 -B -m py_compile apps/calculator/ui/sections/en14825_scop_section.py` OK.
- `python3 -B -m py_compile apps/calculator/ui/sections/en14825_scop_result_formatter.py` OK.
- `python3 -B -m py_compile apps/calculator/ui/sections/en14825_scop_input_mapper.py` OK.
- `python3 -B -m pytest tests/test_apps_calculator_ui_en14825_scop.py -q` OK, 22 passed.
- `python3 -B tools/check_code_structure.py` OK with one accepted soft LOC warning.
- `git diff --check` OK.
- `git status --short` showed only scoped source/test/docs/report changes before commit.
- `find result_reports/active -maxdepth 1 -type f -name '*.md' | wc -l` OK; exact count is reported only in terminal output.

## Structure Warnings / Warning Triage

- Structure Warnings: `apps/calculator/ui/sections/en14825_scop_section.py`
  remains above the 400 LOC soft limit after dropping from 486 LOC to 432 LOC.
- Warning Triage: accepted for this slice with reason.
- Reason: this slice removed the audited non-widget mapping/formatting
  responsibilities. Remaining weight is primarily widget/card construction,
  table wiring, lifecycle, and display update glue. Do not add mapping/result
  formatting back during Slice 3.

## Known Risks / Gaps

- The climate card subcomponent remains in the section. Revisit only if Slice 3
  needs meaningful card-level layout/refit ownership.
- Active report lifecycle cleanup remains a separate follow-up because this task
  does not move summaries/archive files.

## Next Suggested Action

Proceed to EN14825 SCOP Slice 3 tab composition layout refit polish, keeping
input mapping and result formatting in the new helpers.

## Project Memory Delta

- none

## Commit / Push

- Source/test commit and docs/report commit are separated when practical.
- Final commit hashes and push status are reported in terminal output to avoid a
  self-referential report update loop.
