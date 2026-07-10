# 511 Prediction Controller Foundation

## Goal

Add a small controller boundary between PredictWorkspace and prediction
adapter/service layers without letting UI widgets or table models call core ML.

## Scope

- Added `PredictionController`.
- Added `PredictionRunSummary`.
- Controller supports all rows and explicit case-id lists.
- Controller validates rows through `RowToMlInputAdapter`.
- Invalid rows become row-level `invalid` results without model execution.
- Valid rows go through `PredictionService`.
- Service outcomes are converted through `PredictionResultAdapter` and written
  to `PredictSession`.

## Changed Files

- `apps/predict/controllers/__init__.py`
- `apps/predict/controllers/prediction_controller.py`
- `result_reports/active/511_prediction-controller-foundation.md`

## Verification

- `python3 -B -m py_compile apps/predict/controllers/*.py apps/predict/adapters/*.py apps/predict/services/*.py apps/predict/state/*.py` - passed.
- `python3 -B -c "from apps.predict.controllers import *"` - passed.
- Controller invalid-row smoke - passed.
- `rg -n "from ui\\.|import ui\\.|ui\\.predict_window|ui\\.train_window|QTableWidget|traceback\\.print_exc" apps/predict apps/train app_predict.py app_train.py` - no matches.
- `python3 -B tools/check_code_structure.py` - passed with pre-existing
  calculator soft-limit warnings and code-map freshness warning.
- `git diff --check` - passed.
- `git status --short` - checked.

Skipped:

- pytest: focused compile/import/controller smoke covered this slice.
- GUI smoke: controller is Qt-free and workspace integration happens in Slice 4.

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

- `apps/predict/adapters/row_to_ml_input_adapter.py`: input validation boundary.
- `apps/predict/services/prediction_service.py`: core prediction call boundary.
- `apps/predict/adapters/prediction_result_adapter.py`: result conversion
  boundary.
- `docs/architecture/pyside6_train_predict_architecture.md`: controller and
  worker boundary expectations.

## Worker / Long-running Judgment

- No worker was added in this controller slice.
- The controller remains Qt-free and can be called from a later worker without
  changing service or adapter contracts.
- Full production large-batch execution should receive a worker/progress slice
  before treating synchronous execution as complete. Slice 4 may wire the
  foundation flow, but must report this gap if no worker is added.

## Known Risks

- Local model artifact is absent, so only invalid-row and model-load-error paths
  can be smoke-tested locally.
- Changed/dirty-row execution scope remains a follow-up.

## Commit / Push

Commit is performed for this slice. Push is performed after Arc closeout.
