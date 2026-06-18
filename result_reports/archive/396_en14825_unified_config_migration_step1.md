# 396 EN14825 unified config migration Step 1

## Goal

Create the unified EN14825 config owner and migrate EN14825 profile loading to it
without changing SEER/SCOP calculation behavior.

## Scope

- Created `data/region_configs/en14825.json` with top-level metadata and separate
  `seer` / `scop` sections.
- Moved existing SEER/cooling config-like data into `seer`, including current
  core operational hours for `reversible` and `cooling_only`.
- Moved existing SCOP/heating data into `scop`.
- Updated `EN14825Calculator` loading so unified config and legacy SCOP-only
  config are both accepted.
- Updated EN14825 profile paths to the unified config.
- Updated focused profile/dispatcher/calculator tests and compact EN14825 notes.

## Non-goals

- Did not delete, rename, or edit `eu.json` or `en14825_scop.json`.
- Did not make `calculate_seer()` fully config-driven.
- Did not implement SCOP Warmer A inactive point behavior.
- Did not implement EN14825 batch behavior.
- Did not change golden expected values.

## Config Migration

- New owner: `data/region_configs/en14825.json`.
- Root metadata remains minimal: `standard`, `source`, and `unit_system`.
- `seer` owns cooling design data, A/B/C/D test point temperatures, Table 36 bin
  data, current SEER operational hours, and default Cd/appliance type.
- `scop` owns heating test point schema, climate data, operational hours,
  defaults, and source metadata copied from the legacy SCOP config.
- Mode-specific keys are namespaced; no cooling/heating semantic merge was done
  at top level.

## Loader Compatibility

- Unified schema:
  - `self.config = loaded_config`
  - `self.seer_config = loaded_config["seer"]`
  - `self.scop_config = loaded_config["scop"]`
- Legacy SCOP-only schema:
  - `self.scop_config = loaded_config`
  - `self.seer_config` is synthesized from current module constants.
- `self.scop_config` and constructor argument compatibility are preserved for
  existing UI adapter behavior.

## Profile Paths

- `en14825_scop` now points to `data/region_configs/en14825.json`.
- `en14825_seer` now points to `data/region_configs/en14825.json`.
- Other profiles were not changed.

## code_map_check

- Targeted pre-edit code_map check found EN14825 core/UI references but no
  existing `en14825.json` entry.
- Regenerated `docs/code_map/CODEBASE_REFERENCE_MAP.md` because core loader helper
  symbols and source LOC changed.

## Verification

- `python3 -m json.tool data/region_configs/en14825.json >/dev/null` OK.
- Config parity check OK: `scop` matches legacy `en14825_scop.json`; `seer`
  values match migrated `eu.json` data plus current core operational hours.
- `python3 -B -m py_compile core/calculator_en14825.py core/calculator_profiles.py` OK.
- `python3 -B -m pytest tests/test_en14825_golden.py tests/test_calculator_profiles.py tests/test_calculator_dispatcher.py -q` OK: 49 passed.
- `python3 -B tools/check_code_structure.py` OK with existing EN14825 UI section
  LOC soft warnings.
- `git diff --check` OK.
- `git status --short` reviewed before commit.

## Project Memory Delta

- Candidate: EN14825 config owner is now `data/region_configs/en14825.json` with
  namespaced `seer` and `scop` sections; legacy SCOP-only config remains loader
  compatible.
