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
- Arc 9 PySide6 Predictor Schema / Mapping Recovery is complete: the Predict
  schema adapter, table models, mapping/autofill flow, row-to-ML adapter, and
  prediction result adapter now use the `core/predictor_schema`, `core/mapping`,
  and `core/ml` package owners directly.
- Architecture SSOT is updated from
  `docs/architecture/project_wide_architecture_restructuring_plan.md`: final
  target package owners are `core/common`, `core/predictor_schema`,
  `core/mapping`, `core/ml`, and `core/calculators`.
- Arc 7 Core ML / Schema / Mapping Package Restructure is complete:
  `core/ml`, `core/predictor_schema`, and `core/mapping` are the package owners
  for ML implementation, predictor schema, and mapping path/repository/update
  logic.
- Arc 8 Calculator Engine Package Restructure is complete:
  `core/calculators`, `core/calculators/adapters`, and
  `core/calculators/standards` are the implementation owners for calculator
  profiles/dispatcher, calculator adapters, standard engines, and calculator
  result/ranking adapters.
- Arc 8.5 Root Wrapper Retirement is complete: active production code and
  tests use package owner paths, and root ML/constants/calculator compatibility
  wrapper files have been deleted.
- Arc 9.1 legacy `ui/` retirement is complete: harvestable UX ideas have been
  documented and `ui_common.visual_tokens` is the active toolkit-neutral token
  owner for upcoming visual parity work.

## Next Actions

1. Arc 9.5 - Predict / Train Visual UI Parity from Design Assets.
2. Arc 10 - Prediction worker/progress and real-model smoke readiness.
3. Arc 11 - Trainer app foundation.

## Active Blockers / Open Decisions

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
- Do not recreate the retired legacy `ui/` Train/Predict path; PySide6
  Predict/Train work belongs under `apps/predict/` and `apps/train/`.
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
