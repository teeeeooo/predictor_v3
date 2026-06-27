# 521 Arc 7 Predictor Schema Move

## Goal

Move predictor column/schema ownership to `core/predictor_schema/columns.py`
without changing metadata or existing root imports.

## Moved Owner

- `core.predictor_schema.columns` now owns `COLUMNS`, column index constants,
  input/auto/result/dropdown groups, `DROPDOWN_TARGET`, and `NUM_ROWS`.

## Compatibility

- `core.constants` re-exports the moved predictor schema names for existing
  callers.
- `COLUMNS` remains the same object through root compatibility import.

## Excluded

- No column order, header, key, group, width, color, mapping, `ml_feature`, row
  count, UI behavior, ML behavior, mapping behavior, calculator behavior, data,
  model artifact, fixture, golden, or public API changes.

## Verification

- `python3 -B -m py_compile core/predictor_schema/*.py core/constants.py`: passed.
- Root/new schema identity smoke: passed.
- Column metadata presence smoke: passed.
- `git diff --check`: passed.
- `git status --short`: checked.

## Next Action

Slice 5 - Mapping package move.
