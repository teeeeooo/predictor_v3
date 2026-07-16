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
metadata or complete a manual readiness checklist. When a check blocks training,
the default surface presents a plain-language explanation and the action that
resolves it; detailed evidence is available in Diagnostics/logs.

## 4. Train / Model Information Architecture

The resulting surface should provide:

- resource selection/status;
- a clear Train action when the selected data can proceed;
- supported training configuration;
- start/cancel controls;
- progress and current stage;
- user-facing failure context and its resolution action;
- a result summary centered on the completed training outcome;
- produced model save status and elapsed time;
- Predict availability after existing activation conditions pass;
- Diagnostics/log access for advanced technical details.

Mock execution success must not be presented as model-quality success.

## 5. Readiness Model

The workflow may derive at least:

- training data exists;
- headers match active ML projection;
- mapping requirements are sufficiently populated;
- schema/features projection is compatible;
- current model artifact exists;
- current model matches active feature names/order/types;
- retraining is required;
- restart is required;
- training can start;
- Predict can use the current/resulting model.

These checks are internal. If a readiness issue blocks the flow, the user-facing
message identifies the responsible action/tab:

- definition issue -> Data Definition;
- mapping coverage issue -> Data Mapping;
- training input/header issue -> Train / Model;
- restart requirement -> shell-level state.

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
- R² for each trained target;
- MAE/RMSE when available and useful for the result;
- Optuna status and best trial/score when tuning ran or reported a result;
- whether the model was saved;
- elapsed training time;
- whether Predict can use the resulting model;
- the next user action when restart or retraining is still needed.

Target names, metric labels, and optional values follow the existing Train/ML
result contracts. Detailed logs, raw compatibility evidence, and technical
diagnostics remain available on demand rather than in the default result view.

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
- Run schema, feature, mapping, and compatibility checks internally and present
  only a clear proceed/block outcome with an action when blocked.

### Slice 4C — Training execution and progress

- Start/cancel training through the existing execution boundary.
- Show current stage, progress, completion, cancellation, and failure states
  without freezing the main UI.

### Slice 4D — Results and Predict availability

- Present the overall outcome, target-level metrics, applicable Optuna result,
  model-save status, elapsed time, and Predict availability.
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
- Schema/header, feature, mapping, or compatibility problems are detected
  automatically and show a user-facing resolution action first.
- Training runs without blocking the main UI and reports progress.
- Cancellation and failure produce distinct states.
- Successful training shows overall success, target-level R², optional MAE/RMSE,
  applicable Optuna status and best trial/score, model-save status, elapsed time,
  and Predict availability without making production accuracy claims.
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
