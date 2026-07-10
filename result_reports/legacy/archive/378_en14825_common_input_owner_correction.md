# 378 EN14825 Common Input Owner Correction

## Goal

Move EN14825 common inputs to the EN14825 tab owner so SEER/SCOP share the same
Pto/Psb/Pck/Poff and appliance type values across nested tab switches.

## Scope / Non-goals

- Scope: EN14825 tab common input panel, SEER/SCOP common value provider wiring,
  focused tests, `WORK_PLAN` next-action update.
- Non-goals: SCOP result surface UX correction, result panel placement,
  Declared/Tested result array changes, new card UI/framework, climate card
  component split, adapter/table model/model changes, input mapper/result
  formatter changes, `MetricInputTable`/`ResultPanel` changes, core/config,
  fixture/golden changes, workflow docs, memory/project log, lifecycle cleanup,
  or manual GUI smoke.

## Common Input Owner Boundary

- `En14825Tab` now owns the single common input set:
  - `Pto [W]`
  - `Psb [W]`
  - `Pck [W]`
  - `Poff [W]`
  - `기기 유형` with `reversible` / `heating_only`
- SEER and SCOP sections no longer create or own those `StringVar` instances or
  input widgets.
- SEER keeps Pdesignc/Tdesignc/Cd locally.
- SCOP keeps Cd and climate-specific Pdesignh/Tbiv/TOL locally.

## SEER / SCOP Calculation Wiring

- Sections receive a `common_input_values` provider from the EN14825 tab.
- SEER reads Pto/Psb/Pck/Poff from the provider and ignores appliance type.
- SCOP reads Pto/Psb/Pck/Poff plus appliance type from the provider.
- Common input changes schedule recalculation for both sections.

## MVC/SoC Judgment

The EN14825 tab owns cross-section product/test inputs and composition wiring.
SEER/SCOP sections remain section-local widget/table/calculation glue. Existing
adapter/model/helper boundaries are unchanged.

## Behavior Preservation

- Existing standalone SEER/SCOP section construction still works through default
  zero common-input providers.
- Existing SEER/SCOP focused integration behavior remains covered.
- Nested SEER/SCOP tab switching preserves common values because the variables
  live in the parent EN14825 tab.

## Tests

- Added/updated focused tests confirming:
  - EN14825 tab owns one common input set and sections do not own duplicate
    `_p_to_var` or SCOP `_appliance_type_var`;
  - common values survive SEER/SCOP tab switching;
  - SEER calculation reads common auxiliary values;
  - SCOP calculation reads common auxiliary values and appliance type;
  - existing EN14825 SEER/SCOP focused tests pass.

## Validation

- `python3 -B -m py_compile apps/calculator/ui/tabs/en14825_tab.py` OK.
- `python3 -B -m py_compile apps/calculator/ui/sections/en14825_seer_section.py` OK.
- `python3 -B -m py_compile apps/calculator/ui/sections/en14825_scop_section.py` OK.
- `python3 -B -m pytest tests/test_apps_calculator_ui_en14825.py -q` OK, 17 passed.
- `python3 -B -m pytest tests/test_apps_calculator_ui_en14825_scop.py -q` OK, 23 passed.
- `python3 -B tools/check_code_structure.py` OK with one accepted soft LOC warning.
- `git diff --check` OK.
- `git status --short` showed only scoped source/test/docs/report changes before commit.
- `find result_reports/active -maxdepth 1 -type f -name '*.md' | wc -l` OK; exact count is reported only in terminal output.

## Structure Warnings / Warning Triage

- Structure Warnings: existing
  `apps/calculator/ui/sections/en14825_scop_section.py` 400 LOC soft warning
  remains, now 407 LOC.
- Warning Triage: accepted for this slice with reason. This correction removed
  duplicated common inputs from the sections and moved ownership upward; it did
  not add calculation/mapping/result formatting responsibility to SCOP.

## Known Risks / Gaps

- SCOP result surface UX correction remains intentionally separate.
- Active report lifecycle cleanup remains a separate follow-up because this task
  does not move summary/archive files.

## Next Suggested Action

Perform EN14825 SCOP result surface UX correction as the next active slice.

## Project Memory Delta

- none

## Commit / Push

- Source/test and docs/report commits are separated when practical.
- Final commit hashes and push status are reported in terminal output to avoid a
  self-referential report update loop.
