# 399 EN14825 legacy config and fallback cleanup

## Goal

Remove legacy EN14825 config ownership and silent fallback paths after unified
`data/region_configs/en14825.json` became the active owner.

## Scope

- Deleted stale EN14825 legacy config files from active config tree.
- Changed `EN14825Calculator` constructor ownership from `scop_config_path` to
  `config_path`.
- Removed legacy SCOP-only schema compatibility from config loading.
- Removed SEER default fallback behavior from calculator calculation paths.
- Updated focused EN14825 golden/dispatcher tests, EN14825 notes, and WORK_PLAN.

## Non-goals

- Did not edit apps, batch, ML, profiles, memory, summaries, archive, or project
  log.
- Did not change `data/region_configs/en14825.json` values.
- Did not implement SCOP UI readonly/blank behavior.
- Did not change golden expected values.

## Deleted Configs

- `data/region_configs/eu.json`
- `data/region_configs/en14825_scop.json`

These files are preserved by git history and prior result reports, not by active
config tree copies.

## Constructor Cleanup

- `EN14825Calculator.__init__` now accepts `config_path: str = None`.
- Default path remains `data/region_configs/en14825.json`.
- Runtime attribute is now `self.config_path`.
- No `scop_config_path` alias is retained.
- Dispatcher/profile construction continues to pass the profile `config_path`
  positionally and resolves to the unified config.

## Fallback Cleanup

- `_split_config` now requires both top-level `seer` and `scop` sections.
- Legacy SCOP-only config shape no longer loads.
- `_default_seer_config()` was removed.
- `_get_scop_point_contract()` now requires `scop.point_contract` in config.
- SEER design/default/bin/operational-hour values are read from `self.seer_config`
  and missing required keys fail fast with `ValueError`.
- SCOP default `degradation_coefficient` and `appliance_type` are required from
  `self.scop_config["defaults"]` when omitted by caller.
- `T_DESIGN_C` and `CD_DEFAULT` remain only as existing UI compatibility exports
  because current apps import them and apps are outside this task scope; they are
  not used as calculator fallback/default sources.

## Tests

- Removed legacy config compatibility test coverage.
- Updated focused tests to assert `config_path`.
- Existing SEER/SCOP golden expectations passed unchanged.
- Dispatcher EN14825 profile smoke tests passed with unified config path.

## code_map_check

- Targeted pre-edit check searched EN14825Calculator, config path, config owner,
  and legacy config references.
- Regenerated `docs/code_map/CODEBASE_REFERENCE_MAP.md` after structure check
  reported stale map metadata; changes are generation metadata and updated
  `core/calculator_en14825.py` LOC/function length evidence.

## Verification

- `python3 -B -m py_compile core/calculator_en14825.py` OK.
- `python3 -B -m pytest tests/test_en14825_golden.py tests/test_calculator_dispatcher.py`
  OK: 31 passed.
- `python3 -B tools/check_code_structure.py` OK with existing EN14825 UI section
  LOC soft warnings.
- `git diff --check` OK.
- `git status --short` reviewed before commit.

## Project Memory Delta

- EN14825 active config ownership is now single-file unified config:
  `data/region_configs/en14825.json`.
- Legacy EN14825 config files were removed from active tree.
- EN14825 calculator constructor is `config_path` only; `scop_config_path` is not
  supported.

## Next Action

EN14825 SCOP UI point availability correction.
