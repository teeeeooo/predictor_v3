# Project Brief

This document owns the compact Phase / Arc / Milestone map for `predictor_v3`.
It is the first project-state document to read when starting a new session or
resuming work.

It does not own task-specific read pointers, code file pointers, or the exact
next implementation action. Current slice, next action, blockers, constraints,
and explicit handoff pointers belong to `docs/WORK_PLAN.md`.

## 1. Current Phase

Current phase: ML / Predictor Continuation — PySide6 Train/Predict Rewrite.

The calculator UI/workflow stabilization phase is complete enough to resume the
ML / predictor path. The first current workstream is the approved PySide6
Train/Predict rewrite, not an in-place PyQt5 migration.

Project direction remains aligned with `PROJECT_CHARTER.md`:

1. keep completed calculator formula/UI/workflow contracts stable;
2. establish the PySide6 Train/Predict app boundary and reusable Predict
   workspace;
3. stabilize ML feature, model artifact, preprocessing, and result mapping
   contracts;
4. reconnect predictor outputs to calculator inputs and later
   ranking/recommendation workflows.

## 2. Current Architecture State

- Calculator UI/workflow closeout is complete for the current phase. Detailed
  completed calculator history belongs in lifecycle summaries and reports, not
  in this brief.
- Calculator entrypoints remain rooted at `app_calculator.py` and
  `apps.calculator.app:main`, with current calculator UI code under
  `apps/calculator/ui/`.
- Train/Predict paths remain separate from the calculator shell and the
  Tkinter calculator path.
- Train/Predict is a new PySide6 implementation, not a PyQt5 migration.
- New Train/Predict package boundaries are `apps/predict/` and `apps/train/`.
- Existing PyQt5 `ui/` Train/Predict files remain a reference-only legacy path
  until a later explicit retirement slice.
- `app_predict.py` is the Predict-only application entrypoint.
- `app_train.py` is the administrator/developer entrypoint that adds Train /
  Model and Data Mapping capabilities while reusing the Predict workspace.
- `PredictWorkspace` is owned by the Predict package and reused by the Train
  app's Predict tab.
- `core.predictor`, `core.trainer`, `core.data_pipeline`, `core.models`, and
  `core.constants` remain UI-toolkit independent.
- Region config, HW candidate input, ML feature schema, calculator result
  schema, and UI table schema must not be mixed.

## 3. Previous Completed Phase

### Calculator UI / Workflow Stabilization

Status: complete for current phase.

Summary anchors:

- EN14825 config, point contract, UI workflow closeout:
  `result_reports/summaries/404_summary-en14825-config-point-contract-ui-workflow-closeout.md`
- EN14825 batch and agent change-gate closeout:
  `result_reports/summaries/416_summary-en14825-batch-agent-change-gate-closeout.md`
- AHRI calculator UI/batch lifecycle closeout:
  `result_reports/summaries/445_summary-ahri-calculator-ui-batch-lifecycle-closeout.md`
- Calculator helper/batch/detail lifecycle closeout:
  `result_reports/summaries/490_summary-calculator-helper-batch-lifecycle-closeout.md`

Detailed EN14825, AHRI, helper, batch, detail, token, and manual-smoke
milestones are intentionally not repeated here.

## 4. Current Arc / Milestone Map

### Arc 1 — PySide6 Train/Predict Rewrite Design Alignment

Goal:

- Make the PySide6 Train/Predict rewrite decision, package boundary, and visual
  reference path discoverable from active project docs.

Status:

- Complete / closing in the current local checkout.

Milestones:

- Design gate and implementation spec added.
- Non-binding visual reference assets added.
- Charter, architecture, workflow, design index, and work plan references
  aligned.
- Legacy PyQt5 `ui/` path classified as reference-only, not immediate deletion.

Reference anchors:

- `docs/designs/2026-06-27-pyside6-train-predict-rewrite-design-gate.md`
- `docs/designs/2026-06-27-pyside6-train-predict-ui-implementation-spec.md`
- `result_reports/active/493_pyside6-train-predict-doc-alignment.md`

### Arc 2 — PySide6 App Skeleton and Package Boundary

Goal:

- Establish `apps/predict/` and `apps/train/` package skeletons without moving
  or deleting legacy PyQt5 `ui/` files.

Target milestones:

- Add `apps/predict` and `apps/train` skeleton packages.
- Convert `app_predict.py` and `app_train.py` to thin wrappers after the new
  packages exist.
- Add minimal PySide6 shell windows and Trainer tab shell.
- Verify PySide6 import smoke and entrypoint import/compile smoke.

### Arc 3 — PredictWorkspace Variable-size Batch UI

Goal:

- Build the reusable Predict workspace around variable-size batch prediction
  rather than fixed row counts.

Target milestones:

- Add editable `Input Cases` table.
- Add read-only `Prediction Results` table.
- Keep input/result rows synchronized by `case_id` and `case_order`.
- Introduce `CaseStore` / `PredictSession` state ownership.
- Preserve selection and scroll synchronization between input and result
  surfaces.
- Forbid fixed UI row-count assumptions.

### Arc 4 — Prediction Execution and Result Mapping

Goal:

- Connect PredictWorkspace rows to the existing prediction path through
  adapters/services without changing ML algorithms.

Target milestones:

- Add UI-row to ML-input adapter.
- Add prediction service wrapper around the existing predictor path.
- Add prediction result adapter for result-table display.
- Support all-case, selected-case, and changed-case prediction scopes as
  approved slices.
- Keep progress/cancel behavior behind worker boundaries.

### Arc 5 — Trainer Admin App

Goal:

- Make `app_train.py` the administrator/developer app with Predict, Train /
  Model, and Data Mapping tabs.

Target milestones:

- Reuse `PredictWorkspace` in the Train app's Predict tab.
- Add Train / Model panel.
- Add Data Mapping panel.
- Add training worker boundary and progress/log status.
- Add model artifact/status visibility.
- Keep mapping update behavior behind a service/adapter boundary.

### Arc 6 — ML Pipeline Stabilization

Goal:

- Stabilize ML feature, leakage, model artifact, preprocessing, and result-key
  contracts after the UI shell boundary is established.

Target milestones:

- Review `MODEL_REGISTRY`, `BASE_FEATURES`, `TARGETS`, and target leakage
  rules.
- Preserve single-artifact and preprocessing compatibility contracts unless a
  later design explicitly changes them.
- Align one-hot option and result-key SSOT ownership.
- Add focused ML tests around feature names, leakage, and prediction/training
  boundary behavior.

### Arc 7 — Calculator to Predictor Integration

Goal:

- Prepare predictor outputs for calculator input adapters and later
  ranking/recommendation workflows.

Target milestones:

- Define a predicted-points/result envelope for calculator handoff.
- Expand calculator input adapters only through approved boundaries.
- Calculate seasonal metrics from prediction output in a later approved slice.
- Keep ranking/recommendation preparation separate from Train/Predict UI
  skeleton work.

## 5. Deferred / Hold Areas

- AS/NZS Excel compatibility Z-phase remains deferred.
- Internal formula trace remains on hold unless a separate core/data contract is
  approved.
- Broad code-quality refactors belong in `docs/REFACTOR_PLAN.md`, not in this
  brief.
- Packaging and hook-integration work should remain separate workflow arcs
  unless explicitly promoted.
- Legacy PyQt5 `ui/` retirement remains deferred until the PySide6 Predict/Train
  apps have import smoke and minimum manual GUI smoke evidence.

## 6. Session Start Rule

1. Read `project_brief.md` to understand the current Phase, active Arc, and
   Milestone position.
2. Read `docs/WORK_PLAN.md` to identify the current slice, next action,
   blockers/open decisions, and constraints.
3. If `docs/WORK_PLAN.md` contains a user-requested `Session Handoff`, follow its
   `Read First` and `Task-Specific Pointers` before broader reads.
4. Use `AGENT_TASK_ROUTER.md` only for the sections required by the current task
   type.
5. Do not reconstruct current priority from archived reports or long report
   histories.

## 7. Document Guide

- `AGENTS.md`: lite rule entrypoint for each agent task.
- `AGENT_TASK_ROUTER.md`: task route and compact gate map.
- `PROJECT_CHARTER.md`: long-term purpose, Phase 1~5, and project principles.
- `project_brief.md`: Phase / Arc / Milestone map.
- `docs/WORK_PLAN.md`: current slice, next action, blocker/open decision,
  constraints, deferred/hold items, and explicit Session Handoff.
- `project_log.md`: milestone decision, failure, and lesson history.
- `ACTIVE_DOCUMENTS.md`: active document owner/inbound/outbound map.
- `result_reports/`: task detail, lifecycle summaries, completed report archive,
  and memory staging.
