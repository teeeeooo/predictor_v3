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

- Calculator closeout is complete with no remaining implementation blocker in
  the recently closed helper/batch/detail/token/manual-smoke scope.
- Train/Predict Arc 4 prediction execution/result mapping foundation is
  implemented: row input conversion, Qt-free prediction service/controller,
  case_id-based result mapping, and PredictWorkspace run-button integration are
  in place without changing core ML behavior.
- ML / Predictor continuation is paused for a project-wide architecture reset:
  the current PySide6 Predictor schema/mapping path is not aligned enough with
  the existing ML pipeline and broader core ownership to continue recovery
  directly.
- Architecture SSOT is updated from
  `docs/architecture/project_wide_architecture_restructuring_plan.md`: final
  target package owners are `core/common`, `core/predictor_schema`,
  `core/mapping`, `core/ml`, and `core/calculators`; compatibility wrappers are
  transitional safety only.
- Legacy PyQt5 `ui/` Train/Predict code remains reference-only until a later
  explicit retirement slice.

## Next Actions

1. Core package boundary foundation planning or implementation slice.
2. ML implementation move.
3. Predictor schema / mapping move.
4. Calculator implementation move.
5. PySide6 Predictor schema/mapping recovery.
6. Prediction worker/progress and real-model smoke readiness.
7. Trainer app foundation.

## Active Blockers / Open Decisions

- Next code work must establish package boundaries without behavior change.
- Compatibility wrappers are transition safety, not final architecture; physical
  implementation moves are later approved migration slices.
- Current PySide6 Predictor schema/mapping path remains blocked until
  `core/predictor_schema`, `core/mapping`, and `core/ml` boundaries are
  introduced and recovery is explicitly approved.
- Real model prediction success smoke is not complete in this checkout because
  `model/model.pkl` is absent.
- Worker/progress/cancel UI is not implemented; synchronous prediction
  execution is foundation-only and should not be treated as final large-batch
  behavior. This follows the architecture reset and schema/mapping recovery.
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
- Do not delete or move legacy PyQt5 `ui/` Train/Predict files without a later
  explicit retirement slice.
- Use focused verification rather than full pytest by default.

## Deferred / Hold

- AS/NZS Excel compatibility remains in the deferred Z-phase.
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
- UI literal legacy inventory and cleanup plan:
  `docs/designs/2026-06-21-ui-magic-literal-legacy-inventory.md`.
- Calculator sample/default inventory and empty-state policy:
  `docs/designs/2026-06-21-calculator-sample-data-empty-state-policy.md`.
- AHRI implementation contract:
  `docs/designs/2026-06-20-ahri-210-240-ui-batch-design-specification.md`.
- Milestone decisions and detailed completed history belong in `project_log.md`
  and the result-report lifecycle directories.
