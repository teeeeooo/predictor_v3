# Arc 11 Train Execution Boundary Design

## Goal

Define the Train execution boundary before implementation so Arc 11 can add
service, worker, controller, UI wiring, and E2E smoke coverage without changing
core ML training behavior.

## Current State

- `app_train.py` launches the PySide6 Trainer shell through `apps.train.app`.
- `TrainShell` embeds the Predict workspace and shows `Train / Model` and
  `Data Mapping` tabs.
- `TrainModelPanel` is currently a visual shell: command buttons are disabled,
  progress/log/summary surfaces are placeholders, and execution is deferred.
- `DataMappingPanel` remains visual-only and its update execution is outside
  this arc.
- Arc 10.5b provides the fixed DEV-only mock bundle for smoke fixtures.

## Boundary Decision

Arc 11 uses two separated training execution paths:

- Production default path: `TrainingService` wraps
  `core.ml.training.train_all_models(data_path=..., log_callback=...)`.
- DEV-only smoke path: a fast backend under `tools/dev/mock_smoke/` writes an
  inference-compatible `model/model.pkl` using existing mock artifact
  generation logic.

The DEV path is only for UI/controller/worker/service E2E confidence. It does
not claim real model quality, real metrics, feature importance, or HVAC physical
trend validity.

## Production Service

Owner: `apps/train/services/training_service.py`.

Responsibilities:

- define explicit Qt-free request/log/progress/result dataclasses;
- validate the training data path before running;
- call `core.ml.training.train_all_models`;
- capture summary text, model artifact path, and log path/status;
- translate exceptions into structured error results;
- expose data/model resource status to the controller/UI boundary.

Non-responsibilities:

- no PySide6 import;
- no widget mutation;
- no QThread ownership;
- no core ML algorithm, preprocessing, target registry, or artifact schema
  changes.

## Worker

Owner: `apps/train/workers/train_worker.py`.

Responsibilities:

- receive an immutable `TrainingRequest`;
- execute the service call away from the UI thread;
- emit log, progress, finished, failed, and cancelled events;
- support cooperative cancel request without `terminate()` or thread kill.

Production cancellation is limited because `train_all_models()` does not expose
an interruptible backend contract. The initial worker may record cancellation
intent and finish the active production service call before returning. The
DEV-only backend should support cooperative cancellation for deterministic E2E
coverage.

## Controller

Owner: `apps/train/controllers/train_controller.py`.

Responsibilities:

- provide `start(...)`, `cancel()`, `is_running`, `resource_status()`, and
  optional `last_result`;
- reject double start;
- validate data path before worker start;
- own QThread/worker lifecycle and cleanup;
- receive worker events on the UI thread;
- expose updates through callbacks/events for the panel.

Non-responsibilities:

- no QWidget subclassing;
- no XGBoost/core training internals;
- no direct QTextEdit writes;
- no orphan worker threads after finish, error, or cancel.

## UI

Owner: `apps/train/ui/train_model_panel.py`, with shell dependency wiring in
`apps/train/ui/shell.py` only when needed.

Responsibilities:

- render data/model paths, preprocess version, command buttons, progress,
  result state, summary table, and training log;
- wire user actions to the controller API;
- update view state from controller callbacks;
- keep Train / Model execution separate from Data Mapping execution.

Initial behavior:

- `학습 실행` is enabled only when a data path exists and no run is active;
- `중지` is enabled only while a cancellable run is active;
- default data path is `data/Practice_4.csv` when present;
- file dialog selection may exist, but smoke tests must not depend on it;
- `모델 열기` and `로그 저장` may stay disabled unless implemented minimally;
- production progress may be indeterminate when precise target progress is not
  available;
- DEV smoke progress should be deterministic.

## Model Artifact And Status

The artifact contract remains the existing single `model/model.pkl` path owned
by `core.ml.artifacts.MODEL_FILE`. Production training writes through the
existing core training route. DEV smoke writes a compatible mock artifact and
may install it explicitly for app smoke.

After a training run finishes, the Train shell/panel should refresh model
status through the service/controller boundary where possible. Predict smoke can
then run against the generated artifact.

## E2E Smoke Plan

Fast Train UI E2E:

- generate the Arc 10.5b mock bundle;
- install mock train data/mapping/model only when explicitly needed;
- instantiate Train UI with an injected DEV-only fast backend/controller;
- start training through the UI/controller boundary;
- assert progress/log/summary/finish state changes;
- assert a generated inference-compatible model artifact exists;
- run Predict smoke with the generated model and mock mapping/case TSV;
- clean generated outputs and local installs.

Optional real core training smoke:

- directly exercise `TrainingService` with real `train_all_models`;
- remain opt-in because Optuna and 5-fold validation are expensive;
- clearly report skipped/meaningless metrics in ordinary validation.

## Excluded Scope

- Data Mapping Excel update execution;
- core ML algorithm, preprocessing, target registry, model artifact schema, or
  training formula changes;
- calculator behavior changes;
- mapping JSON schema changes;
- real model quality, feature importance, or HVAC physical trend claims;
- generated mock data/model/mapping/output committed to git.

## Reuse / Commonization

- Reuse Predict controller/worker lifecycle as the closest app-side reference.
- Reuse existing `tools/dev/mock_smoke/generators.py` artifact generation logic
  for the DEV-only backend instead of creating a second artifact contract.
- Keep Train-specific service/worker/controller local to `apps/train` because
  training requests, cancellation limits, and result semantics differ from
  prediction row execution.
