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

- Arc 9.5 is reopened as `Arc 9.5 Reopen -- Unified Case Table Visual /
  Table UX Parity Correction`.
- The previous Arc 9.5 closeout is preserved as implementation history, but it
  is not accepted as final completion by the user.
- The local `docs/designs/assets/predict_ref_img.png` has been replaced by the
  user and is now the B-option unified case table visual reference.
- The split input/result table structure is not accepted as the final Predict
  case-table UX because one visible row must represent one prediction case for
  visible-as-selected copy/paste behavior.
- Arc 9.5 completion requires unified case table visual parity and spreadsheet
  UX baseline completion before Arc 10 starts.
- The following are Arc 9.5 completion blockers, not deferred polish:
  grouped undo; Tab / Shift+Tab / Enter / Shift+Enter navigation;
  click/type replace-on-type; mapping-backed per-row dropdown option updates.

## Next Actions

1. Arc 9.5 Reopen Slice 8 - Unified Result / Status Integration.
2. Arc 9.5 Reopen Slice 9 - Predict Visual Asset Parity Correction.
3. Arc 10 - Prediction worker/progress and real-model smoke readiness after
   Arc 9.5 final acceptance.

## Active Blockers / Open Decisions

- The previous Arc 9.5 closeout recorded incomplete spreadsheet baseline items
  as deferred; user review rejected that as final completion.
- Current code uses split `InputTableView` / `ResultTableView` surfaces; this
  must be corrected to a unified case table before Arc 10.
- The updated local `predict_ref_img.png` is the B-option visual reference for
  the correction arc.
- Split input/result table UX and hidden joined-copy behavior are not accepted
  as final visual/table parity.
- Real model prediction success smoke is not complete in this checkout because
  `model/model.pkl` is absent.
- Worker/progress/cancel UI is not implemented; synchronous prediction
  execution remains the current foundation and stays on hold until Arc 10.
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
- Arc 10 worker/progress/cancel remains on hold until Arc 9.5 final acceptance.
- Arc 11 Trainer execution foundation remains on hold.
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
