# 398 EN14825 SCOP point contract core/config

## Goal

Implement the EN14825 SCOP point contract in unified config and core, without
changing public result keys or existing golden expected values.

## Scope

- Added `scop.point_contract` to `data/region_configs/en14825.json`.
- Added core resolver support for active, required, mapped, and inactive SCOP
  logical points.
- Updated SCOP validation/build/curve construction to use resolver output.
- Added focused core tests for Warmer A inactive behavior, TOL/Tbiv mapping, and
  Average/Colder required-point behavior.
- Updated compact EN14825 notes and WORK_PLAN next action.

## Non-goals

- Did not edit UI, batch, ML, profiles, legacy config files, memory, summaries,
  archive, or project log.
- Did not implement SCOP UI readonly/blank behavior.
- Did not implement EN14825 batch behavior.
- Did not change golden expected values.

## Point Contract

- Config owner: `data/region_configs/en14825.json` `scop.point_contract`.
- `standard_points`: A/B/C/D.
- `conditional_points`: TOL/Tbiv.
- Warmer active standard points: B/C/D; A is inactive.
- Average and Colder active standard points: A/B/C/D.
- Duplicate temperature policy: standard point value is source.
- Conditional points below the first useful nonzero-bin interpolation segment are
  not required as independent curve inputs.

## Resolver

- `_resolve_scop_point_contract(...)` resolves:
  - active standard points;
  - required independent input points;
  - mapped logical points;
  - inactive points;
  - resolved logical point temperatures;
  - canonical curve point keys.
- Legacy `en14825_scop.json` loading synthesizes the same default contract.

## Mapping Behavior

- Warmer A is not required for core calculation.
- Warmer `Tbiv = 2°C` maps to point B.
- Warmer `TOL < 2°C` is retained as threshold temperature but not required as a
  curve input when it is below the first useful nonzero-bin segment.
- Average/Colder keep A as required.
- Average `TOL = -11°C` remains an independent required input because it is
  needed for interpolation to the first nonzero bin.
- Capacity and COPPL curves now use the same canonical curve point set for
  duplicate temperatures.

## Golden Delta

- None. Existing SCOP golden expected values passed unchanged.

## code_map_check

- Targeted pre-edit code_map check found EN14825 calculator references but no
  specific point-contract entry.
- Regenerated `docs/code_map/CODEBASE_REFERENCE_MAP.md`; change is limited to
  generation metadata and updated `core/calculator_en14825.py` LOC.

## Verification

- `python3 -B -m py_compile core/calculator_en14825.py` OK.
- `python3 -B -m pytest tests/test_en14825_golden.py` OK: 17 passed.
- `python3 -B tools/check_code_structure.py` OK with existing EN14825 UI section
  LOC soft warnings.
- `git diff --check` OK.
- `git status --short` reviewed before commit.

## Project Memory Delta

- Candidate: EN14825 SCOP point availability is now governed by
  `scop.point_contract`; Warmer A is inactive and duplicate TOL/Tbiv temperatures
  map to the active standard point value in core.
