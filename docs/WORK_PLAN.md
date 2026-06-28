# Work Plan

## Purpose

- Maintain the current slice, next action, active blockers/open decisions,
  active constraints, and deferred/hold items.
- Keep Phase / Arc / Milestone direction in `project_brief.md`.
- Keep long-term goals and Phase 1~5 direction in `PROJECT_CHARTER.md`.
- Keep completed work history in `project_log.md`, `result_reports/summaries/`,
  and `result_reports/archive/`.
- Keep refactor candidates and structural triggers in `docs/REFACTOR_PLAN.md`.

## Work Plan Update Rule

- `WORK_PLAN.md` is the near-term execution board, not a roadmap, task log, or
  report index.
- Update only when current slice, next action, execution order, active
  constraints, blockers/open decisions, or hold status changes.
- Do not append completed report lists, full report content, terminal output, or
  repeated next-action history.
- Arc and milestone status belong to `project_brief.md`; only reference them here
  when they directly constrain the current slice.
- Ordinary work plan maintenance does not create or update `Session Handoff`.
  That section exists only when the user explicitly requests a session or
  next-agent handoff, following
  `docs/agent_workflows/DOCUMENT_SYNC_AND_LIFECYCLE.md`.

## Current Slice

- Arc 12 Slice 1 adds the Calculator application boundary foundation:
  application-owned profile resolver and app-side core dispatcher adapter.
- Arc 12 Slice 0 formalized the Calculator UI/Application Boundary Audit.
- Arc 12 first implementation target is the ISO/ISEER 2-point single
  application usecase, followed by matching batch reuse.
- Calculator formulas, configs, fixtures, golden expected values, profile IDs,
  and public result dict contracts are protected throughout Arc 12.
- Arc 11 Reopen / Correction is complete for automated closeout scope.
- Train production UI execution now flows through an explicit execution port and
  killable process runner adapter; the legacy direct Train worker path has been
  removed, and `TrainingService` is validation/status only.
- Predict execution orchestration now has a UI/runtime-neutral usecase/port,
  with QThread lifecycle isolated in the PySide runner adapter and PySide runner
  creation owned by the PySide workspace composition layer.
- Calculator usecase boundary correction is acknowledged and moved to Arc 12.
- Former Arc 12 ML Pipeline Stabilization is now Arc 13 and on hold until Arc
  11 and Arc 12 architecture corrections are complete.
- Arc 9.5 second correction is accepted after focused automated coverage and
  user manual-smoke acceptance.
- The accepted Predict target remains the B-option unified case table from
  `docs/designs/assets/predict_ref_img.png`: one visible row per prediction
  case, with input, auto-fill/calculated, prediction result, and status/warning
  columns grouped in one spreadsheet-like table.
- Arc 10 Prediction Worker / Progress implementation is complete for automated
  coverage and awaiting manual smoke.
- Arc 10 moved batch prediction execution behind worker/progress/cancel
  boundaries, cleaned up Predict model/mapping resource status ownership, and
  kept real-model smoke readiness explicit without changing ML, mapping,
  calculator, or unified table contracts.
- Arc 10.5b/Arc 11 DEV-only isolated mock bundle and smoke runners are
  available to verify Predict E2E, Train shell/status, and Train execution E2E
  without committing generated mock data, mapping, model artifacts, or output.

## Next Actions

1. Arc 12 Slice 2 - ISO/ISEER 2-point UseCase Extraction.

## Active Blockers / Open Decisions

- Real model prediction success smoke is not complete in this checkout because
  `model/model.pkl` is absent.
- Mock smoke can cover workflow readiness, but it cannot validate prediction
  accuracy, physical trends, feature importance, or production model quality.
- Calculator usecase boundary correction is the next architecture correction.
- A future explicit DEV/demo sample loader remains optional and is not part of
  the production empty-state contract.

## Active Constraints

- Do not restore production performance prefills; focused tests own any samples
  needed for calculation and detail regression coverage.
- Preserve `app_calculator.py` → `apps.calculator.app:main` as the canonical
  calculator launch boundary.
- Preserve calculator, schema, config, fixture, golden, and public result
  contracts.
- Keep Train/Predict rewrite separate from the Tkinter calculator path.
- Do not recreate the retired legacy `ui/` Train/Predict path; PySide6
  Predict/Train work belongs under `apps/predict/` and `apps/train/`.
- Use focused verification rather than full pytest by default.

## Deferred / Hold

- AS/NZS Excel compatibility remains in the deferred Z-phase.
- Data Mapping update execution remains deferred and is not part of Arc 11
  Train execution.
- Broad ML / predictor algorithm work remains deferred; follow-up prediction
  execution work must preserve core ML behavior.
- Internal formula trace and broad code-quality refactors remain on hold; their
  candidates belong in `docs/REFACTOR_PLAN.md`.

## Reference Anchors

- Active Arc / Milestone map: `project_brief.md`.
- Last closed EN14825 batch/workflow summary:
  `result_reports/summaries/416_summary-en14825-batch-agent-change-gate-closeout.md`.
- AHRI calculator and supporting UI/workflow closeout:
  `result_reports/summaries/445_summary-ahri-calculator-ui-batch-lifecycle-closeout.md`.
- Calculator helper/batch/detail lifecycle closeout:
  `result_reports/summaries/490_summary-calculator-helper-batch-lifecycle-closeout.md`.
- PySide6 Train/Predict rewrite design gate:
  `docs/designs/2026-06-27-pyside6-train-predict-rewrite-design-gate.md`.
- PySide6 Train/Predict governing architecture contract:
  `docs/architecture/pyside6_train_predict_architecture.md`.
- PySide6 Train/Predict visual/table parity harvest:
  `docs/designs/2026-06-27-pyside6-visual-table-parity-harvest.md`.
- B-option unified case table visual reference:
  `docs/designs/assets/predict_ref_img.png`.
- Spreadsheet table UX baseline:
  `docs/ui_ux/03_SPREADSHEET_TABLE_UX_CONTRACT.md`.
- Input/result surface shaping:
  `docs/ui_ux/05_INPUT_MATRIX_AND_RESULT_SURFACE_RULES.md`.
- UI literal legacy inventory and cleanup plan:
  `docs/designs/2026-06-21-ui-magic-literal-legacy-inventory.md`.
- Calculator sample/default inventory and empty-state policy:
  `docs/designs/2026-06-21-calculator-sample-data-empty-state-policy.md`.
- AHRI implementation contract:
  `docs/designs/2026-06-20-ahri-210-240-ui-batch-design-specification.md`.
- Milestone decisions and detailed completed history belong in `project_log.md`
  and the result-report lifecycle directories.
