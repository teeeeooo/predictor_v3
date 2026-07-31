# Project Brief

This document owns the compact Phase / owner / milestone map for `predictor_v3`.
Near-term execution belongs to `docs/WORK_PLAN.md`; history belongs to
`project_log.md`, its archives, and result records.

## Current Phase

Train/Admin Phase 5 and Predict Findings #1–#7 are complete and merged. The
active product workstream is **Predict input workflow broad overhaul**. Detailed
design and source implementation have not started; the entry gate is a fresh
current-state Predict workspace audit followed by an explicit product/owner
boundary and Lane C Build handoff.

`docs/designs/2026-07-14-future-predict-ui-ux-overhaul-boundary.md` remains an
input to that design work. It does not fix the detailed design or source plan.

## Owner Map

- **Data Definition** is the canonical user-edit owner for Feature structure,
  stable identity, Predict/ML ordering, Derived/One-hot structure,
  Target/registry presentation, validation, impact, and safe publication through
  the versioned structured manifest and immutable generation.
- **Data Mapping** owns concrete `mapping.json` values, mapping attribute CRUD,
  exchange, dirty-draft reconciliation, and the runtime mapping cascade. Concrete
  values do not move into Data Definition.
- **Train** owns explicit training-data selection, training execution,
  run/generation-scoped Candidate creation and analysis, and the validated
  promotion workflow. Definition Save and training success do not automatically
  train or replace Active.
- **Predict** consumes a saved contract generation, Data Mapping values, and a
  compatible loaded model. It preserves generation-bound preprocessing,
  inference, Target/result mapping, execution gating, row isolation,
  cancellation, partial results, reload, Active observation, and no-hot-swap
  behavior.
- **Calculator** owns calculation implementations under `core/calculators` and
  the protected formula, profile/config, fixture/golden, and public result
  contracts. Standard calculation core and region config stay
  calculator-neutral; ML/Predict and Calculator integrate through approved
  contracts without copying or changing formulas.

Standalone and embedded Predict use the same shared workspace behavior. Findings
#1–#7 completed the bounded Predict presentation, reset/running projection,
message semantics, execution gate, runtime group-header synchronization, and
model/Target status repairs without changing the contracts above.

## Contract Boundaries

- Data Definition, Data Mapping, Train, Predict, and Calculator remain distinct
  owners. Region config, HW candidate input, ML feature schema, calculator result
  schema, and UI table schema remain separate contracts.
- `core.ml`, `core.predictor_schema`, `core.mapping`, `core.common`, and
  `core.calculators` remain UI-toolkit independent.
- Train and Predict remain separate PySide6 applications; the calculator shell
  and Tkinter paths stay separate.
- Immutable Definition publication, consumer preflight, runtime cutover,
  training Candidate publication, explicit Active promotion, deployment export,
  and Predict reload remain distinct state transitions.
- Standalone and embedded Predict share the case-table workspace contract.
  Root-level horizontal scrolling remains prohibited; any width solution belongs
  to the table and responsive viewport design.

## Milestone Map

### Closed Foundation

- Arc 13–15 established the ML pipeline, Predict schema projection, mapping
  entity/runtime cascade, and unified Data Definition owner.
- Train/Admin Phases 1–4 established mapping/data foundations, Data Mapping and
  Data Definition workflows, the Unified Feature Manager, immutable generation
  publication, and shared Train/Predict runtime consumption.
- Train/Admin Phase 5 established model lifecycle, Candidate/Active separation,
  training result and analysis, Train/Model UI, deployment export and explicit
  Predict reload, headless experiments, agent-assisted campaigns, and guarded
  final confirmation/retention boundaries.
- Predict Findings #1–#7 are complete. No numbered finding remains active.

Closed foundation retains its owner and behavior contracts; exact audit heads,
validation runs, repair sequences, and merge history belong to the log, archives,
records, and Git.

### Active — Predict Input Workflow Broad Overhaul

The next product milestone is a unified one-row-per-case input workflow that must
be audited before design. Expected audit areas include row operations;
spreadsheet selection/editing; manual, mapping-backed, calculated, result, and
status cell roles; mapping cascade discoverability; issue placement; and
table-owned width, scrolling, frozen identity, and responsive viewport behavior.

Because the shared public case-table behavior crosses several owners, source work
requires a Lane C Build handoff after the Orchestrator fixes detailed scope,
acceptance, preserved behavior, and exclusions.

### Later — Production ML Readiness / Calculator Integration

- Validate production model/data availability, prediction quality, physical
  trends, and feature importance only through an explicitly approved workstream.
- Define a predicted-points/result envelope for Calculator handoff.
- Expand Calculator input adapters only through approved owner boundaries.
- Keep seasonal calculation, ranking, and recommendation work separate from the
  Predict input foundation and protected formula ownership.

## Controlled Operations / Deferred

- Production confirmation/promotion, migration apply, retention/delete apply,
  production data/model mutation, and deployment remain separately authorized
  controlled operations.
- Result graph or Advanced surface, export redesign, Train navigation, lifecycle
  wording redesign, model training workflow, ML feature/schema changes,
  Calculator formula changes, and packaging/deployment are not automatically part
  of the first Predict input overhaul scope.
- AS/NZS Excel compatibility and historical reconstruction remain deferred.
- Internal formula trace remains on hold unless a separate core/data contract is
  approved.
- Broad refactors remain trigger-based under `docs/REFACTOR_PLAN.md`.

## State Navigation

- Start with `AGENTS.md` and the matching router/owner route.
- Read `docs/WORK_PLAN.md` for the active slice, next action, blockers,
  constraints, and holds.
- Read this brief for phase, owner, and milestone direction.
- Read the future Predict boundary before the fresh audit; expand it only after
  current-state evidence and owner decisions exist.
- Search `project_log.md` and its monthly archives by heading for durable history;
  use result records only for pointed evidence.
