# 400 EN14825 UI import dependency cleanup

## Goal

Remove remaining SEER UI dependencies on core module constants so EN14825
defaults are owned by `data/region_configs/en14825.json`.

## Scope

- Removed `T_DESIGN_C` and `CD_DEFAULT` exports from
  `core/calculator_en14825.py`.
- Removed SEER UI imports of those core constants.
- Added `SeerAdapter.get_seer_defaults()` as the SEER UI default source.
- Updated `En14825SeerSection` initial `Tdesignc`, `Cd`, and `Type` values to
  come from adapter/config defaults.
- Kept `SeerTableModel` headless by requiring caller-provided `t_design_c`.
- Added focused UI tests for config-owned defaults.

## Non-goals

- Did not edit `data/region_configs/en14825.json`.
- Did not implement SCOP UI point availability behavior.
- Did not change layout, visual styling, batch, ML, profiles, memory, summaries,
  archive, or project log.
- Did not change golden expected values.

## Removed Exports

- `T_DESIGN_C`
- `CD_DEFAULT`

Active `apps`, `core`, and `tests` no longer reference these names.

## UI Default Source

- `SeerAdapter.get_seer_defaults()` reads:
  - `seer.design.t_design_c`
  - `seer.defaults.degradation_coefficient`
  - `seer.defaults.appliance_type`
- Missing config/default state fails fast with `ValueError`.
- `SeerAdapter.calculate(...)` reads config defaults only for omitted
  `t_design_c`, `cd`, or `appliance_type`; explicit caller values keep existing
  behavior.
- `En14825SeerSection` uses adapter defaults for initial design vars and numeric
  parse fallback values.

## Tests

- Added focused assertion that adapter defaults match unified config values.
- Added GUI-section assertion that initial SEER defaults come from adapter/config.
- Existing EN14825 golden tests passed unchanged.

## code_map_check

- Targeted pre-edit code_map check found SEER adapter/table-model import edges to
  core constants.
- Regenerated `docs/code_map/CODEBASE_REFERENCE_MAP.md`; updated map removes
  `T_DESIGN_C`/`CD_DEFAULT` import edges and refreshes LOC metadata.

## Verification

- `python3 -B -m py_compile core/calculator_en14825.py apps/calculator/ui/en14825/seer_adapter.py apps/calculator/ui/en14825/seer_table_model.py apps/calculator/ui/sections/en14825_seer_section.py`
  OK.
- `python3 -B -m pytest tests/test_en14825_golden.py` OK: 16 passed.
- `python3 -B -m pytest tests/test_apps_calculator_ui_en14825.py` OK: 19
  passed.
- Active dependency `rg` check for `T_DESIGN_C`/`CD_DEFAULT` in `apps core
  tests` returned no matches.
- `python3 -B tools/check_code_structure.py` OK with existing EN14825 UI section
  LOC soft warnings.
- `git diff --check` OK.
- `git status --short` reviewed before commit.

## Project Memory Delta

- EN14825 SEER UI defaults now flow from `SeerAdapter`/unified config, not core
  module constants.
- Core no longer exports `T_DESIGN_C` or `CD_DEFAULT`.

## Next Action

EN14825 SCOP UI point availability correction.
