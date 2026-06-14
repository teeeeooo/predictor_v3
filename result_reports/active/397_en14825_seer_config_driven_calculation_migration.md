# 397 EN14825 SEER config-driven calculation migration

## Goal

Move EN14825 SEER calculation reads from core module constants to
`self.seer_config` while preserving current SEER/SCOP behavior.

## Scope

- Updated SEER helper paths in `core/calculator_en14825.py`.
- Added focused tests proving unified config values affect SEER calculation.
- Kept module constants as legacy fallback data for SCOP-only config loading.
- Updated compact EN14825 notes and WORK_PLAN next action.

## Non-goals

- Did not edit `data/region_configs/en14825.json`, `eu.json`, or
  `en14825_scop.json`.
- Did not modify SCOP calculation behavior.
- Did not implement SCOP Warmer A inactive point handling, TOL/Tbiv duplicate
  mapping, or EN14825 batch behavior.
- Did not change golden expected values.

## SEER Config-driven Migration

- `_build_cooling_eerpl_points()` now reads A/B/C/D temperatures from
  `self.seer_config["test_point_temps"]`.
- `_calculate_seer_on()` now reads cooling bin temperatures and hours from
  `self.seer_config["bin_data"]`.
- `_get_seer_operational_hours()` now reads appliance-type hours from
  `self.seer_config["operational_hours"]`.
- `calculate_seer()` now resolves omitted `t_design_c`, `cd`, and
  `appliance_type` from `self.seer_config` defaults.
- Explicit caller-provided values still take priority.

## Loader Compatibility

- Unified `en14825.json` continues to provide `seer` and `scop` sections.
- Legacy `en14825_scop.json` still synthesizes `self.seer_config` from module
  constants, so SEER calculation remains available for legacy constructor paths.
- `self.scop_config` was not changed.

## code_map_check

- Targeted pre-edit code_map check found `core/calculator_en14825.py` and
  EN14825 UI adapter references.
- Regenerated `docs/code_map/CODEBASE_REFERENCE_MAP.md`; change is limited to
  generation metadata and updated `core/calculator_en14825.py` LOC.

## Verification

- `python3 -B -m py_compile core/calculator_en14825.py` OK.
- `python3 -B -m pytest tests/test_en14825_golden.py -q` OK: 11 passed.
- `python3 -B tools/check_code_structure.py` OK with existing EN14825 UI section
  LOC soft warnings.
- `git diff --check` OK.
- `git status --short` reviewed before commit.

## Project Memory Delta

- Candidate: EN14825 SEER calculation now reads cooling bins, declared point
  temperatures, defaults, and operational hours from `self.seer_config`; module
  constants remain legacy fallback only.
