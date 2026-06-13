# 392 EN14825 SCOP LOC soft warning deferred check

## Goal

Check whether the `en14825_scop_section.py` LOC soft warning needs immediate
split work, without modifying source code.

## Scope

- Reviewed the current soft warning state for
  `apps/calculator/ui/sections/en14825_scop_section.py`.
- Inventoried current SCOP section responsibilities from the section file
  symbols and existing report evidence.
- Updated `docs/WORK_PLAN.md` so the next execution item is EN14825 batch
  integration preflight and the SCOP split remains deferred.

## Evidence

- `python3 -B tools/check_code_structure.py` exits OK and reports
  `en14825_scop_section.py` above the 400 LOC soft limit at 552 LOC.
- Summary 385 already records that SCOP section soft LOC warnings were triaged
  and that future SCOP UI responsibility additions should begin with a split
  audit.
- Report 387 preserved the same warning as accepted for that slice, with a
  follow-up to run split audit or extract subcomponents before adding more SEER
  or SCOP section UI responsibility.

## Responsibility Inventory

- Current SCOP section still owns stacked climate card construction, input
  table/controller wiring, climate toggles, recalculation scheduling, result
  card visibility, and widget lifecycle cleanup.
- Mapping, formatting, and result surface responsibilities are already routed
  through helper modules imported by the section:
  `en14825_scop_input_mapper`, `en14825_scop_result_formatter`, and
  `en14825_scop_result_surface`.
- This task adds no new SCOP card-level layout/refit responsibility.

## Decision

- Split implementation is not required now.
- A split audit is required before the next SCOP card-level layout/refit code
  slice or other meaningful SCOP section responsibility expansion.
- The accepted/deferred state remains valid, and execution can proceed to
  EN14825 batch integration preflight.

## Verification

- `python3 -B tools/check_code_structure.py` OK with soft LOC warnings for
  `en14825_seer_section.py` and `en14825_scop_section.py`.
- `git diff --check` OK.
- `git status --short` reviewed before commit.

## Scope Compliance

- Source code, tests, calculator logic, summaries, archive, and memory seed were
  not modified.

## Commit / Push

- Final commit hash and push status are reported in terminal output.
