# 379 EN14825 Common Input Placement Terminology Correction

## Goal

Keep EN14825 common input ownership in `En14825Tab` while making the inputs feel
visually attached to the selected SEER/SCOP page, and align SEER/SCOP wording.

## Scope / Non-goals

- Scope: common input panel placement, SEER/SCOP section title terminology,
  SCOP condition/toggle wording, focused tests, and `WORK_PLAN` checkpoint.
- Non-goals: SCOP result surface UX correction, result panel right-side layout,
  Declared/Tested 2-row result arrangement, editable Tdesignh input, new card UI,
  shared card framework, climate card component split, adapter/model/helper
  changes, `ResultPanel`/`MetricInputTable` changes, core/config, fixture/golden,
  workflow docs, memory/project log, lifecycle cleanup, or manual smoke.

## Common Input Placement

- `En14825Tab` still owns the single common `StringVar` set for
  Pto/Psb/Pck/Poff and appliance type.
- The common input panel is now created as the first visible block inside each
  SEER/SCOP notebook page, using the same tab-owned variables.
- SEER/SCOP tab switches keep common values because the values remain owned by
  the parent tab.

## Terminology Changes

- SEER section title changed from `SEER Comparison (EN 14825)` to `SEER`.
- SCOP section title changed from `SCOP Comparison (EN 14825)` to `SCOP`.
- SCOP `기본 사양 (Base Specs)` changed to `설계 사양`.
- SCOP climate card titles changed to `Average 조건`, `Warmer 조건`, and
  `Colder 조건`.
- SCOP climate toggle text changed to `활성화`.

## MVC/SoC Judgment

Common input state remains in the EN14825 tab owner. Sections still consume a
provider and keep section-local inputs only. This is a presentation/wording
correction without moving calculation, mapping, adapter, model, or result
formatter responsibilities.

## Behavior Preservation

- Common input values still persist across SEER/SCOP tab switches.
- Existing provider-based SEER/SCOP calculation wiring is unchanged.
- SCOP Average/Warmer/Colder LabelFrame structure is unchanged apart from
  display text.

## Tests

- Updated focused tests to assert:
  - SEER/SCOP nested tab labels remain `SEER` and `SCOP`;
  - common inputs remain owned by `En14825Tab`;
  - common input panel is the first visible block in both SEER and SCOP pages;
  - SEER/SCOP section titles no longer contain duplicated comparison wording;
  - SCOP condition labels and toggle text use the corrected strings.

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
  remains at 407 LOC.
- Warning Triage: accepted for this slice with reason. This task changed only
  placement/terminology and did not add SCOP mapping, formatting, calculation,
  or card component responsibility.

## Known Risks / Gaps

- SCOP result surface UX correction remains the next separate slice.
- Tdesignh remains non-editable; a read-only display can be considered later if
  useful, without changing adapter/config/core ownership.
- Manual GUI smoke was intentionally not run in this task.
- Active report lifecycle cleanup remains a separate follow-up because this task
  does not move summary/archive files.

## Next Suggested Action

Proceed with EN14825 SCOP result surface UX correction.

## Project Memory Delta

- none

## Commit / Push

- Source/test and docs/report commits are separated when practical.
- Final commit hashes and push status are reported in terminal output to avoid a
  self-referential report update loop.
