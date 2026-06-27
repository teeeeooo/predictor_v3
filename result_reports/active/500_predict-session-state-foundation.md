# 500 Predict Session State Foundation

## Goal

Add the Qt-free variable-size state foundation for Arc 3 so table models do not
own row storage directly.

## Scope

- Added `CaseRow` for editable input/autofill row state and dirty tracking.
- Added `ResultRow` for result state linked by `case_id`.
- Added `CaseStore` for append/insert/remove/update/get operations and shared
  `case_order`.
- Added `PredictSession` to own `CaseStore`, result mapping, case order access,
  and summary counts.

## Changed Files

- `apps/predict/state/__init__.py`
- `apps/predict/state/case_row.py`
- `apps/predict/state/result_row.py`
- `apps/predict/state/case_store.py`
- `apps/predict/state/predict_session.py`
- `result_reports/active/500_predict-session-state-foundation.md`

## Verification

- `python3 -B -m py_compile apps/predict/state/case_row.py apps/predict/state/result_row.py apps/predict/state/case_store.py apps/predict/state/predict_session.py` - passed.
- `python3 -B -c "from apps.predict.state.predict_session import PredictSession; s=PredictSession(); s.case_store.append_empty_rows(3); assert len(s.case_store.case_order)==3"` - passed.
- `git diff --check` - passed.
- `git status --short` - checked.

Skipped:

- pytest: no focused tests were required for this skeleton state slice.
- GUI smoke: Qt-free state layer only.

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

- `docs/architecture/pyside6_train_predict_architecture.md`: PredictSession,
  table model, and case-order ownership contract.
- `apps/predict/ui/workspace.py`: existing placeholder state before Arc 3 UI
  slices.

Structure / code map judgment:

- New state files are Qt-free and stay under the `apps.predict` owner boundary.
- No common state abstraction was extracted because this state belongs only to
  PredictWorkspace ownership.
- Code-map freshness warning is known from prior slices; this slice records a
  checked judgment without regenerating the map.

## Known Risks

- Result statuses are placeholder strings for skeleton display only.
- No prediction execution, model loading, training, mapping update, or
  calculator integration was added.

## Commit / Push

Commit is performed for this slice. Push is performed after Arc closeout.
