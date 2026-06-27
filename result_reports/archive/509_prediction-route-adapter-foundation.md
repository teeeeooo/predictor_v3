# 509 Prediction Route Adapter Foundation

## Goal

Establish the first Qt-free prediction input adapter and prediction service
boundary for Arc 4 without changing core ML behavior.

## Scope

- Confirmed the existing prediction route:
  `core.predictor.load_model(MODEL_FILE)` and
  `core.predictor.predict_row(model_data, row_dict)`.
- Read legacy `ui.predict_window` only as reference evidence.
- Added `RowToMlInputAdapter` to convert `CaseRow` input/autofill values into a
  core predictor input request.
- Added structured row input outcomes for validation errors and warnings.
- Added `PredictionService` to wrap the existing core predictor route.
- Added row-level service result objects for complete/error outcomes.

## Changed Files

- `apps/predict/adapters/__init__.py`
- `apps/predict/adapters/row_to_ml_input_adapter.py`
- `apps/predict/services/__init__.py`
- `apps/predict/services/prediction_service.py`
- `result_reports/active/509_prediction-route-adapter-foundation.md`

## Verification

- `python3 -B -m py_compile apps/predict/adapters/*.py apps/predict/services/*.py apps/predict/state/*.py` - passed.
- `python3 -B -c "from apps.predict.state.predict_session import PredictSession; from apps.predict.adapters import *; from apps.predict.services import *"` - passed.
- `rg -n "from ui\\.|import ui\\.|ui\\.predict_window|ui\\.train_window|QTableWidget" apps/predict apps/train app_predict.py app_train.py` - no matches.
- `python3 -B tools/check_code_structure.py` - passed with pre-existing
  calculator soft-limit warnings and code-map freshness warning.
- `git diff --check` - passed.
- `git status --short` - checked.

Skipped:

- pytest: focused compile/import smoke covered this slice.
- GUI smoke: Qt-free adapter/service foundation only.

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

- `core/predictor.py`: existing `load_model`, `build_input_df`, and
  `predict_row` route.
- `core/constants.py`: `MODEL_FILE`, `BASE_FEATURES`, `TARGETS`, and current
  UI column metadata.
- `ui/predict_window.py`: legacy reference only for current route shape.
- `docs/architecture/pyside6_train_predict_architecture.md`: adapter/service
  boundary requirements.
- `docs/agent_workflows/UI_SURFACE_WORKFLOW.md` and related UI/UX contracts:
  acceptance/routing context for table/input/result surfaces.

## Route / Environment Notes

- Local `model/model.pkl` is absent, so `PredictionService` can report a
  row-level model-load error but no successful real prediction smoke was run.
- No fake/mock prediction result was added to the production path.
- Current Arc 3 input columns do not yet provide the full ML feature surface.
  The adapter validates required cooling capacity and maps supported fields,
  while missing model/data readiness is surfaced through row-level outcomes.

## Known Risks

- Mapping/autofill completeness remains limited until later column schema and
  mapping adapter work.
- Worker/progress handling is not implemented in this slice.

## Commit / Push

Commit is performed for this slice. Push is performed after Arc closeout.
