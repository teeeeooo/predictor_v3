# Arc 11 Predict / Train Hexagonal Boundary Reopen

Date: 2026-06-28

## Purpose

Formalize the reopened Arc 11 acceptance decision for the Machine Learning /
Predictor phase. The correct hierarchy is Phase > Arc > Slice; do not create
decimal sub-arcs such as Arc 11.1.

Arc 11 is reopened because the previous automated Train/Predict coverage did
not complete the application-usecase and execution boundary acceptance.

## Audit Summary Already Performed

The first-pass architecture audit was already performed before this record. The
repo state confirms the finding: prediction execution orchestration is still
owned by PySide6/QThread controller and worker code, and production training is
still launched through an in-process service call to `train_all_models()`.

## Non-Negotiable Architecture Rule

Controller/service split alone is not enough when the service or controller
still owns infrastructure execution concerns. Long-running execution, killable
jobs, process lifecycle, stdout/stderr event parsing, external tool execution,
and artifact promotion/cleanup are outbound adapter concerns behind explicit
ports.

Application usecases must remain UI/runtime-neutral where the workflow may be
reused from PySide6, Tkinter, another desktop GUI toolkit, Web UI, CLI smoke
runner, remote worker, or automation shell.

## Predict Finding

Current prediction service and row/result adapters are mostly toolkit-neutral,
but `PredictionController` owns PySide6 `QThread` lifecycle and
`PredictionWorker` is a PySide6 `QObject`/signal worker. That is acceptable as a
PySide adapter implementation, not as the final application-usecase boundary.

Arc 11 Slice 2 owns the correction: extract a UI/runtime-neutral prediction
usecase and execution port, keeping the existing QThread worker as a PySide
runner adapter where useful.

## Train Finding

Production training currently flows through `TrainingService` into
`core.ml.training.train_all_models()` inside the app process, with QThread
orchestration in the controller/worker layer. Cooperative or requested
cancellation is insufficient for the visible `중지` button.

Arc 11 Slice 1 owns the correction: production Train execution must use a
`TrainingExecutionPort` and a killable process runner adapter such as
`QProcessTrainingRunner`. `중지` means hard-stop the running training process;
if graceful termination does not finish quickly, the runner kills the process
and cleans temporary artifacts.

## Calculator Moved To Arc 12

Calculator UI/application boundary debt is real, but it is out of Arc 11 scope.
Arc 11 records the routing decision only. Calculator usecase correction belongs
to Arc 12 and must not be designed or implemented inside Arc 11 slices.

## Arc Map Correction

- Arc 11: Predict / Train Hexagonal Boundary Recovery, reopened.
- Arc 12: Calculator UseCase Boundary Correction, planned after Arc 11.
- Arc 13: ML Pipeline Stabilization, formerly Arc 12, on hold until Arc 11 and
  Arc 12 architecture corrections are complete.

## Required Implementation Order

1. Slice 0 - Acceptance Reset / Hexagonal Boundary Formalization.
2. Slice 1 - Train Execution Port + QProcess Hard Stop.
3. Slice 2 - Predict Execution UseCase / Execution Port Correction.
4. Slice 3 - Re-closeout / Train-Predict Manual Smoke Gate.

## Train Hard-Stop Semantics

The production runner must run training in a separate process, forward
structured events, terminate on cancel, kill after a short timeout if needed,
return a cancelled result, and avoid leaving orphan processes or partial final
model artifacts.

## UI/Runtime Portability Acceptance Rule

Future non-PySide interfaces must be able to reuse application-level prediction
and training orchestration without importing PySide6 or QThread types. Web UI
is only one example; the criterion is UI/runtime portability.

## Excluded Scope

- ML algorithm, preprocessing, target registry, feature schema, and artifact
  schema changes.
- Mapping schema changes.
- Calculator implementation or calculator design extraction.
- Broad report lifecycle cleanup.
