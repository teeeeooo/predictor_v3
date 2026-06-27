# Project Brief

This document owns the compact Phase / Arc / Milestone map for `predictor_v3`.
It is the first project-state document to read when starting a new session or
resuming work.

It does not own task-specific read pointers, code file pointers, or the exact
next implementation action. Current slice, next action, blockers, constraints,
and explicit handoff pointers belong to `docs/WORK_PLAN.md`.

## 1. Current Phase

Current phase: Arc 9.5 ready - Predict / Train Visual UI Parity from Design
Assets.

The calculator UI/workflow stabilization phase is complete enough to resume the
ML / predictor path, and the approved PySide6 Train/Predict foundation now
exists. PySide6 Predictor schema/mapping recovery and legacy `ui/` retirement
are complete enough to proceed to visual parity from the approved design
assets.

Project direction remains aligned with `PROJECT_CHARTER.md`:

1. keep completed calculator formula/UI/workflow contracts stable;
2. keep the project-wide architecture reset boundaries stable during deeper
   Train/Predict recovery;
3. establish no-behavior-change core package boundaries through compatibility
   wrappers;
4. stabilize ML feature, model artifact, preprocessing, and result mapping
   contracts;
5. reconnect predictor outputs to calculator inputs and later
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
- Current PySide6 foundation work is production foundation. Arc 9 recovered the
  schema/mapping path against the existing ML pipeline and broader core
  ownership; worker/progress remains deferred to Arc 10.
- The current `core/` root is no longer the active implementation surface for
  ML/schema/mapping/calculator owners. Arc 7 moved ML/schema/mapping
  implementation ownership under `core/ml`, `core/predictor_schema`, and
  `core/mapping`; Arc 8 moved calculator implementation ownership under
  `core/calculators`; Arc 8.5 retired root compatibility wrappers and migrated
  active callers to package owner paths.
- Legacy Train/Predict `ui/` files are retired in Arc 9.1 after harvesting
  useful visual/table ideas into active UI/UX docs.
- `app_predict.py` is the Predict-only application entrypoint.
- `app_train.py` is the administrator/developer entrypoint that adds Train /
  Model and Data Mapping capabilities while reusing the Predict workspace.
- `PredictWorkspace` is owned by the Predict package and reused by the Train
  app's Predict tab.
- `core.ml`, `core.predictor_schema`, `core.mapping`, `core.common`, and
  `core.calculators` remain UI-toolkit independent.
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

- Design gate and architecture contract added.
- Non-binding visual reference assets added.
- Charter, architecture, workflow, design index, and work plan references
  aligned.
- Legacy `ui/` path classified as reference-only before Arc 9.1 retirement.

Reference anchors:

- `docs/designs/2026-06-27-pyside6-train-predict-rewrite-design-gate.md`
- `docs/architecture/pyside6_train_predict_architecture.md`
- `result_reports/summaries/506_summary-pyside6-train-predict-arc3-closeout.md`

### Arc 2 — PySide6 App Foundation and Package Boundary

Goal:

- Establish `apps/predict/` and `apps/train/` package foundations before later
  legacy `ui/` retirement.

Target milestones:

- Add `apps/predict` and `apps/train` foundation packages.
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

### Arc 4 — Prediction Execution and Result Mapping Foundation

Goal:

- Connect PredictWorkspace rows to the existing prediction path through
  adapters/services without changing ML algorithms, while keeping later
  schema/mapping recovery explicit.

Status:

- Complete as production foundation, with schema/mapping recovery deferred
  until the project-wide architecture reset.

Completed milestones:

- Add UI-row to ML-input adapter.
- Add prediction service wrapper around the existing predictor path.
- Add prediction result adapter for result-table display.
- Add controller/workspace run-button integration.
- Keep result lookup by internal `case_id`.

Remaining gap:

- Worker/progress/cancel and real-model success smoke remain deferred until
  after schema/mapping recovery.

### Arc 5 — Project-wide Architecture Audit / Restructuring Plan

Goal:

- Audit the current project-wide architecture before deeper PySide6 Predictor
  recovery.

Target milestones:

- Classify current `core/` flat public surface across ML pipeline, calculator
  engines, shared utilities, constants, and schemas.
- Decide owner boundaries and migration constraints for package restructuring.
- Identify compatibility wrapper strategy and required import-smoke coverage.
- Leave physical moves and target folder tree finalization to the approved
  architecture SSOT update.

### Arc 6 — Architecture SSOT Update

Goal:

- Update architecture owner docs with the audited target structure and
  migration contract.

Status:

- Current documentation update arc.

Target milestones:

- Define the approved package boundary target for ML, calculators, common
  utilities, and constants/schema.
- Record the temporary public compatibility surface during migration.
- Record that compatibility wrappers are transition safety only, not final
  architecture.
- Keep detailed implementation slices in `docs/WORK_PLAN.md`, not this brief.

### Arc 7 — Core ML / Schema / Mapping Package Restructure

Goal:

- Move ML, predictor schema, and mapping responsibilities under real package
  owners with no behavior change.

Status:

- Complete as no-behavior-change package restructure. Arc 8.5 later retired
  root compatibility wrappers after active caller migration.

Target milestones:

- Add package shell / boundary imports for `core/ml`,
  `core/predictor_schema`, and `core/mapping`.
- Move ML implementation ownership to `core/ml/`.
- Move predictor column/schema ownership to `core/predictor_schema/`.
- Move mapping path/repository/update pure logic ownership to `core/mapping/`.
- Preserve existing behavior through focused import migration and smoke checks.
- Verify import policy, smoke checks, and no-behavior-change closeout.
- Do not move calculator engines, dispatcher, profiles, or calculator adapters
  in this arc.

### Arc 8 — Calculator Engine Package Restructure

Goal:

- Calculator implementation ownership now lives under `core/calculators/`
  after Arc 7 closeout.

Target milestones:

- Completed: calculators package shell.
- Completed: dispatcher and profiles moved to `core/calculators/`.
- Completed: calculator adapters moved to `core/calculators/adapters/`.
- Completed: calculator engines moved to `core/calculators/standards/`.
- Completed: calculator formulas, config, public result contracts, focused
  tests, and golden behavior preserved.

### Arc 9 — PySide6 Predictor Schema / Mapping Recovery

Goal:

- Recover the PySide6 Predictor schema/mapping path after Arc 7 and Arc 8
  package owners exist.

Target milestones:

Status:

- Complete.

Completed milestones:

- Aligned PySide6 schema adapter and table models with
  `core/predictor_schema`.
- Recovered mapping/autofill flow through `core/mapping` and app-side
  controller boundaries.
- Aligned row-to-ML and prediction result adapters with `core/ml`,
  `core/predictor_schema`, and `core/mapping`.
- Preserved existing model artifact and prediction behavior.

### Arc 9.1 — Legacy UI Retirement and ui_common Adoption

Goal:

- Retire the legacy `ui/` path and preserve useful visual/table ideas before
  Predict/Train visual parity work.

Status:

- Complete.

Completed milestones:

- Harvested legacy dropdown, spreadsheet, and visual-token ideas into active
  UI/UX docs.
- Adopted `ui_common.visual_tokens` as the active toolkit-neutral visual token
  owner for Arc 9.5.
- Deleted the legacy `ui/` folder and legacy tests.
- Removed active PyQt dependency wording from active code/docs while preserving
  archive/history.

### Arc 9.5 — Predict / Train Visual UI Parity from Design Assets

Goal:

- Bring the PySide6 Predict and Train surfaces visually closer to the approved
  design reference assets without changing ML, mapping schema, calculator, or
  worker/progress behavior.

Target milestones:

- Apply visual tokens from `ui_common.visual_tokens`.
- Use `docs/designs/assets/predict_ref_img.png` and
  `docs/designs/assets/train_ref_img.png` as non-pixel-perfect layout
  references.
- Improve Predict/Train surface hierarchy, spacing, table visual states, and
  command/status presentation.

### Arc 10 — Prediction Worker/Progress

Goal:

- Move large-batch prediction execution behind approved worker/progress/cancel
  boundaries.

Target milestones:

- Add worker boundary after schema/mapping recovery is stable.
- Add progress/cancel UI behavior without changing core prediction semantics.
- Complete real-model smoke readiness when a valid model artifact is available.

### Arc 11 — Trainer Admin App Foundation

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

### Arc 12 — ML Pipeline Stabilization

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

### Arc 13 — Calculator to Predictor Integration

Goal:

- Prepare predictor outputs for calculator input adapters and later
  ranking/recommendation workflows.

Target milestones:

- Define a predicted-points/result envelope for calculator handoff.
- Expand calculator input adapters only through approved boundaries.
- Calculate seasonal metrics from prediction output in a later approved slice.
- Keep ranking/recommendation preparation separate from Train/Predict UI
  foundation work.

## 5. Deferred / Hold Areas

- AS/NZS Excel compatibility Z-phase remains deferred.
- Internal formula trace remains on hold unless a separate core/data contract is
  approved.
- Broad code-quality refactors belong in `docs/REFACTOR_PLAN.md`, not in this
  brief.
- Packaging and hook-integration work should remain separate workflow arcs
  unless explicitly promoted.
- Arc 9.1 retires the legacy `ui/` folder after harvesting useful UX ideas and
  adopting `ui_common.visual_tokens` for visual parity work.

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
