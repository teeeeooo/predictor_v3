# 526 Arc 8 Dispatcher / Profiles / Adapters Move

## Goal

Move calculator routing, profile registry, and adapter ownership under
`core/calculators/` while preserving root imports.

## Moved Owners

- `core.calculators.profiles`: `CalculatorProfile`,
  `list_calculator_profiles`, `resolve_calculator_profile`.
- `core.calculators.dispatcher`: `create_calculator_for_profile`.
- `core.calculators.adapters.input_adapter`: calculator input envelope helpers.
- `core.calculators.adapters.prediction_adapter`: predicted-points envelope
  helpers.
- `core.calculators.adapters.unit_adapter`: unit normalization helpers.

## Compatibility

- Root modules remain importable:
  - `core.calculator_profiles`
  - `core.calculator_dispatcher`
  - `core.calculator_input_adapter`
  - `core.calculator_prediction_adapter`
  - `core.calculator_unit_adapter`
- Profiles and dispatcher wrappers use explicit re-exports.
- Adapter wrappers use wildcard re-export because those modules expose several
  helper constants/functions and public surface preservation is safer than
  hand-copying symbol lists in this move-only slice.

## Excluded

- No standard engine moves in this slice.
- Dispatcher still imports standard engines from root compatibility paths until
  Slice 4.
- No calculator behavior/formula/config/fixture/golden/public result contract,
  ML, mapping schema, PySide6 recovery, worker/progress, Trainer, dependency,
  data/model artifact, or UI behavior changes.

## Verification

- `python3 -B -m py_compile core/calculators/*.py core/calculators/adapters/*.py core/calculator_profiles.py core/calculator_dispatcher.py core/calculator_input_adapter.py core/calculator_prediction_adapter.py core/calculator_unit_adapter.py`: passed.
- Root/new profiles identity smoke: passed.
- Root/new dispatcher identity smoke: passed.
- Root/new adapter import smoke: passed.
- `git diff --check`: passed.
- `git status --short`: checked.

## Next Action

Slice 4 - Calculator standard engines move.
