# 510 Prediction Result Mapping Foundation

## Goal

Add the case_id-based result mapping foundation so prediction outcomes can be
stored in `PredictSession` and displayed by `ResultTableModel` without table
models knowing service details.

## Scope

- Added `PredictionResultAdapter`.
- Added `PredictSession` result set/clear helpers.
- Expanded `summary_counts()` with running/invalid status counts.
- Updated result table columns for core prediction targets.
- Added `ResultTableModel.refresh_case_id()` for row-scoped result updates.

## Changed Files

- `apps/predict/adapters/__init__.py`
- `apps/predict/adapters/prediction_result_adapter.py`
- `apps/predict/state/predict_session.py`
- `apps/predict/ui/tables/result_table_model.py`
- `result_reports/active/510_prediction-result-mapping-foundation.md`

## Verification

- `python3 -B -m py_compile apps/predict/adapters/*.py apps/predict/services/*.py apps/predict/state/*.py apps/predict/ui/tables/result_table_model.py` - passed.
- `python3 -B -c "from apps.predict.state.predict_session import PredictSession; from apps.predict.state.result_row import ResultRow; s=PredictSession(); rows=s.case_store.append_empty_rows(1); s.set_result(ResultRow(case_id=rows[0].case_id, status='complete', result_values={'power': 1.23})); assert s.result_for_case(rows[0].case_id).status == 'complete'"` - passed.
- `rg -n "None|Traceback|case_id" apps/predict/ui/tables/result_table_model.py apps/predict/ui/workspace.py` - checked. Hits are internal Python `None` returns, internal `case_id` lookup, and explicit conversion of `None` cell values to an empty string.
- `python3 -B tools/check_code_structure.py` - passed with pre-existing
  calculator soft-limit warnings and code-map freshness warning.
- `git diff --check` - passed.
- `git status --short` - checked.

Skipped:

- pytest: focused compile/session smoke covered this slice.
- GUI smoke: result mapping/state boundary only.

## Change Gate

```yaml
change_gate:
  new_source: small
  hotspot_delta: none
  code_map_check: checked
  ui_literal_exemption: none
  reuse_commonization: checked
  report_exemption: none
  read_ledger: included
```

Read Ledger:

- `apps/predict/services/prediction_service.py`: service result shape.
- `apps/predict/state/predict_session.py`: result ownership.
- `apps/predict/ui/tables/result_table_model.py`: display-only result model
  boundary.
- `docs/ui_ux/05_INPUT_MATRIX_AND_RESULT_SURFACE_RULES.md`: result surface
  absence/raw-traceback guidance.

## UI/UX Contract Check

- Result lookup remains internal `case_id` based.
- `case_id` is not displayed as a result table column.
- Missing result values display as blank strings, not the user-facing string
  `None`.
- Raw tracebacks are not generated or displayed by this mapping adapter.
- Numeric result values are formatted compactly before reaching
  `ResultTableModel`.

## Known Risks

- Result columns are target-level foundation columns and may need a later column
  schema adapter refinement.
- Successful prediction smoke is still blocked locally by missing
  `model/model.pkl`.

## Commit / Push

Commit is performed for this slice. Push is performed after Arc closeout.
