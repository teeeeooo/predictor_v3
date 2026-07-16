# Train/Admin Phase 4 — Train/Model and Shell UX Overhaul

Status: proposed phase design; current-state audit and finalization pending
Date: 2026-07-16
Depends on: Phases 1–3

## 1. Goal

Complete the Train/Admin experience by redesigning the common shell and
Train / Model workflow around the user's task: selecting training data, training,
checking progress, and reviewing results. Readiness, safe execution, recovery,
and cross-tab state support that flow without turning the default surface into an
internal state dashboard.

This phase does not change ML algorithms unless a separately approved defect or
compatibility requirement demands it.

## 2. Shell Scope

The shell continues to host:

1. Predict
2. Train / Model
3. Data Definition
4. Data Mapping

The shell communicates the current user-facing next action without duplicating
each tab. Normal schema, feature, mapping, and compatibility details stay behind
the workflow and are exposed in Diagnostics/logs when needed.

The shell may derive the following internal state:

- model artifact status;
- training data status;
- schema/definition readiness;
- mapping readiness;
- unsaved Data Definition changes;
- unsaved Data Mapping changes;
- restart required;
- retraining required;
- fixture/mock context where relevant to development/test compositions;
- blocking errors requiring user action.

Only the user-facing state and next action belong on the default surface. Detailed
status indicators remain actionable through the responsible tab or Diagnostics/
logs.

## 3. Train / Model Target Workflow

```text
select training data
    -> train
    -> check progress
    -> review results
```

Schema, feature, mapping, and compatibility checks run automatically as part of
selection/start validation. They do not require the user to inspect technical
metadata or complete a manual readiness checklist. Not every derived readiness
state blocks Start; the classification in Section 5 determines whether a check
is a training-start blocker, a non-blocking warning/state, or a post-training
artifact/Predict blocker. When a check blocks training, the default surface
presents a plain-language explanation and the action that resolves it; detailed
evidence is available in Diagnostics/logs.

## 4. Train / Model Information Architecture

The resulting surface should provide:

- resource selection/status;
- a clear Train action when the selected data can proceed;
- supported training configuration as a compact summary, with optional overrides
  in Advanced settings;
- start/cancel controls;
- progress and current stage;
- user-facing failure context and its resolution action;
- a result summary centered on the completed training outcome;
- produced model save status and elapsed time;
- Predict availability after existing activation conditions pass;
- Diagnostics/log access for advanced technical details.

Mock execution success must not be presented as model-quality success.

### Default and Advanced training settings

The normal flow uses the safe defaults already provided by the authoritative
Train/ML settings owner and execution contract. Phase 4 does not create a
second UI-owned default policy.

- Only values that the existing Train/ML contract requires the user to decide
  before a run appear in the default surface.
- Supported training can start without opening Advanced settings when those
  required decisions are already satisfied.
- Optional or technical settings belong in a collapsed `Advanced settings`
  area, or an equivalent progressive-disclosure surface.
- The default surface does not list preprocessing-version internals, full
  feature-policy details, Optuna parameter details, or RFECV configuration just
  because those settings are valid.
- When an optional setting is changed, show a concise summary of the change;
  do not expand the normal flow into a settings-management screen.

## 5. Readiness and Blocker Classification

The workflow may derive technical readiness internally, but only the
authoritative Train/ML execution boundary decides whether a state blocks a new
training start. The UI must not turn every readiness value into a manual
checklist or a Start blocker.

### 5.1 Training-start blockers

These are conditions under which training cannot be safely started:

- the selected training-data file is missing or unreadable;
- the file or data format is unsupported;
- a training-required Target or feature column is missing;
- another input condition defined by the authoritative Train/ML execution
  contract makes the run impossible.

The exact predicate is determined during the current-state audit from the
existing Train/ML owner and execution boundary. Phase 4 does not invent a new
policy in the UI. Only this category produces a blocked Start result.

### 5.2 Non-blocking warnings and states

Training may proceed when these conditions are not required by the authoritative
Train/ML contract, although they may require a later action or explain current
artifact state:

- no existing model artifact;
- an old model or retraining-required state;
- restart required;
- incomplete mapping values when the selected training input does not require
  them for the current run;
- no model currently available for Predict.

Predict readiness, existing model existence, and existing artifact compatibility
must not be inverted into prerequisites for new model training. An incomplete
mapping or schema state similarly does not block Start merely because it is a
readiness issue; the authoritative owner contract remains the source of truth.

### 5.3 Post-training artifact/Predict blockers

These occur after training execution completes and concern persistence or use of
the resulting model:

- model save failure;
- artifact validation failure;
- mismatch between the new artifact and the active feature contract;
- Predict load or activation failure;
- restart not completed, leaving Predict unable to use the saved result.

These states are represented in the result view through model-save status,
Predict availability, and the next action. They do not retroactively become
training-start blockers.

All three categories remain internal state. The default surface shows only the
user-facing outcome and next action. Owner routing for a blocking issue is:

- input/header issue -> Train / Model;
- a required definition issue -> Data Definition;
- a required mapping issue -> Data Mapping;
- post-training artifact/Predict issue -> Train / Model or shell action.

## 6. Training Execution

Preserve existing execution boundaries and Cooling/Heating independence.

The UX must:

- prevent duplicate starts;
- make cancellation explicit;
- show progress without freezing the UI;
- retain enough failure context for correction;
- distinguish cancelled, failed, and completed;
- avoid claiming activation before persistence and compatibility checks pass;
- preserve model registry and artifact ownership.

Optuna, RFECV, monotone constraints, model selection, and algorithm behavior are
not redesigned here.

## 7. Result Presentation

After completion, show:

- overall success or failure;
- success or failure for each trained Target;
- R² for each trained target;
- MAE/RMSE when available and useful for the result;
- whether Optuna ran and its completion status;
- best trial or best score when Optuna provides it;
- whether the model was saved;
- total elapsed training time and per-Target time when the result contract
  provides it;
- whether Predict can use the resulting model;
- the next user action when the result cannot be saved or used by Predict.

Target names, metric labels, and optional values follow the existing Train/ML
result contracts. If an existing owner does not yet provide a requested result
field, the Phase 4 audit identifies a Qt-free result projection extension; it
does not claim the field is already implemented. The default result view excludes
full schema details, full feature order, raw mapping coverage, raw compatibility
evidence, the complete Optuna trial list, stack traces, and step-by-step internal
validation output. These remain available in Diagnostics/logs or a detail view.

Repository mock results carry an explicit limitation:

```text
Pipeline and contract validation only.
This does not establish real-world accuracy or production readiness.
```

## 8. Shared UI System

By phase completion, Train/Admin uses reusable common components for:

- spreadsheet-like tables;
- section/page headers;
- command bars;
- status badges;
- issue banners and lists;
- empty/missing/error states;
- dirty indicators;
- save/discard confirmations;
- restart/retrain notices;
- progress surfaces;
- result summaries.

These components should be suitable for later Predict adoption. Avoid a
Train-only visual system that would require another rewrite.

The visual overhaul may substantially change spacing, typography, table
treatment, layout, and component composition while preserving meaningful cell
roles and status semantics.

## 9. Cross-tab Workflow

Required handoffs include:

- shell status -> responsible tab;
- Data Definition save -> restart/retrain/mapping-value action;
- Data Mapping save -> updated mapping readiness;
- Train completion -> updated model status and Predict readiness;
- dirty state -> warning before close or destructive context change;
- restart-required state -> remains visible until process boundary is satisfied.

Avoid fragile direct widget dependencies. Use existing controller/service state
or an appropriate application-level coordination mechanism discovered during
implementation audit.

## 10. Implementation Slices

### Slice 4A — Current-state audit and design finalization

- Audit the merged-main Train/Model and shell surfaces against current owner and
  public-contract boundaries.
- Freeze the user-flow, automatic-validation, progressive-disclosure, error-
  recovery, and result-summary contracts before implementation.
- Keep this slice documentation/planning only.

### Slice 4B — Training-data selection and automatic validation

- Make training-data selection the first user task.
- Run schema, feature, mapping, and compatibility checks internally.
- Present a clear proceed/block outcome only for Section 5.1 training-start
  blockers; present Section 5.2 states as warnings or follow-up actions without
  blocking Start unless the authoritative Train/ML contract requires it.

### Slice 4C — Training execution and progress

- Start/cancel training through the existing execution boundary.
- Show current stage, progress, completion, cancellation, and failure states
  without freezing the main UI.

### Slice 4D — Results and Predict availability

- Present the overall outcome, per-Target success/failure and R², optional
  MAE/RMSE, applicable Optuna status/best trial or score, model-save status,
  elapsed time, Predict availability, and the next action for Section 5.3
  post-training blockers.
- Preserve existing runner/worker, artifact, and ML boundaries.

### Slice 4E — Common shell and Diagnostics/log consolidation

- Make shell state and shared visual components support the user flow without
  exposing internal readiness by default.
- Route error details and technical evidence to Diagnostics/logs; retain concise
  user-facing messages and resolution actions in the primary surface.
- Record the component inventory and remaining Predict adoption gaps.

Each slice is one logical commit and is pushed to the phase branch. The phase is
merged only after cross-tab workflow and mock training smoke pass.

## 11. Acceptance Scenarios

- Training-data selection is the first primary task and leads to a clear Train
  action when automatic checks pass.
- A supported default training run starts without opening Advanced settings.
- Train asks for input before Start only when an existing Train/ML contract
  requires a user decision that cannot be satisfied by its safe defaults.
- The default surface remains centered on data selection, execution, progress,
  and results rather than configuration management.
- Only authoritative training-start blockers prevent the Train action; existing
  model, restart, mapping, or Predict readiness does not block Start without an
  owner-contract basis.
- Schema/header, feature, mapping, or compatibility checks are detected
  automatically and show a user-facing resolution action first when they block.
- Training runs without blocking the main UI and reports progress.
- Cancellation and failure produce distinct states.
- Successful training shows overall success, per-Target outcome and R², optional
  MAE/RMSE, applicable Optuna status and best trial/score, model-save status,
  elapsed time, and Predict availability without making production accuracy
  claims.
- Post-training save, artifact, activation, or restart failures are represented
  as Predict availability and next-action states rather than Start blockers.
- Detailed failure evidence is available in Diagnostics/logs.
- Shell state refreshes after relevant actions without becoming a readiness
  dashboard.
- Unsaved Definition or Mapping work is not silently lost.
- Predict remains operational and consumes a compatible model, while its internal
  UX remains unchanged.

## 12. Non-goals

- Predict internal redesign.
- New ML algorithms.
- Automatic real-data transformation.
- Production model-quality certification.
- Calculator changes.
- Replacing established model registry or public artifact APIs without a separate
  approved design.
