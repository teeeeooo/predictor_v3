# Train/Admin Phase 4 — Train/Model and Shell UX Overhaul

Status: proposed phase design  
Date: 2026-07-14  
Depends on: Phases 1–3

## 1. Goal

Complete the Train/Admin experience by redesigning the common shell and
Train / Model workflow around resource readiness, safe execution, understandable
results, and consistent cross-tab state.

This phase does not change ML algorithms unless a separately approved defect or
compatibility requirement demands it.

## 2. Shell Scope

The shell continues to host:

1. Predict
2. Train / Model
3. Data Definition
4. Data Mapping

The shell communicates overall workflow state without duplicating each tab.

Required common state includes:

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

Status indicators should be actionable and route the user to the responsible tab
or next action.

## 3. Train / Model Target Workflow

```text
select or confirm training data
    -> inspect schema/header/model readiness
    -> configure supported training options
    -> run training
    -> monitor progress and logs
    -> inspect outcome and validation summary
    -> save/activate artifact under existing policy
    -> confirm Predict availability
```

Missing prerequisites must be visible before a long operation starts.

## 4. Train / Model Information Architecture

The resulting surface should provide:

- resource selection/status;
- concise readiness summary;
- blockers and warnings;
- supported training configuration;
- start/cancel controls;
- progress and current stage;
- actionable failure context;
- result summary;
- produced model artifact status;
- compatibility with current schema/features;
- Predict activation/readiness;
- advanced logs/details without dominating the normal view.

Mock execution success must not be presented as model-quality success.

## 5. Readiness Model

The UI distinguishes at least:

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

Readiness issues identify the responsible owner tab:

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

- which model targets were trained;
- success/failure per model;
- artifact path/status;
- active feature count and compatibility summary;
- warnings about mock data or absent real validation;
- whether Predict can load the artifact;
- next action when restart or retraining is still needed.

Detailed logs remain available for diagnosis.

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

### Slice 4A — Common shell and actionable status

- Redesign shell-level status and navigation.
- Integrate dirty, restart, retrain, model, mapping, and training-data state.
- Keep Predict internally unchanged.

### Slice 4B — Train/Model readiness workflow

- Reorganize prerequisites, configuration, and blockers around the start decision.
- Add owner-tab handoffs for unresolved readiness issues.

### Slice 4C — Training execution experience

- Improve progress, cancellation, failure, and completion states.
- Preserve existing runner/worker and ML boundaries.

### Slice 4D — Result and artifact activation state

- Present per-model results and artifact compatibility.
- Update Predict readiness only after existing activation conditions pass.

### Slice 4E — Shared visual/component consolidation

- Remove duplicated panel-specific status/table/banner patterns.
- Establish reusable PySide6 components and final visual consistency.
- Record the component inventory and remaining Predict adoption gaps.

Each slice is one logical commit and is pushed to the phase branch. The phase is
merged only after cross-tab workflow and mock training smoke pass.

## 11. Acceptance Scenarios

- Missing training data is visible before Start and links to correction.
- Schema/header mismatch points to Data Definition or the training-input owner.
- Missing mapping coverage points to Data Mapping.
- Training runs without blocking the main UI and reports progress.
- Cancellation and failure produce distinct states.
- Successful mock training creates/loads the expected artifact contract without
  making accuracy claims.
- Shell statuses refresh after relevant actions.
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
