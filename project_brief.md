# Project Brief

This document owns the compact Phase / Arc / Milestone map for `predictor_v3`.
Execution belongs to `docs/WORK_PLAN.md`; history belongs to the log and records.

## Current Phase

Train/Admin UI/UX Overhaul Phase 4 — Train/Model and Shell UX current-state audit
and design finalization is next. Phase 3 — Data Definition UX Overhaul is
complete, final-audit approved, and merged through PR #16. The earlier
ML/Predictor foundation through Arc 15-FU1 and the merged Phase 1–2 Train/Admin
work remain the active owner baseline.

## Current Owner State

- Data Definition is the canonical schema and feature-definition owner.
- Data Mapping Manager owns `mapping.json` values and runtime mapping cascade.
- `core/ml/feature_catalog*` and `config/ml/features.csv` remain the ML
  compatibility contract; the former Feature Catalog Manager UI is retired.
- `config/ml/features.csv` remains the ML feature storage and contract file.
- Train and Predict remain separate PySide6 applications under `apps/train/`
  and `apps/predict/`; the calculator shell and Tkinter path stay separate.
- Canonical calculator launch remains `app_calculator.py` →
  `apps.calculator.app:main`.
- Calculator implementation ownership is under `core/calculators`; calculator
  formulas, profile/config semantics, fixtures/goldens, and public result
  contracts remain protected.
- `core.ml`, `core.predictor_schema`, `core.mapping`, `core.common`, and
  `core.calculators` remain UI-toolkit independent.
- Standard calculation core and standard/region config are calculator-neutral.
  Calculator and ML/Predict reuse their contracts without copying formulas.
- Region config, HW candidate input, ML feature schema, calculator result
  schema, and UI table schema remain separate contracts.

## Milestone Map

### Closed Foundation

- Arc 13 — ML Pipeline Stabilization: complete for automated scope.
- Arc 13.5/13.5A — Feature Catalog Editor/Manager: historical foundation,
  superseded by the Arc 15 Data Definition owner and now retired from the UI.
- Arc 13.5R — Predict Schema projection foundation: complete.
- Arc 14 — Mapping entity, manager UI, runtime cascade, and snapshot export:
  complete for automated scope.
- Arc 15 — Data Definition foundation: complete for automated scope.
- Arc 15-FU1 — controller state-builder extraction: complete, validated, and
  merged into `main` without changing controller behavior.
- Train/Admin UI/UX Overhaul Phase 1 — strict bootstrap, populated mapping
  fixture, dynamic mapping attributes, and aligned mock readiness: complete for
  repository-automated scope and merged before Phase 2.
- Train/Admin UI/UX Overhaul Phase 2 — seven-group Data Mapping information
  architecture, spreadsheet CRUD/Undo, validation and safe persistence, plus
  exchange export/import: merged after repository-automated acceptance; deferred
  native interaction evidence remains separately recorded.
- Train/Admin UI/UX Overhaul Phase 3 — table-first Data Definition inventory,
  controlled Add/Edit, guarded schema Save and impact, saved-only Data Mapping
  handoff/coverage, keyboard/accessibility polish, and bounded native evidence:
  final audit approved and merged through PR #16.

### Closed — Train/Admin Phase 3 Data Definition UX Overhaul

Phase 3 established the table-first Data Definition inventory, controlled Add/Edit,
guarded schema-only Save, impact/blocker workflow, saved-only Data Mapping
handoff, and keyboard/accessibility polish. It is complete and merged through PR
#16. These boundaries remain in force:

- Data Definition owns structure and mapping attribute definitions; Data Mapping
  owns concrete values.
- Existing projection, validation, save, readiness, handoff, and persistence
  owners remain authoritative.
- Unsupported active ML rename/delete and projection-changing writes remain
  blocked until an explicit compatibility owner is approved.
- Predict internal redesign, live schema reload, automatic retraining, and real
  company data remain outside this milestone.

### Next Workstream — Train/Admin Phase 4 Train/Model and Shell UX Overhaul

Phase 4 begins with a current-state audit and design finalization. Its primary
user flow is:

```text
select training data → train → check progress → review results
```

Schema, feature, mapping, and compatibility validation is automatic and internal.
The default surface presents the user's next action and outcome, not normal
technical readiness details. Errors lead with a user-facing explanation and
resolution action; Diagnostics/logs provide the deeper technical context.

Results center on overall success, target-level R², optional MAE/RMSE, Optuna
status with best trial/score when applicable, model-save status, elapsed time, and
Predict availability. Existing Train, ML, persistence, artifact, and public
contracts are preserved.

### Later — Production ML Readiness / Calculator Integration

- Validate production model/data availability, prediction quality, physical
  trends, and feature importance through an explicitly approved workstream.
- Define a predicted-points/result envelope for calculator handoff.
- Expand calculator input adapters only through approved owner boundaries.
- Keep seasonal calculation, ranking, and recommendation work separate from
  Train/Predict UI foundation and from formula ownership.

## Deferred / Hold

- AS/NZS Excel compatibility and historical reconstruction remain deferred.
- Internal formula trace remains on hold unless a separate core/data contract
  is approved.
- Broad refactors remain trigger-based under `docs/REFACTOR_PLAN.md`.
- Packaging, deployment, and hook integration remain separate workstreams
  unless explicitly promoted.

## State Navigation

- Start every task with `AGENTS.md`; use only the matching router/owner route.
- Read `docs/WORK_PLAN.md` for the current slice, one next action, blockers,
  constraints, and explicit handoff pointers.
- Read this brief when phase, owner state, or milestone direction is needed.
- Read `result_reports/memory/project_memory_seed.md` only for relevant prior
  decisions, failures, open questions, or workstream recovery.
- Use the log/records/legacy evidence for history, not to reconstruct priority.
