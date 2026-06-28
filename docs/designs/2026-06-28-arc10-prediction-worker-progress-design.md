# Arc 10 Prediction Worker / Progress Design

Date: 2026-06-28

## Purpose

Fix the Arc 10 owner boundary before implementation so prediction execution can
move off the UI thread without changing ML behavior, mapping schema,
calculator contracts, or the accepted Arc 9.5 unified case table UX.

## Current Flow

- `PredictWorkspace._run_prediction()` disables the run button and calls
  `PredictionController.run_all()` synchronously.
- `PredictionController.run_case_ids()` validates each row, writes invalid or
  running results to `PredictSession`, calls `PredictionService.predict_many()`,
  then records returned service results.
- `PredictionService` is Qt-free and wraps `core.ml.inference.load_model()` and
  `predict_row()`.
- `PredictWorkspace` currently owns direct model-file existence display through
  `MODEL_FILE` / `Path`, and mapping-file display through the mapping
  repository path.
- `DataMappingPanel` still has user-facing wording that describes Predict
  dropdown ownership as repository-centric rather than adapter/core-owner
  centric.

## Target Flow

1. `PredictWorkspace` triggers a controller start method and updates only UI
   state: button state, progress text, row refresh, and status/badges.
2. `PredictionController` chooses the run scope, builds row requests, records
   invalid rows immediately on the UI thread, and marks valid rows as running
   before the worker starts.
3. `PredictionWorker` receives immutable `PredictionJob` data containing a
   `run_id` and the valid request list.
4. The worker calls `PredictionService.predict_one()` for each valid request
   and emits row result, progress, finished, cancelled, or failed events.
5. `PredictionController` receives worker events on the UI thread, converts
   service results through `PredictionResultAdapter`, mutates `PredictSession`,
   and asks the workspace to refresh affected rows.
6. `PredictWorkspace` displays progress and final/cancelled/partial summary
   state without calling core ML directly.

## Contract Dataclasses

The worker boundary should use small explicit dataclasses rather than a generic
job framework:

- `PredictionJob`: `run_id`, `requests`, `total`.
- `PredictionProgress`: `run_id`, `completed`, `total`, `current_case_id`,
  `message`.
- `PredictionWorkerSummary`: `run_id`, `total`, `complete`, `error`,
  `cancelled`.
- Optional `PredictionRunState`: minimal controller/UI state if it simplifies
  button/progress rendering.
- Optional `PredictionModelStatus`: Qt-free model path, state, and message.

Signal payloads can be sent with `Signal(object)` to keep PySide typing simple.

## Cancellation Semantics

- Cancellation is cooperative.
- `PredictionWorker.cancel()` sets a flag; the worker checks it before and
  after each row.
- Already emitted complete/error row results remain unchanged.
- Not-yet-run rows should be marked `cancelled` by the controller only if the
  result adapter/state model explicitly supports a row-level cancelled status;
  otherwise they remain pending and the run summary/status says cancelled or
  partial.
- No `QThread.terminate()` or forced thread kill pattern is allowed.

## Error Semantics

- Invalid input rows are detected before worker execution and are not sent to
  the worker.
- Row-level service errors do not abort the batch.
- Missing or unloadable model state should produce controlled row-level errors
  for valid requests.
- A worker-level `failed` signal is reserved for unexpected infrastructure
  failures outside normal service row errors.

## Resource Status Cleanup

- Model status belongs to `PredictionService` or a small app-side service
  method surfaced through `PredictionController`.
- Model status should report path and state such as missing, load error, or
  loaded without requiring widgets.
- Mapping status belongs to the mapping repository/adapter/controller boundary,
  not direct widget-owned raw file checks.
- After cleanup, `PredictWorkspace` should not import `MODEL_FILE` directly or
  own direct `Path(MODEL_FILE)` checks.

## Data Mapping Wording

The Data Mapping panel should describe Predict dropdown ownership as
`DropdownOptionAdapter` plus the core mapping owner, or equivalent wording. It
should not imply that the UI or a raw repository call owns dropdown behavior.

## Non-goals

- No Arc 11 Trainer execution foundation.
- No generic worker framework.
- No ML algorithm, feature, preprocessing, artifact, mapping JSON, calculator,
  or public result contract changes.
- No broad visual redesign of the accepted Arc 9.5 unified table.

## Implementation Order

1. Add contracts and Qt-free service status.
2. Implement the focused prediction worker.
3. Wire controller orchestration and QThread lifecycle.
4. Connect workspace progress/cancel UI and resource-status cleanup.
5. Strengthen tests for model-missing, invalid rows, mixed partial results,
   cancellation, double start, and Train-shell construction.
