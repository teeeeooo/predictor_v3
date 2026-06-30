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

- Arc 13 Slice 3 moved predictor schema ML-visible input/auto/result columns to
  catalog projection while preserving existing `COLUMNS`, `INPUT_COLS`,
  `AUTO_COLS`, `RESULT_COLS`, dropdown-only input columns, and rule-only result
  columns.
- Arc 13 Slice 2.5 clarified the feature catalog contract: `ml_name` is the
  raw training header and internal ML name, alias/header mapping is out of
  scope, and catalog loader/validation/projection responsibilities are split.
- Arc 13 Slice 2 converted `core/ml/features.py` exports to catalog projection
  while preserving `BASE_FEATURES`, `DERIVED_FEATURES`, and stable `TARGETS`
  order. `TARGET_COMPAT_ORDER` was removed after result rows were reordered.
- Arc 13 Slice 1 added the non-runtime feature catalog draft plus
  `core/ml/feature_catalog.py` loader/validator and focused parity tests
  against current constants, predictor schema, registry references, one-hot
  tuples, zero-fill policy, and Train panel target tuple.
- Arc 13 Slice 0 formalized the ML Feature Manifest Minimal Design Gate:
  current feature owners were audited, the single-file
  `config/ml/features.csv` target schema was proposed, and runtime connection
  was explicitly deferred to implementation slices.
- Arc 12 Calculator UI/Application Boundary Correction is complete for
  automated scope.
- ISO/ISEER, SASO T3, Hong Kong CSPF/HSPF, EN14825 SEER/SCOP, and AHRI
  SEER2/HSPF2 now have application boundary treatment for single and matching
  batch paths where applicable.
- Arc 12 Slice 12 hardened remaining calculator outbound construction/config
  concerns behind focused `apps/calculator/adapters/` gateways.
- Arc 12 Slice 13 diagnosed the EN14825 broad selector stall as a Tk
  headless/test-isolation issue around sequential destroyed `Tk()` roots and
  `CalculatorTkApp` withdrawn-root `update()`.
- Arc 12 Slice 14 fixed the EN Tk headless test isolation issue with a
  test-only Tk helper and restored `tests -k "en14825"` completion.
- Arc 13 ML Pipeline Stabilization is active, with the first entry point
  narrowed to ML Feature Manifest SSOT Foundation.
- Arc 12 Slice 3 reused the ISO/ISEER 2-point application usecase from the
  matching batch handler.
- Arc 12 Slice 2 extracted the ISO/ISEER 2-point single calculation
  orchestration into an application usecase.
- Arc 12 Slice 1 added the Calculator application boundary foundation:
  application-owned profile resolver and app-side core dispatcher adapter.
- Arc 12 Slice 0 formalized the Calculator UI/Application Boundary Audit.
- Arc 12 final consistency audit added guards against completed UI/batch
  surfaces importing the core dispatcher or mutating calculator config.
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

1. Arc 13 Slice 4 - One-hot Adapter Projection from Catalog or Training Header
   Runtime Guard.

## Active Blockers / Open Decisions

- Real model prediction success smoke is not complete in this checkout because
  `model/model.pkl` is absent.
- Mock smoke can cover workflow readiness, but it cannot validate prediction
  accuracy, physical trends, feature importance, or production model quality.
- Calculator usecase boundary correction is complete for automated Arc 12
  scope; Slice 12 outbound adapter hardening is complete, and no remaining
  calculator extraction blocker is holding Arc 13.
- EN14825 broad selector completes after Slice 14 test-only Tk isolation.
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
- Broad ML / predictor algorithm work remains deferred; later prediction
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
