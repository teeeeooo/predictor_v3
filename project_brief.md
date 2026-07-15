# Project Brief

This document owns the compact Phase / Arc / Milestone map for `predictor_v3`.
Execution belongs to `docs/WORK_PLAN.md`; history belongs to the log and records.

## Current Phase

Train/Admin UI/UX Overhaul Phase 2 — Data Mapping UX Overhaul is complete for
code and repository-automated acceptance. PR #15 is the Ready-for-review merge
target; native interaction/visual acceptance is deferred under recorded
blockers. Phase 3 — Data Definition UX Overhaul starts only after PR #15 is
merged to `main`, from a separate branch and Draft PR following a current-state
audit. The earlier ML/Predictor foundation through Arc 15-FU1 remains the active
owner baseline.

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
  exchange export/import: complete for code and repository automation; PR #15
  is the merge target and native acceptance remains deferred.

### Next Workstream — Train/Admin Phase 3 Data Definition UX Overhaul

After PR #15 is merged, sync and confirm merged `main`, create a separate Phase
3 branch and Draft PR, then audit current state before confirming Slice 3A.
Phase 3 turns diagnostics-first Data Definition into an intent-driven manager
while preserving these boundaries:

- Data Definition owns structure and mapping attribute definitions; Data
  Mapping owns concrete values.
- Existing projection, validation, save, and readiness owners remain in place.
- Unsupported active ML rename/delete remains blocked.
- Predict internal redesign, live schema reload, automatic retraining, and real
  company data remain outside Phase 3.

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
