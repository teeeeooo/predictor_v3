# Project Brief

This document owns the compact Phase / Arc / Milestone map for `predictor_v3`.
Execution belongs to `docs/WORK_PLAN.md`; history belongs to the log and records.

## Current Phase

Train/Admin Phase 4 — Unified Feature Manager current-state audit and design
finalization is the current workstream. Production implementation has not
started. Phase 3 — Data Definition UX Foundation is complete, final-audit
approved, and merged through PR #16. The earlier
ML/Predictor foundation through Arc 15-FU1 and the merged Phase 1–2 Train/Admin
work remain the active owner baseline.

## Current Owner State

- Data Definition is the canonical user-edit owner for Feature definition. Phase
  4 proposes extending it across Predict/ML Feature structure, Derived/One-hot,
  Target/registry, ordering, validation, impact, and safe related-contract Save.
- Data Mapping Manager owns concrete `mapping.json` values and runtime mapping
  cascade; Phase 4 does not move value editing into Data Definition.
- `core/ml/feature_catalog*` and `config/ml/features.csv` remain the ML
  compatibility contract; the former Feature Catalog Manager UI is retired.
- `config/ml/features.csv` is the current ML contract file and the proposed ML
  compatibility/projection surface, not an independent user-edit owner. Existing
  write guards remain until Phase 4 approves and implements persistence.
- Train owns explicit training-data selection and training execution. Phase 4
  proposes dynamic validated Feature/Target consumption but no automatic
  retraining.
- Predict consumes saved schema/Feature contracts, mapping values, and compatible
  model artifacts; its internal UI redesign remains deferred.
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
- Unsupported active ML rename/delete and projection-changing writes, Remove/
  Reorder, Derived authoring, One-hot group CRUD, Target/registry management, and
  live reload were outside Phase 3 and are owned by the proposed Phase 4.
- Automatic retraining, automatic activation, Predict internal redesign, and real
  company data remain excluded.

### Current Workstream — Train/Admin Phase 4 Unified Feature Manager

Phase 4 begins with a current-state and contract audit. Its final workflow lets a
user manage Predict and ML Feature contracts without directly editing internal
CSV, JSON, Python registry, or projection files:

```text
Unified Data Definition
    → validated Predict/ML/Derived/One-hot/Target candidates
    → all-or-nothing publish
    → Predict, Train, and Data Mapping owner refresh
```

Concrete mapping values remain in Data Mapping. Training remains an explicit
user action in Train. Data Definition does not trigger training or automatic
model activation, and Predict internal redesign is not part of Phase 4. Phase 4A
must finalize one application-wide generation cutover, immutable training-run
snapshots, dirty Mapping draft reconciliation, One-hot source-mode ownership, and
the boundary between Target CRUD and new model-group/model-level policy creation.

### Next Workstream — Train/Admin Phase 5 Train/Model and Shell UX Overhaul

Phase 5 retains this primary user flow:

```text
select training data → train → check progress → review results
```

Schema, Feature, mapping, and compatibility validation is automatic and
internal. The default surface presents the user's next action and outcome, not
normal technical readiness details. Errors lead with a user-facing explanation
and resolution action; Diagnostics/logs provide deeper technical context.

Results center on overall success, target-level R², optional MAE/RMSE, Optuna
status with best trial/score when applicable, model-save status, elapsed time, and
Predict availability. Existing Train, ML, persistence, artifact, and public
contracts plus the Phase 4 dynamic Feature/Target provider are preserved.
Training-start blockers remain limited to authoritative
Train/ML input and execution conditions; existing artifact, restart, mapping, or
Predict state is non-blocking or post-training unless its owner contract says
otherwise.

### Later — Predict UI/UX Overhaul

Predict internal redesign follows Phase 5 and a fresh populated-state audit.

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
