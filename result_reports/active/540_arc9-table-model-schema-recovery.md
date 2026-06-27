# 540 Arc 9 Table Model Schema Recovery

## Goal

Move PySide6 `InputTableModel` and `ResultTableModel` from local mock column
definitions to the core-driven Predict schema adapter.

## Changes

- `InputTableModel` now uses `build_input_column_schema()`.
- `ResultTableModel` now uses `build_result_column_schema()`.
- Removed local `InputColumn` / `INPUT_COLUMNS` and `ResultColumn` /
  `RESULT_COLUMNS` definitions from table models.
- Added schema-driven editability, headers, result display, and background
  roles.
- Allowed table models to be created with an optional `PredictSession` for
  focused import/smoke tests.
- Added focused table model tests in
  `tests/test_apps_predict_table_models.py`.
- Hardened the schema adapter Qt-free test by running it in an isolated Python
  subprocess.

## Boundary Decision

- Table models display state only and do not call mapping repositories,
  prediction services, or ML adapters.
- Result lookup remains `case_id` based through `PredictSession.case_order` and
  `PredictSession.result_for_case()`.
- Result table visible columns are the core predictor `RESULT_COLS`; row-level
  `status` and `message` stay in `ResultRow` state for controller/status
  handling rather than local table schema.

## UI/UX Contract Check

- Row headers remain the user-facing row identity.
- Input/result split-table layout, selection sync, scroll sync, and
  variable-size row lifecycle are preserved.
- Intentionally deferred table parity gaps: TSV copy, TSV paste,
  Delete/Backspace clear, grouped undo, Tab/Enter navigation,
  click/type replace-on-type, and validation rendering.

## Verification

- `python3 -B -m py_compile apps/predict/**/*.py`
- `python3 -B -c "from PySide6.QtWidgets import QApplication; import os; os.environ.setdefault('QT_QPA_PLATFORM','offscreen'); app=QApplication.instance() or QApplication([]); from apps.predict.ui.workspace import PredictWorkspace; w=PredictWorkspace(); assert w is not None"`
- `python3 -B -c "from apps.predict.ui.tables.input_table_model import InputTableModel; from apps.predict.schema.column_schema_adapter import build_predict_column_schema; m=InputTableModel(); assert m.columnCount() > 0; assert m.columnCount() <= len(build_predict_column_schema())"`
- `python3 -B -m pytest tests/test_apps_predict_schema_adapter.py tests/test_apps_predict_table_models.py`
- `git diff --check`
- `git status --short`

## Excluded Scope

- No mapping/autofill implementation in this slice.
- No row-to-ML/result adapter rewrite in this slice.
- No worker/progress/cancel implementation.
- No ML algorithm, model artifact, mapping JSON schema, calculator, fixture, or
  golden changes.

## Next Action

Arc 9 Slice 4 - Mapping repository and autofill recovery.
