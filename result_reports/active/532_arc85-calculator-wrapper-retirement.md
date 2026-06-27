# 532 - Arc 8.5 Calculator Wrapper Retirement

## Goal

Migrate active calculator callers to `core.calculators.*` owner paths and delete
root calculator compatibility wrappers.

## Migrated Callers

- `apps/calculator/ui/**`
  - Dispatcher callers now use `core.calculators.dispatcher`.
  - EN14825 UI adapters now use `core.calculators.standards.en14825`.
- `tests/**`
  - Dispatcher/profile/adapter/standard-engine imports now use
    `core.calculators.*` owner paths.
- `core/_legacy/calculator_iso16358_legacy.py`
  - KS dependency now imports from `core.calculators.standards.ks_c9306` so the
    legacy module remains importable without a root wrapper.
- `core/calculator_result_adapter.py`
  - Profile resolver dependency now imports from `core.calculators.profiles`.
- Current docs/examples:
  - Updated active architecture/design references from root calculator wrapper
    paths to owner paths where they describe current routing.

## Deleted Root Calculator Wrappers

- `core/calculator_dispatcher.py`
- `core/calculator_profiles.py`
- `core/calculator_input_adapter.py`
- `core/calculator_prediction_adapter.py`
- `core/calculator_unit_adapter.py`
- `core/calculator_iso16358.py`
- `core/calculator_ks_c9306.py`
- `core/calculator_en14825.py`
- `core/calculator_ahri_seer2.py`
- `core/calculator_ahri_hspf2.py`
- `core/calculator_asnzs_hspf_excel.py`

## Deferred To Slice 4

- `core/calculator_result_adapter.py`
- `core/calculator_ranking_adapter.py`

These are not compatibility wrappers; they are flat root calculator-adjacent
adapters that require move/rename to
`core/calculators/adapters/result_adapter.py` and
`core/calculators/adapters/ranking_adapter.py`.

## Validation

- `python3 -B -m py_compile core/calculators/*.py core/calculators/adapters/*.py core/calculators/standards/*.py app_calculator.py`
  - Result: passed.
- Calculator profile creation smoke for KS, ISO/Hong Kong, AHRI, and EN14825:
  - Result: passed.
- Standard engine owner import smoke:
  - Result: passed.
- Root calculator wrapper file absence guard:
  - Result: passed for Slice 3 delete targets.
- Active-tree root calculator search with `docs/archive/**` excluded:
  - Result: only Slice 4 result/ranking adapter references remain.
- Prompt-pattern search without excluding `docs/archive/**`:
  - Result: historical archive hits remain in `docs/archive/**` and are left
    untouched.
- `git diff --check`
  - Result: passed.
- `git status --short`
  - Result: expected Slice 3 changes before commit.

## Excluded

- No calculator formula, config, fixture, golden, public result key, schema, or
  PySide6 recovery changes.
- No generated code map refresh in this slice; code map refresh is deferred to
  Slice 5.
- No archive/history document edits.

## Next

Slice 4 - Move flat calculator result/ranking adapters and delete the root
files.
