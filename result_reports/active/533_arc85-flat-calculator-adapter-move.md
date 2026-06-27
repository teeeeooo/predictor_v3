# 533 - Arc 8.5 Flat Calculator Adapter Move

## Goal

Move the remaining flat root calculator-adjacent adapters under
`core/calculators/adapters/` and delete the root files.

## Moved

- `core/calculator_result_adapter.py`
  -> `core/calculators/adapters/result_adapter.py`
- `core/calculator_ranking_adapter.py`
  -> `core/calculators/adapters/ranking_adapter.py`

## Migrated Callers

- `tests/test_calculator_result_adapter.py`
- `tests/test_calculator_ranking_adapter.py`
- `tests/test_calculator_envelope_chain.py`
- `tests/test_calculator_schema_boundaries.py`
- Current design reference:
  `docs/designs/2026-05-17-calculator-result-envelope-ml-adapter.md`

## Validation

- `python3 -B -m py_compile core/calculators/adapters/*.py`
  - Result: passed.
- `python3 -B -c "from core.calculators.adapters.result_adapter import wrap_calculator_result_envelope; from core.calculators.adapters.ranking_adapter import build_ranking_candidate_envelope"`
  - Result: passed.
- `rg -n "calculator_result_adapter|calculator_ranking_adapter" apps core tests scripts ui docs --glob '!result_reports/archive/**'`
  - Result: only historical hits in `docs/archive/**`; left untouched.
- `test ! -f core/calculator_result_adapter.py && test ! -f core/calculator_ranking_adapter.py`
  - Result: passed.
- `git diff --check`
  - Result: passed.
- `git status --short`
  - Result: expected Slice 4 move changes before commit.

## Excluded

- No calculator formula, config, fixture, golden, public result key, ML
  behavior, PySide6 recovery, or ranking feature behavior changes.
- No archive/history document edits.

## Next

Slice 5 - Focused tests and root-wrapper absence guard.
