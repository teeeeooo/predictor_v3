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

- Arc 13 Feature Catalog migration, Arc 13.5/13.5A Feature Catalog Manager,
  Arc 13.5R Predict Schema projection foundation, and Arc 14 Data Mapping
  Manager, runtime cascade, and snapshot export are complete for their
  automated scopes.
- Arc 15 Data Definition foundation automated scope is complete. Data
  Definition is the canonical schema/feature-definition owner; Data Mapping
  Manager owns `mapping.json` values; Feature Catalog Manager is the legacy
  compatibility/read/export surface.
- Arc 15-FU1 — Data Definition Controller State Builder Extraction is complete.
  Controller actions remain unchanged, state composition now belongs to the
  adjacent pure builder, and main merge readiness is maintained.

## Next Actions

Next: Arc 15 main merge execution.

1. Execute the Arc 15 main merge.
2. Start Standard Calculation Capability Extension design.

## Active Blockers / Open Decisions

- Real model prediction success smoke is not complete in this checkout because
  `model/model.pkl` is absent.
- Mock smoke can cover workflow readiness, but it cannot validate prediction
  accuracy, physical trends, feature importance, or production model quality.
- A future explicit DEV/demo sample loader remains optional and is not part of
  the production empty-state contract.
- Schema/column/rule changes use an initial restart-required policy; live schema
  reload remains a future decision.
- `mapping.json` is the SSOT for Refrigerant and Expansion options:
  `ref_type` and `exp_type` are required mapping sections, and Predict dropdown
  hard-coded fallback options have been removed.
- One-hot ML input projection is not yet v2-owned. Arc 14A/14C kept semantic
  mapping fields separate from legacy `mapping`, `source`, and `mapping_key`
  compatibility fields.
- Bundle 2A-F records dependency correction: Train/Predict share
  `requirements/ml_runtime.txt`; Predict includes XGBoost/scikit-learn runtime
  for real `model.pkl` inference while excluding training-only `optuna`; Excel
  policy remains `openpyxl` for generated XLSX write/export and `xlwings` for
  existing user Excel reads in Windows user environments.
- Real training CSV data is not in this checkout; the real training data remains
  on the user's local PC.

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
- After Arc 15, Standard Calculation Capability Extension proceeds in this
  order: BRAZIL core/profile; BRAZIL calculator integration and department
  deployment; AHRI multi-capacity audit/foundation; two-stage SEER2; two-stage
  HSPF2; triple-capacity northern heat-pump HSPF2; AHRI calculator integration
  and department deployment.
- Resume ML Production Readiness as a new Arc after the standard calculation
  capability sequence.
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
- Arc 13.5 Feature Catalog editor design gate:
  `docs/designs/2026-07-01-arc13-5-feature-catalog-editor-design-gate.md`.
- Arc 13.5 revised slice plan:
  `docs/designs/2026-07-02-arc13-5-feature-catalog-editor-revised-slice-plan.md`.
- Arc 13.5R Predict Schema / Mapping Manager foundation:
  `docs/designs/2026-07-03-arc13-5r-predict-schema-mapping-manager-foundation.md`.
- Arc 13.5R projection owner switch:
  `docs/designs/2026-07-03-arc13-5r-projection-owner-switch.md`.
- KOREA calculator notebook entry sub-arc:
  `docs/designs/2026-07-01-korea-notebook-entry-subarc-spec.md`.
- KS C 9306 HSPF official oracle closeout:
  `result_reports/summaries/651_summary-ks-hspf-official-oracle-closeout.md`.
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
