# Project Brief

This document owns the compact Phase / Arc / Milestone map for `predictor_v3`.
It is the first project-state document to read when starting a new session or
resuming work.

It does not own task-specific read pointers, code file pointers, or the exact
next implementation action. Current slice, next action, blockers, constraints,
and explicit handoff pointers belong to `docs/WORK_PLAN.md`.

## 1. Current Phase

Current phase: Machine Learning / Predictor Phase, post-Arc 13 planning. Arc
13 ML Feature Catalog migration is complete for automated scope; Calculator
Sub-Arc - KOREA Notebook Entry is complete; current near-term execution moves
to Arc 13.5 Feature Catalog Editor work.

The calculator UI/workflow stabilization phase is complete enough to resume the
ML / predictor path, and the approved PySide6 Train/Predict foundation now
exists. PySide6 Predictor schema/mapping recovery, legacy `ui` retirement, and
Arc 9.5 unified case table parity correction now have focused automated
coverage and user manual-smoke acceptance.

Arc 9.5 was reopened after user review because spreadsheet baseline items were
deferred and the split input/result table structure did not satisfy the desired
case-row workflow. The accepted closeout targets and reflects the updated local
B-option reference at `docs/designs/assets/predict_ref_img.png`: one unified
case table where one visible row is one prediction case and input,
auto-fill/calculated, prediction result, and status/warning columns are grouped
in the same spreadsheet-like table. A later manual smoke rejected the prior
Arc 9.5 final closeout because structural table, dropdown, Train embedding, and
Trainer table-surface issues remained. The automated correction slices are now
complete, and the user has accepted the corrected manual smoke. Arc 10
Prediction Worker / Progress implementation has since been completed through
worker, controller, progress/cancel UI, resource-status cleanup, and focused
automated coverage. Arc 11 now adds Train execution service/worker/controller/UI
wiring and DEV-only Train E2E smoke. Arc 11 final architecture acceptance is
reopened because Train production execution is not yet behind a killable
outbound process adapter and Predict execution orchestration remains
PySide6/QThread-bound. Calculator boundary correction is real but routed to Arc
12, not mixed into Arc 11. Manual GUI smoke and real-model success smoke remain
pending until the reopened correction slices close.

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
  ownership; Arc 10 added Predict worker/progress/cancel execution boundaries,
  and Arc 11 is reopened to correct Train/Predict application-usecase and
  execution adapter boundaries before manual closeout.
- The current `core/` root is no longer the active implementation surface for
  ML/schema/mapping/calculator owners. Arc 7 moved ML/schema/mapping
  implementation ownership under `core/ml`, `core/predictor_schema`, and
  `core/mapping`; Arc 8 moved calculator implementation ownership under
  `core/calculators`; Arc 8.5 retired root compatibility wrappers and migrated
  active callers to package owner paths.
- Legacy Train/Predict `ui/` files are retired in Arc 9.1; Arc 9.2 preserves
  project-specific visual/table harvest evidence under `docs/designs/`.
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

- Worker/progress/cancel execution moved to Arc 10. Real-model success smoke
  remains pending until a valid model artifact is available.

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

- Harvested legacy dropdown, spreadsheet, and visual-token ideas before
  retiring the legacy path.
- Adopted `ui_common.visual_tokens` as the active toolkit-neutral visual token
  owner for Arc 9.5.
- Deleted the legacy `ui/` folder and legacy tests.
- Removed active PyQt dependency wording from active code/docs while preserving
  archive/history.

### Arc 9.2 — Legacy UI Harvest Location Correction and Detail Recovery

Goal:

- Move project-specific legacy visual/table evidence out of portable UI/UX
  contracts and into design references for Arc 9.5.

Status:

- Complete in the current local arc.

Completed milestones:

- Recovered detailed legacy `ui/` behavior from Git history.
- Moved the PySide6 visual/table parity harvest to
  `docs/designs/2026-06-27-pyside6-visual-table-parity-harvest.md`.
- Kept `docs/ui_ux/` as the portable UI/UX rule set.

### Arc 9.5 — Predict / Train Visual UI Parity from Design Assets

Goal:

- Bring the PySide6 Predict and Train surfaces visually closer to the approved
  design reference assets without changing ML, mapping schema, calculator, or
  worker/progress behavior.

Status:

- Complete / accepted after second-correction automated coverage and user
  manual-smoke acceptance.

Reopen decision:

- The prior Arc 9.5 closeout implemented useful visual foundation work, but it
  deferred grouped undo, Tab/Enter navigation, click/type replace-on-type, and
  mapping-backed per-row dropdown updates.
- Those deferred items are baseline spreadsheet UX requirements and must be
  completed before final Arc 9.5 closeout.
- The split input/result table structure is replaced as the target by a
  unified case table structure based on the updated local
  `docs/designs/assets/predict_ref_img.png`.
- The later final closeout is superseded by manual-smoke findings covering the
  detached group header, non-editable dropdown/autocomplete behavior, duplicated
  Train/Predict status ownership, UI-level mapping option lookup, and Trainer
  `QTableWidget` usage.

Completed milestones:

- Apply visual tokens from `ui_common.visual_tokens`.
- Use `docs/designs/assets/predict_ref_img.png` and
  `docs/designs/assets/train_ref_img.png` as non-pixel-perfect layout
  references.
- Use `docs/designs/2026-06-27-pyside6-visual-table-parity-harvest.md` as the
  Arc 9.5 project-specific acceptance reference.
- Improve Predict/Train surface hierarchy, spacing, table visual states, and
  command/status presentation.
- Add PySide6 style adapter under `apps/common/ui/style.py`.
- Add Predict status strip, command bar, table clipboard basics, dropdown
  affordance, validation/result status rendering, and result summary badge.
- Add Train Model and Data Mapping visual admin panels while keeping execution
  deferred.

Completed correction milestones:

- Update architecture and design acceptance documents for the unified case
  table.
- Add an app-side unified case column adapter without changing core schema.
- Add unified case table model and view.
- Complete spreadsheet UX baseline, including grouped undo, Tab/Enter
  navigation, click/type replace-on-type, and read-only mutation prevention.
- Complete mapping-backed per-row dropdown option updates.
- Integrate result/status columns into the unified table.
- Correct Predict and Trainer visual parity.
- Correct table-linked group header geometry, editable dropdown/autocomplete,
  mapping option boundary, embedded Train/Predict header ownership, Trainer
  model/view table compliance, and workspace row command boundary.
- Manual-smoke correction slices passed automated coverage and were accepted by
  the user, so Arc 9.5 is closed for the current scope.

### Arc 10 — Prediction Worker/Progress

Goal:

- Move large-batch prediction execution behind approved worker/progress/cancel
  boundaries.

Target milestones:

- Add worker boundary after schema/mapping recovery is stable.
- Add progress/cancel UI behavior without changing core prediction semantics.
- Complete real-model smoke readiness when a valid model artifact is available.

Status:

- Implementation complete for automated coverage; awaiting manual smoke and
  real-model success smoke when a valid `model/model.pkl` is available.

Completed milestones:

- Move prediction execution behind worker/progress/cancel boundaries without
  changing core ML behavior.
- Clean up Predict model/mapping resource status ownership through service,
  controller, adapter, or repository boundaries.
- Keep real-model success smoke ready but blocked until a valid
  `model/model.pkl` artifact is available.
- Cover invalid rows, model-missing errors, partial success/error, cancellation,
  row-level cancelled state, running-state mutation guards, and Train shell
  construction with focused automated tests.

### Arc 11 — Predict / Train Hexagonal Boundary Recovery

Goal:

- Correct Predict/Train application-usecase and execution boundaries so future
  UI/runtime replacements can reuse core and application-level logic.
- Fix production Train execution so the visible `중지` button hard-stops the
  running training process.

Target milestones:

- Slice 0 - Architecture acceptance reset.
- Slice 1 - Train execution port + QProcess hard stop.
- Slice 2 - Predict usecase / execution port.
- Slice 3 - Re-closeout / manual smoke gate.

Status:

- Complete for automated closeout scope.
- Train production UI execution runs through an explicit execution port and
  killable process runner adapter; the legacy direct Train worker path is
  removed.
- Predict execution orchestration has a UI/runtime-neutral usecase/port, with
  QThread lifecycle isolated in the PySide runner adapter and PySide runner
  creation owned by the PySide workspace composition layer.
- Calculator boundary issue exists but is moved to Arc 12.

Completed milestones:

- Added Train execution boundary design and architecture contract updates.
- Added Qt-free training service/state contracts.
- Added worker-backed training execution and cooperative cancellation.
- Added TrainController QThread lifecycle orchestration.
- Connected Train / Model UI controls, progress, log, summary, and model status
  refresh to the controller boundary.
- Added DEV-only Train execution smoke and Predict-after-Train smoke.
- Reopened and corrected production Train execution through a killable process
  runner adapter.
- Extracted Predict request/result orchestration into a UI/runtime-neutral
  usecase and execution port.
- Finalized Train/Predict execution boundaries by removing
  `PredictionController`'s concrete PySide runner dependency, deleting the
  legacy direct `TrainWorker`, and reducing `TrainingService` to
  validation/status ownership.
- Re-ran Train/Predict automated smoke gate for closeout.
- Kept Data Mapping update execution deferred.

### Arc 12 — Calculator UseCase Boundary Correction

Goal:

- Extract or define a calculator application-usecase boundary so future
  UI/runtime surfaces and predictor-calculator integration do not copy Tk
  UI-section orchestration.

Target milestones:

- Calculator UI/Application Boundary Audit.
- CalculatorUseCase Target Design.
- First narrow usecase extraction.
- Calculator regression / smoke / closeout.

Status:

- Arc 12 is complete for automated scope.
- ISO/ISEER, SASO T3, Hong Kong CSPF/HSPF, EN14825 SEER/SCOP, and AHRI
  SEER2/HSPF2 now have application boundary treatment or thin UI shims that
  delegate to application-owned adapters/usecases.
- Slice 12 also moves the remaining AHRI dispatcher calls, EN14825 concrete
  calculator creation, and SASO T3 config override concern behind focused
  outbound gateways under `apps/calculator/adapters/`.
- Matching batch paths reuse application usecases/adapters where applicable.
- Arc 13 is unblocked as the next recommended arc.
- Calculator formula/config/golden/public result contracts remain protected.

### Arc 13 — ML Pipeline Stabilization

Goal:

- Stabilize ML feature, leakage, model artifact, preprocessing, and result-key
  contracts after Arc 11 and Arc 12 architecture corrections are complete,
  starting with a minimal ML feature manifest design and validation foundation.

Target milestones:

- Establish a user-managed single-file feature manifest boundary for
  `config/ml/features.csv` without immediately connecting it to runtime.
- Review `MODEL_REGISTRY`, `BASE_FEATURES`, `TARGETS`, and target leakage
  rules.
- Separate user-managed feature contract fields from code-derived UI
  presentation, model policy, derived formulas, and artifact schema.
- Preserve single-artifact and preprocessing compatibility contracts unless a
  later design explicitly changes them.
- Align one-hot option and result-key SSOT ownership.
- Add focused ML tests around feature names, leakage, and prediction/training
  boundary behavior.

Status:

- Complete for automated Arc 13 scope. Slice 0 created the ML Feature Manifest
  Minimal Design Gate. Slice 1
  added the non-runtime catalog draft, loader/validator, and parity tests.
  Slice 2 moved `core/ml/features.py` exports to catalog projection. Slice 2.5
  clarified the `ml_name` training-header contract and split catalog
  responsibilities. Slice 3 moved predictor schema ML-visible columns to
  catalog projection while preserving current UI schema exports. Slice 3.5
  split predictor UI-only compatibility columns into their own schema owner.
  Slice 4 moved Predict one-hot group ownership to catalog projection. Slice 5
  connected training header and inference zero-fill runtime guards. Slice 6
  hardened registry/resource guards and documented the feature edit workflow.
  Slice 7 closed Arc 13 with summary/archive lifecycle cleanup.

### Calculator Sub-Arc — KOREA Notebook Entry

Goal:

- Add the KOREA notebook entry as a bounded calculator sub-arc before resuming
  the ML catalog UI workflow.

Status:

- Complete. KOREA is registered as a top-level calculator notebook tab with
  CSPF/HSPF single calculation, midpoint guide, batch, and detail surfaces.

Scope boundary:

- Preserve calculator formula/config/golden/public result contracts and keep
  the notebook entry separate from Arc 13.5 Train/Admin catalog editor work.

### Arc 13.5 — Feature Catalog Editor Bridge

Goal:

- Move the feature catalog user workflow from direct CSV editing toward an
  `app_train.py` Train/Admin Feature Catalog table editor.

Target milestones:

- Slice 0: Feature Catalog Editor Design Gate.
- Slice 1: read-only catalog viewer with validate and CSV export.
- Slice 2: editable catalog table with save.

Direction:

- `config/ml/features.csv` remains the storage and contract file.
- Direct CSV editing is no longer the default user workflow.
- CSV export remains available for storage, sharing, and Excel/Numbers review.
- UI implementation should route Train UI actions through
  controller/service/usecase boundaries to catalog loader/validator/writer
  ownership rather than making the UI own raw CSV parsing or writing.
- `config/ml/README.md` and workflow document updates are deferred to the Arc
  13.5 implementation slices.

Status:

- Planned bridge arc after the Calculator Sub-Arc and before Arc 14.

### Arc 14 — ML Catalog-Aligned Real Dataset Readiness Audit

Goal:

- Audit real dataset readiness against the Arc 13 catalog contract and Arc 13.5
  editor workflow.

Status:

- Deferred until after Calculator Sub-Arc and Arc 13.5.

### Later — Calculator to Predictor Integration

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
- Arc 9.1/9.2 retired the legacy `ui/` folder, adopted
  `ui_common.visual_tokens`, and moved project-specific harvest evidence under
  `docs/designs/` for visual parity work.

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
