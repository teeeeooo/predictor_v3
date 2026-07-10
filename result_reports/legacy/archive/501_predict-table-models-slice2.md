# 501 Predict Table Models Slice 2

## Goal

Add QAbstractTableModel skeletons for editable Input Cases and read-only
Prediction Results while keeping both models backed by the same PredictSession
and case order.

## Scope

- Added `InputTableModel` with local skeleton input/autofill column schema.
- Added `ResultTableModel` with local skeleton result column schema.
- `InputTableModel.setData()` updates values through `CaseStore`.
- `ResultTableModel` reads results by `case_id` through `PredictSession`.

## Changed Files

- `apps/predict/ui/tables/__init__.py`
- `apps/predict/ui/tables/input_table_model.py`
- `apps/predict/ui/tables/result_table_model.py`
- `result_reports/active/501_predict-table-models-slice2.md`

## Verification

- `python3 -B -m py_compile apps/predict/ui/tables/input_table_model.py apps/predict/ui/tables/result_table_model.py` - passed.
- `python3 -B -c "from apps.predict.state.predict_session import PredictSession; from apps.predict.ui.tables.input_table_model import InputTableModel; from apps.predict.ui.tables.result_table_model import ResultTableModel; s=PredictSession(); s.case_store.append_empty_rows(2); im=InputTableModel(s); rm=ResultTableModel(s); assert im.rowCount()==2 and rm.rowCount()==2"` - passed.
- `git diff --check` - passed.
- `git status --short` - checked.

Skipped:

- pytest: focused import/model smoke covered this slice.
- GUI smoke: table views are introduced in the next slice.

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

- `docs/architecture/pyside6_train_predict_architecture.md`: table model
  responsibilities and forbidden prediction/model calls.
- `apps/predict/state/predict_session.py`,
  `apps/predict/state/case_store.py`: session and row storage owner APIs.

Structure / code map judgment:

- Table models do not own row storage and do not call prediction, model loading,
  training, mapping, calculator, or legacy UI paths.
- Column schema is intentionally local to this skeleton slice and can move to a
  later adapter without changing `core/constants.py`.

## Known Risks

- Column lists are minimal skeleton columns, not the final ML column mapping.
- No QTableView, paste/export, sorting/filtering, or prediction execution was
  implemented.

## Commit / Push

Commit is performed for this slice. Push is performed after Arc closeout.
