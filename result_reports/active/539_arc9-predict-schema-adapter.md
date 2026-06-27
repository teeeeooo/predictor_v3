# 539 Arc 9 Predict Schema Adapter

## Goal

Create a Qt-free PySide6 Predict schema adapter from the core predictor schema
owner and prepare table/result adapters to stop carrying local column metadata.

## Changes

- Added `apps/predict/schema/column_schema_adapter.py`.
- Added `apps/predict/schema/__init__.py`.
- Added focused schema adapter tests in
  `tests/test_apps_predict_schema_adapter.py`.
- Added minimal core schema metadata in `core/predictor_schema/columns.py`:
  - `cooling_capa` -> `Cooling Capa`
  - `heating_capa` -> `Heating Capa`
  - ML result targets for cooling/heating power, refrigerant quantity, and
    cooling/heating Hz result columns.

## Boundary Decision

- The schema adapter is Qt-free and reads from
  `core.predictor_schema.columns`.
- Column order, keys, headers, and grouping remain owned by
  `core/predictor_schema/columns.py`.
- The added metadata does not change the ML feature list, target list,
  preprocessing formula, model artifact, mapping JSON schema, or public
  calculator contracts.
- Table models and prediction services still do not import each other.

## UI/UX Contract Check

- Table surfaces remain governed by the toolkit-neutral spreadsheet contract.
- This slice adds schema metadata only; TSV copy/paste, clear, undo, navigation,
  and validation rendering remain table UX parity gaps for a later dedicated
  table slice.

## Verification

- `python3 -B -m py_compile apps/predict/schema/*.py apps/predict/ui/tables/*.py apps/predict/state/*.py`
- `python3 -B -c "from apps.predict.schema.column_schema_adapter import build_predict_column_schema; schema=build_predict_column_schema(); assert schema; assert any(c.group == 'input' for c in schema)"`
- `python3 -B -c "from core.predictor_schema.columns import COLUMNS; from apps.predict.schema.column_schema_adapter import build_predict_column_schema; assert len(build_predict_column_schema()) == len(COLUMNS)"`
- `python3 -B -m pytest tests/test_apps_predict_schema_adapter.py`
- `git diff --check`
- `git status --short`

## Excluded Scope

- No root compatibility wrapper recreation.
- No ML algorithm, feature list, target list, preprocessing formula, model
  artifact, mapping JSON schema, calculator formula/config/fixture/golden, or
  public result contract changes.
- No worker/progress/cancel implementation.
- No Trainer foundation implementation.

## Next Action

Arc 9 Slice 3 - InputTableModel / ResultTableModel schema recovery.
