# 528 - Arc 8 Focused Tests, Caller Classification, Code Map Refresh

## Goal

Validate the calculator package restructure after moving dispatcher/profile/adapter and standard-engine ownership under `core/calculators/`, classify remaining root compatibility callers, and refresh the code map after the Arc 8 structure moves.

## Changes

- Corrected the direct `EN14825Calculator()` default config lookup after the standard engine move so it continues to resolve the existing `data/region_configs/en14825.json` SSOT from the repository root.
- Updated moved prediction adapter docstrings from root compatibility module paths to the new `core.calculators.adapters.*` owner paths.
- Regenerated `docs/code_map/CODEBASE_REFERENCE_MAP.md` after the calculator package move.

## Caller Classification

- `core/calculators/*` owner modules no longer import or document root `core.calculator_*` compatibility paths.
- Root `core.calculator_*` callers remain in apps and tests as compatibility callers. They are intentionally left in place for transition safety and public import compatibility.
- `core/calculator_result_adapter.py` and `core/calculator_ranking_adapter.py` remain root modules in this slice; they are not part of the dispatcher/profile/standard-engine move.
- Legacy references under `core/_legacy/` and `tests/_legacy/` remain historical/legacy context.

## Validation

- `python3 -B -m pytest tests/test_calculator_dispatcher.py tests/test_calculator_profiles.py tests/test_en14825_golden.py tests/test_ahri_seer2_smoke.py tests/test_ahri_hspf2_smoke.py tests/test_ahri_hspf2_v3_smoke.py tests/test_iso16358_hspf_smoke.py tests/test_iso16358_cspf_iso_t1_default_golden.py tests/test_iso16358_hspf_official_exact_golden.py tests/test_iso16358_cspf_hong_kong_config.py tests/test_iso16358_hspf_hong_kong_config.py tests/test_calculator_input_adapter.py tests/test_calculator_prediction_adapter.py tests/test_calculator_unit_adapter.py`
  - Result: 167 passed.
- `python3 -B -m py_compile core/*.py core/calculators/*.py core/calculators/adapters/*.py core/calculators/standards/*.py app_calculator.py app_predict.py app_train.py`
  - Result: passed.
- `python3 -B -c "import core.calculator_dispatcher; import core.calculators.dispatcher; import core.calculator_profiles; import core.calculators.profiles"`
  - Result: passed.
- `python3 -B -c "from core.calculators.dispatcher import create_calculator_for_profile; profiles=['ks_c9306_cspf','ks_c9306_hspf','iso_t1_default_2point_cspf','hong_kong_cspf','hong_kong_hspf','ahri_usa_seer2','ahri_usa_hspf2','en14825_seer','en14825_scop']; [create_calculator_for_profile(profile_id=p) for p in profiles]"`
  - Result: passed.
- `python3 -B tools/check_code_structure.py`
  - Result: passed with existing soft warnings for large calculator/UI files.
- `python3 -B tools/code_checker/build_reference_map.py`
  - Result: refreshed code map.
- `python3 -B tools/code_checker/build_reference_map.py --check`
  - Result: fresh against current HEAD before commit; warning notes the expected uncommitted working tree and dirty generated-map metadata.
- `rg -n "core\\.calculator_|from core\\.calculator_|import core\\.calculator_" core/calculators`
  - Result: no owner-module root compatibility references.
- `git diff --check`
  - Result: passed.
- `git status --short`
  - Result: expected modified source/code-map files plus this report before commit.

## Excluded

- No formula, schema, fixture, golden, public API, model artifact, or dependency changes.
- No broad caller migration from root compatibility modules to new owner modules.
- No full pytest run.

## Next

Proceed to Arc 8 closeout docs/report and then push after the final closeout commit.
