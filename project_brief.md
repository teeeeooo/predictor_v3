# Project Brief

This document owns the compact Phase / Arc / Milestone map for `predictor_v3`.
Execution belongs to `docs/WORK_PLAN.md`; history belongs to the log and records.

## Current Phase

The ML / Predictor foundation through Arc 15-FU1 is complete and merged into
`main`. Arc 13 stabilized ML features, Arc 13.5/13.5A established
the Feature Catalog Manager, Arc 13.5R established the Predict Schema
projection foundation, Arc 14 completed Data Mapping Manager/runtime cascade/
snapshot export, and Arc 15 plus FU1 completed Data Definition and the
no-behavior-change controller state-builder extraction.

Next is Standard Calculation Capability Extension; afterward, Production ML
Readiness resumes and later connects predictor outputs to calculator adapters.

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

### Next Workstream — Standard Calculation Capability Extension

Boundary: global standard logic belongs in canonical core; country/region
behavior belongs in config, profile, handler, or adapter boundaries. Calculator
integration follows core capability and does not become the formula owner.

Confirmed capability scope:

- BRAZIL: reuse ISO 16358-1 core; own Brazil bins/rules as config/core
  capability; produce 3-point and 2-point comparison results; keep Rule 1,
  Rule 2, and final OK/NG in core.
- AHRI: add two-stage SEER2, two-stage HSPF2, and triple-capacity northern
  heat-pump HSPF2. Triple-capacity cooling SEER2 uses the normal two-stage
  cooling path; product-type resolution belongs to core/application, not UI.

Execution order:

1. BRAZIL core/profile.
2. BRAZIL calculator integration and department deployment.
3. AHRI multi-capacity audit/foundation.
4. Two-stage SEER2, then two-stage HSPF2, then triple-capacity northern
   heat-pump HSPF2.
5. AHRI calculator integration and department deployment.
6. Resume ML as a new Production ML Readiness workstream.

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
