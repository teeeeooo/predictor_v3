# 525 Arc 8 Calculator Package Shell

## Goal

Create the Arc 8 calculator package boundary without moving implementation.

## Scope

- Added `core/calculators/` package shell.
- Added `core/calculators/standards/` owner boundary.
- Added `core/calculators/adapters/` owner boundary.
- Added target owner shell modules for profiles, dispatcher, input adapter,
  prediction adapter, and unit adapter.

## Changed Files

- `core/calculators/__init__.py`
- `core/calculators/profiles.py`
- `core/calculators/dispatcher.py`
- `core/calculators/standards/__init__.py`
- `core/calculators/adapters/__init__.py`
- `core/calculators/adapters/input_adapter.py`
- `core/calculators/adapters/prediction_adapter.py`
- `core/calculators/adapters/unit_adapter.py`
- `result_reports/active/525_arc8-calculator-package-shell.md`

## Excluded

- No implementation move in this slice.
- No calculator formulas, behavior, config, fixtures, golden files, public
  result contracts, PySide6 recovery, worker/progress, Trainer, ML, mapping
  schema, data/model artifact, dependency, or UI behavior changes.

## Verification

- `python3 -B -m py_compile core/calculators/*.py core/calculators/adapters/*.py core/calculators/standards/*.py`: passed.
- Calculator package owner import smoke: passed.
- `git diff --check`: passed.
- `git status --short`: checked.

## Next Action

Slice 3 - Calculator dispatcher / profiles / adapters move.
